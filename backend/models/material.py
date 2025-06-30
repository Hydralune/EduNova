from backend.extensions import db
from datetime import datetime

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    material_type = db.Column(db.String(50), default='text')  # text, pdf, video, link
    file_path = db.Column(db.String(255), nullable=True)
    file_hash = db.Column(db.String(64), nullable=True)  # SHA256哈希值，用于检测重复文件
    external_url = db.Column(db.String(255), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    order = db.Column(db.Integer, default=0)
    
    # Add relationship
    course = db.relationship('Course')
    
    def __repr__(self):
        return f'<Material {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'material_type': self.material_type,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'external_url': self.external_url,
            'course_id': self.course_id,
            'course_name': self.course.name if self.course else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'order': self.order
        }

