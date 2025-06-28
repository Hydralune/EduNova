from backend.extensions import db
from datetime import datetime
import json

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    questions = db.Column(db.Text, nullable=False)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关联关系 - 移除backref以避免冲突
    course = db.relationship("Course")
    
    def __repr__(self):
        return f"<Assessment {self.title}>"
    
    def get_questions(self):
        try:
            return json.loads(self.questions)
        except:
            return []
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "course_id": self.course_id,
            "course_name": self.course.name if self.course else None,
            "questions": self.get_questions(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_active": self.is_active
        }

class StudentAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessment.id"), nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON format
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime, nullable=True)
    
    # 关联关系
    student = db.relationship("User", backref="answers")
    assessment = db.relationship("Assessment", backref="student_answers")
    
    def __repr__(self):
        return f"<StudentAnswer {self.id}>"
    
    def get_answers(self):
        try:
            return json.loads(self.answers)
        except:
            return []
    
    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.full_name if self.student else None,
            "assessment_id": self.assessment_id,
            "assessment_title": self.assessment.title if self.assessment else None,
            "answers": self.get_answers(),
            "score": self.score,
            "feedback": self.feedback,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "graded_at": self.graded_at.isoformat() if self.graded_at else None
        }
