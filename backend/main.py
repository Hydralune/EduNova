import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 禁用 ChromaDB telemetry 以防止崩溃
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

from flask import Flask, jsonify, request, make_response, send_from_directory
from backend.extensions import db, jwt, cors, migrate
from flask_cors import CORS

# 检测是否在PyInstaller环境中运行
def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和PyInstaller打包后的环境 """
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        # 这是PyInstaller特有的属性，不是标准sys模块的一部分
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        # 不在PyInstaller环境中，使用正常的路径
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Initialize Flask app
app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# 确保数据库目录存在
db_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, 'eduNova.sqlite')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 文件上传配置
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 限制上传文件大小为200MB

# JWT配置 - 使用与SECRET_KEY相同的密钥以确保一致性
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 令牌过期时间1小时
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # 刷新令牌过期时间7天

# Initialize extensions with app
db.init_app(app)
jwt.init_app(app)
migrate.init_app(app, db)

# 配置CORS，特别允许前端域名访问
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    "supports_credentials": True,
    "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "expose_headers": ["Content-Type", "Authorization"],
    "max_age": 3600
}})

# 全局OPTIONS处理
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = make_response()
    # 获取来源
    origin = request.headers.get('Origin', '')
    # 特别允许前端域名
    if origin in ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

# Create upload directory
uploads_folder = os.path.join(app.root_path, 'uploads')
os.makedirs(uploads_folder, exist_ok=True)
# 创建头像上传目录
avatars_folder = os.path.join(uploads_folder, 'avatars')
os.makedirs(avatars_folder, exist_ok=True)

# Import models - Fix import order to prevent circular imports
from backend.models.user import User
from backend.models.course import Course
from backend.models.learning import LearningRecord, ChatHistory
from backend.models.material import Material
from backend.models.assessment import Assessment, StudentAnswer, AssessmentSubmission
from backend.models.config import Config

# Import and register blueprints
from backend.api.user import user_bp
from backend.api.admin import admin_bp
from backend.api.learning import learning_bp
from backend.api.rag_ai import rag_api
from backend.api.auth import auth_bp
from backend.api.student_quiz import student_quiz_bp

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(learning_bp, url_prefix='/api')
app.register_blueprint(rag_api, url_prefix='/api/rag')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_quiz_bp, url_prefix='/api')

# 配置前端静态文件路由
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # 检查是否在PyInstaller环境中
    frontend_path = resource_path('frontend/dist')
    
    # 如果请求的是API路由，不处理
    if path.startswith('api/'):
        return jsonify({"error": "Not Found"}), 404
    
    # 如果路径为空或不存在，返回index.html
    if path == '' or not os.path.exists(os.path.join(frontend_path, path)):
        return send_from_directory(frontend_path, 'index.html')
    
    # 返回请求的静态文件
    return send_from_directory(frontend_path, path)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': '教育管理系统后端运行正常'})

# Create database tables and initialize with sample data
def create_tables():
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 如果没有管理员账户，创建默认用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
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
        
        # 如果没有课程，创建示例课程
        if Course.query.count() == 0:
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

# 配置静态文件路由
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    print(f"请求上传文件: {filename}")
    
    # 检查文件是否存在
    file_path = os.path.join(app.root_path, 'uploads', filename)
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return jsonify({"error": f"File not found: {filename}"}), 404
    
    # 获取文件扩展名
    _, ext = os.path.splitext(filename)
    
    # 处理Markdown文件
    if ext.lower() == '.md':
        print(f"检测到Markdown文件: {filename}")
        return send_from_directory(
            os.path.dirname(os.path.join(app.root_path, 'uploads', filename)),
            os.path.basename(filename),
            mimetype='text/markdown'
        )
    
    return send_from_directory(os.path.join(app.root_path, 'uploads'), filename)

# 配置头像访问路由
@app.route('/uploads/avatars/<path:filename>')
def avatar_file(filename):
    print(f"请求头像文件: {filename}")
    try:
        return send_from_directory(os.path.join(app.root_path, 'uploads', 'avatars'), filename)
    except Exception as e:
        print(f"访问头像文件失败: {str(e)}")
        return jsonify({"error": f"Failed to access avatar: {str(e)}"}), 404

if __name__ == '__main__':
    create_tables()
    # 打印所有注册的路由，方便排查 404 问题
    print('==== 所有注册的路由 ====')
    for rule in app.url_map.iter_rules():
        print(rule)
    print('=======================')
    app.run(host='0.0.0.0', port=5001, debug=False)

