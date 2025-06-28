import os
import sys
# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import models after initializing db
from backend.models.user import User
from backend.models.course import Course

def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("Creating sample users...")
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='System Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create teacher user
            teacher = User(
                username='teacher',
                email='teacher@example.com',
                full_name='Sample Teacher',
                role='teacher',
                is_active=True
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            
            # Create student user
            student = User(
                username='student',
                email='student@example.com',
                full_name='Sample Student',
                role='student',
                is_active=True
            )
            student.set_password('student123')
            db.session.add(student)
            
            db.session.commit()
            print("Sample users created successfully.")
        else:
            print("Admin user already exists, skipping user creation.")
        
        print("Creating sample courses...")
        # Check if courses exist
        if Course.query.count() == 0:
            # Create sample courses
            course1 = Course(
                name="Python Programming",
                description="Learn Python programming from scratch",
                category="Programming",
                difficulty="beginner",
                teacher_id=2,  # Teacher's ID
                is_public=True
            )
            db.session.add(course1)
            
            course2 = Course(
                name="Machine Learning Basics",
                description="Introduction to machine learning concepts",
                category="Data Science",
                difficulty="intermediate",
                teacher_id=2,  # Teacher's ID
                is_public=True
            )
            db.session.add(course2)
            
            course3 = Course(
                name="Web Development",
                description="Learn HTML, CSS, and JavaScript",
                category="Web",
                difficulty="beginner",
                teacher_id=2,  # Teacher's ID
                is_public=True
            )
            db.session.add(course3)
            
            db.session.commit()
            print("Sample courses created successfully.")
        else:
            print("Courses already exist, skipping course creation.")

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!") 