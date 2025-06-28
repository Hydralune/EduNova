#!/usr/bin/env python3
import os
import sys
import datetime

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 30 * 24 * 3600

# 启用CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# 初始化SQLAlchemy
db = SQLAlchemy(app)
jwt = JWTManager(app)

# 创建数据库目录
db_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_dir, exist_ok=True)

# 定义User模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), default='student')  # admin, teacher, student
    avatar = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

# 认证路由
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403
    
    # 创建访问令牌
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            "username": user.username,
            "role": user.role
        },
        expires_delta=datetime.timedelta(hours=1)
    )
    
    # 创建刷新令牌
    refresh_token = create_refresh_token(
        identity=user.id,
        expires_delta=datetime.timedelta(days=30)
    )
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name
        }
    }), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not username or not email or not password:
        return jsonify({"error": "Username, email and password required"}), 400
    
    # 检查用户名或邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409
    
    # 创建新用户
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        role='student'  # 默认为学生角色
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }), 201

# 用户路由
@app.route('/api/users/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200

# 健康检查路由
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "API server is running"}), 200

# Import and register learning blueprint
from api.learning import learning_bp
app.register_blueprint(learning_bp)  # url_prefix already defined in blueprint

# 初始化数据库和创建默认用户的函数
def create_tables_and_users():
    # 确保database目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 创建数据库表
    db.create_all()
    
    # 如果没有管理员账户，创建默认管理员
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='System Admin',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # 创建教师和学生账户
        teacher = User(
            username='teacher1',
            email='teacher1@example.com',
            full_name='Teacher One',
            role='teacher'
        )
        teacher.set_password('teacher123')
        db.session.add(teacher)
        
        student = User(
            username='student1',
            email='student1@example.com',
            full_name='Student One',
            role='student'
        )
        student.set_password('student123')
        db.session.add(student)
        
        db.session.commit()
        print("已创建默认用户")

if __name__ == '__main__':
    # 在启动应用前创建表和默认用户
    with app.app_context():
        # 确保database目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 创建数据库表
        db.create_all()
        
        # 如果没有管理员账户，创建默认管理员
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='System Admin',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # 创建教师和学生账户
            teacher = User(
                username='teacher1',
                email='teacher1@example.com',
                full_name='Teacher One',
                role='teacher'
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            
            student = User(
                username='student1',
                email='student1@example.com',
                full_name='Student One',
                role='student'
            )
            student.set_password('student123')
            db.session.add(student)
            
            db.session.commit()
            print("已创建默认用户")
    
    print("服务器启动中，访问 http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
