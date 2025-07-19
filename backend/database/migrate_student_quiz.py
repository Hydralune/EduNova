import os
import sys
# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Flask
from backend.extensions import db
from backend.models.user import User
from backend.models.course import Course
from backend.models.student_quiz import StudentAIQuiz

# 创建一个简单的 Flask 应用
app = Flask(__name__)
db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, 'eduNova.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate():
    """执行数据库迁移"""
    with app.app_context():
        # 检查 student_ai_quizzes 表是否存在
        inspector = db.inspect(db.engine)
        if 'student_ai_quizzes' not in inspector.get_table_names():
            print("创建 student_ai_quizzes 表...")
            # 创建表
            StudentAIQuiz.__table__.create(db.engine)
            print("student_ai_quizzes 表创建成功！")
        else:
            print("student_ai_quizzes 表已存在")

if __name__ == '__main__':
    migrate()
    print("数据库迁移完成") 