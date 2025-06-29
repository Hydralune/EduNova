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
    questions = db.Column(db.Text, nullable=False)  # JSON格式存储题目
    duration = db.Column(db.String(50), nullable=True)  # 如 "30分钟", "2小时"
    due_date = db.Column(db.DateTime, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    max_attempts = db.Column(db.Integer, default=1)
    is_published = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    course = db.relationship('Course', backref=db.backref('assessments', lazy=True))
    student_answers = db.relationship('StudentAnswer', backref='assessment', lazy=True)

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
        
        # 解析JSON格式的题目
        try:
            result['questions'] = json.loads(self.questions)
        except (json.JSONDecodeError, TypeError):
            result['questions'] = []
        
        return result


class StudentAnswer(db.Model):
    """学生答案模型，用于存储学生对评估的回答"""
    __tablename__ = 'student_answers'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON格式存储答案
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
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
