from backend.extensions import db
from datetime import datetime

class LearningRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # login, view_material, submit_answer, ask_question
    activity_detail = db.Column(db.Text, nullable=True)  # 活动详情（JSON格式）
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, nullable=True)  # 活动持续时间（秒）
    
    # Use string references for relationships to avoid circular imports
    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('learning_records', lazy='dynamic'))
    course = db.relationship('Course', foreign_keys=[course_id], lazy='joined')
    
    def __repr__(self):
        return f'<LearningRecord {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'course_id': self.course_id,
            'course_name': self.course.name if self.course else None,
            'activity_type': self.activity_type,
            'activity_detail': self.activity_detail,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'duration': self.duration
        }

class ChatHistory(db.Model):
    """学生与AI助手的对话历史"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Use string references for relationships
    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('chat_history', lazy='dynamic'))
    course = db.relationship('Course', foreign_keys=[course_id], lazy='joined')

    def __repr__(self):
        return f'<ChatHistory {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'course_id': self.course_id,
            'course_name': self.course.name if self.course else None,
            'question': self.question,
            'answer': self.answer,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        } 