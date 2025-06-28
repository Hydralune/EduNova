import os
import sys
# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.main import app, db

def init_db():
    """初始化数据库，删除旧数据库并创建新的"""
    with app.app_context():
        # 删除数据库文件
        db_dir = os.path.join(os.path.dirname(__file__), 'database')
        db_path = os.path.join(db_dir, 'eduNova.sqlite')
        if os.path.exists(db_path):
            print(f"删除旧数据库文件: {db_path}")
            os.remove(db_path)
        else:
            print(f"数据库文件不存在: {db_path}")
            # 确保数据库目录存在
            os.makedirs(db_dir, exist_ok=True)
        
        # 创建新的数据库表
        print("创建新的数据库表...")
        db.create_all()
        
        # 初始化示例数据
        from backend.models.user import User
        
        print("创建默认用户...")
        # 创建管理员
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='系统管理员',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # 创建教师
        teacher = User(
            username='teacher',
            email='teacher@example.com',
            full_name='示例教师',
            role='teacher',
            is_active=True
        )
        teacher.set_password('teacher123')
        db.session.add(teacher)
        
        # 创建学生
        student = User(
            username='student',
            email='student@example.com',
            full_name='示例学生',
            role='student',
            is_active=True
        )
        student.set_password('student123')
        db.session.add(student)
        
        db.session.commit()
        print("默认用户创建成功！")
        
        # 创建示例课程
        from backend.models.course import Course
        
        print("创建示例课程...")
        # 创建示例课程
        course1 = Course(
            name="Python编程基础",
            description="学习Python编程的基本概念和语法",
            category="计算机科学",
            difficulty="beginner",
            teacher_id=2,  # 教师ID
            is_public=True
        )
        db.session.add(course1)
        
        course2 = Course(
            name="数据结构与算法",
            description="掌握常见数据结构和算法",
            category="计算机科学",
            difficulty="intermediate",
            teacher_id=2,
            is_public=True
        )
        db.session.add(course2)
        
        course3 = Course(
            name="机器学习入门",
            description="了解机器学习的基本原理和应用",
            category="人工智能",
            difficulty="advanced",
            teacher_id=2,
            is_public=True
        )
        db.session.add(course3)
        
        db.session.commit()
        print("示例课程创建成功！")
        
        print("数据库初始化完成!")

if __name__ == "__main__":
    init_db() 