from datetime import datetime
from backend.extensions import db
from backend.models.user import User

# 课程与学生的多对多关系表
course_students = db.Table(
    'course_students',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    difficulty = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    duration = db.Column(db.Integer, default=0)  # 课程时长（小时）
    is_public = db.Column(db.Boolean, default=True)
    cover_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联教师（一对多）
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', backref=db.backref('courses_teaching', lazy='dynamic'))
    
    # 关联学生（多对多）
    students = db.relationship('User', secondary=course_students, 
                              lazy='subquery', 
                              backref=db.backref('courses_enrolled', lazy=True))
    
    def __repr__(self):
        return f'<Course {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'duration': self.duration,
            'is_public': self.is_public,
            'cover_image': self.cover_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.username if self.teacher else None,
            'student_count': len(self.students) if self.students else 0
        }
    
    def to_dict_with_details(self):
        data = self.to_dict()
        data['students'] = [student.to_dict() for student in self.students] if self.students else []
        return data

