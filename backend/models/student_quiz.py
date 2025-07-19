from backend.models.user import db
from datetime import datetime
import json

class StudentAIQuiz(db.Model):
    """学生AI自测测验模型"""
    __tablename__ = 'student_ai_quizzes'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='generating')  # generating, in_progress, completed, abandoned
    config = db.Column(db.Text, nullable=True)  # JSON with quiz configuration
    questions = db.Column(db.Text, nullable=True)  # JSON with questions (updated as generated)
    answers = db.Column(db.Text, nullable=True)  # JSON with student answers
    question_scores = db.Column(db.Text, nullable=True)  # JSON with scores for each question
    question_feedback = db.Column(db.Text, nullable=True)  # JSON with feedback for each question
    score = db.Column(db.Float, nullable=True)  # Overall score
    feedback = db.Column(db.Text, nullable=True)  # Overall feedback
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # 关联关系
    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('ai_quizzes', lazy=True))
    course = db.relationship('Course', backref=db.backref('ai_quizzes', lazy=True))

    def __repr__(self):
        return f'<StudentAIQuiz {self.id} by student {self.student_id}>'

    def to_dict(self):
        """将模型转换为字典"""
        result = {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'score': self.score,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        # 解析JSON格式的字段
        try:
            if self.config:
                result['config'] = json.loads(self.config)
            if self.questions:
                result['questions'] = json.loads(self.questions)
            if self.answers:
                result['answers'] = json.loads(self.answers)
            if self.question_scores:
                result['question_scores'] = json.loads(self.question_scores)
            if self.question_feedback:
                result['question_feedback'] = json.loads(self.question_feedback)
        except (json.JSONDecodeError, TypeError) as e:
            # 如果解析失败，保留原始字符串
            pass
            
        return result 