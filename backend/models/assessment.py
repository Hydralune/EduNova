from backend.extensions import db
from datetime import datetime
import json

class Assessment(db.Model):
    """评估模型，用于存储测验、考试等评估内容"""
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    type = db.Column(db.String(50), default='quiz')  # quiz, exam, assignment
    total_score = db.Column(db.Float, default=100.0)
    questions = db.Column(db.Text, nullable=False, default='[]')  # JSON格式存储题目或题目列表
    duration = db.Column(db.Integer, nullable=True)  # 以分钟为单位
    due_date = db.Column(db.DateTime, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    max_attempts = db.Column(db.Integer, default=1)
    is_published = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    course = db.relationship('Course', backref=db.backref('assessments', lazy=True))
    student_answers = db.relationship('StudentAnswer', backref='assessment', lazy=True)
    creator = db.relationship('User', backref=db.backref('created_assessments', lazy=True))

    def __repr__(self):
        return f'<Assessment {self.title}>'

    def to_dict(self):
        """将模型转换为字典"""
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'course_id': self.course_id,
            'type': self.type,
            'total_score': self.total_score,
            'duration': self.duration,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'max_attempts': self.max_attempts,
            'is_published': self.is_published,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        # 安全处理created_by字段（可能不存在于旧数据库中）
        try:
            result['created_by'] = self.created_by
        except:
            result['created_by'] = None
        
        # 解析JSON格式的题目
        result['questions'] = self.get_questions()
        
        return result
    
    def get_questions(self):
        """获取题目列表，处理不同的存储格式"""
        if not self.questions:
            return []
            
        try:
            # 尝试解析为JSON
            if isinstance(self.questions, str):
                # 如果是字符串，尝试解析为JSON
                return json.loads(self.questions)
            elif isinstance(self.questions, list):
                # 如果已经是列表，直接返回解析后的题目列表
                questions_list = []
                for q in self.questions:
                    if isinstance(q, str):
                        try:
                            questions_list.append(json.loads(q))
                        except:
                            questions_list.append(q)
                    else:
                        questions_list.append(q)
                return questions_list
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing questions: {e}")
            return []
        
        return []


class StudentAnswer(db.Model):
    """学生答案模型，用于存储学生对评估的回答"""
    __tablename__ = 'student_answers'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON格式存储答案
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    question_scores = db.Column(db.Text, nullable=True)  # JSON格式存储每道题的得分
    question_feedback = db.Column(db.Text, nullable=True)  # JSON格式存储每道题的反馈
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime, nullable=True)
    graded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # 关联关系
    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('submissions', lazy=True))
    grader = db.relationship('User', foreign_keys=[graded_by], backref=db.backref('graded_submissions', lazy=True))

    def __repr__(self):
        return f'<StudentAnswer {self.id} by student {self.student_id}>'

    def to_dict(self):
        """将模型转换为字典"""
        result = {
            'id': self.id,
            'student_id': self.student_id,
            'assessment_id': self.assessment_id,
            'score': self.score,
            'feedback': self.feedback,
            'submitted_at': self.submitted_at.isoformat(),
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'graded_by': self.graded_by
        }
        
        # 解析JSON格式的答案
        try:
            result['answers'] = json.loads(self.answers)
        except (json.JSONDecodeError, TypeError):
            result['answers'] = {}
        
        # 解析JSON格式的题目评分
        try:
            if self.question_scores:
                result['question_scores'] = json.loads(self.question_scores)
        except (json.JSONDecodeError, TypeError):
            result['question_scores'] = []
        
        # 解析JSON格式的题目反馈
        try:
            if self.question_feedback:
                result['question_feedback'] = json.loads(self.question_feedback)
        except (json.JSONDecodeError, TypeError):
            result['question_feedback'] = []
        
        return result


class AssessmentSubmission(db.Model):
    """评估提交模型，用于存储学生提交的完整评估（包括所有题目的答案）"""
    __tablename__ = 'assessment_submissions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  # JSON格式存储完整提交内容
    total_score = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), default='submitted')  # submitted, grading, completed
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # 关联关系
    student = db.relationship('User', backref=db.backref('assessment_submissions', lazy=True))
    assessment = db.relationship('Assessment', backref=db.backref('submissions', lazy=True))

    def __repr__(self):
        return f'<AssessmentSubmission {self.id} by student {self.student_id}>'

    def to_dict(self):
        """将模型转换为字典"""
        result = {
            'id': self.id,
            'student_id': self.student_id,
            'assessment_id': self.assessment_id,
            'total_score': self.total_score,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        # 解析JSON格式的提交内容
        try:
            result['content'] = json.loads(self.content)
        except (json.JSONDecodeError, TypeError):
            result['content'] = {}
        
        return result
