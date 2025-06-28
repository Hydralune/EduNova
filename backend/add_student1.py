import os
import sys
from flask import Flask
from werkzeug.security import generate_password_hash
import datetime

# Set up path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Create Flask app
app = Flask(__name__)

# 确保数据库目录存在
db_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, 'eduNova.sqlite')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import extensions and models after app creation
from backend.extensions import db
from backend.models.user import User

def add_student1():
    with app.app_context():
        # Initialize database
        db.init_app(app)
        
        # Check if student1 already exists
        student1 = User.query.filter_by(username='student1').first()
        if student1:
            print(f"User student1 already exists (ID: {student1.id})")
            return
        
        # Create student1 user
        student1 = User(
            username='student1',
            email='student1@example.com',
            full_name='Student One',
            role='student',
            is_active=True,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        student1.set_password('student123')
        
        # Add to database
        db.session.add(student1)
        db.session.commit()
        
        print(f"Created student1 user with ID: {student1.id}")
        
        # Verify all users
        users = User.query.all()
        print(f"\nAll users in database ({len(users)}):")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {user.role}, Active: {user.is_active}")

if __name__ == "__main__":
    add_student1() 