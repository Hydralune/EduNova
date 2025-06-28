from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from backend.models.user import db

class SystemConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), default='general')
    is_public = db.Column(db.Boolean, default=False)  # 是否公开（可被非管理员查看）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __repr__(self):
        return f'<SystemConfig {self.key}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'category': self.category,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_value(cls, key, default=None):
        """获取配置值，如果不存在则返回默认值"""
        config = cls.query.filter_by(key=key).first()
        if config:
            return config.value
        return default
    
    @classmethod
    def set_value(cls, key, value, description=None, category='general', is_public=False, user_id=None):
        """设置配置值，如果不存在则创建"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
            config.updated_at = datetime.utcnow()
            if description:
                config.description = description
            if category:
                config.category = category
            if is_public is not None:
                config.is_public = is_public
            if user_id:
                config.updated_by = user_id
        else:
            config = cls(
                key=key,
                value=value,
                description=description,
                category=category,
                is_public=is_public,
                updated_by=user_id
            )
            db.session.add(config)
        
        db.session.commit()
        return config 