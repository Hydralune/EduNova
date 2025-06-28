import functools
import datetime
from flask import current_app, request, jsonify, Blueprint
from backend.models.user import User
from backend.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt

auth_bp = Blueprint('auth', __name__)

def role_required(roles):
    """角色验证装饰器"""
    def decorator(f):
        @functools.wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            role = claims.get('role')
            if role not in roles:
                return jsonify({'error': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """管理员权限装饰器"""
    return role_required(['admin'])(f)

def teacher_required(f):
    """教师权限装饰器"""
    return role_required(['admin', 'teacher'])(f)

@auth_bp.route('/login', methods=['POST'])
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
        identity=str(user.id),
        additional_claims={
            "username": user.username,
            "role": user.role
        },
        expires_delta=datetime.timedelta(hours=1)
    )
    
    # 创建刷新令牌
    refresh_token = create_refresh_token(
        identity=str(user.id),
        expires_delta=datetime.timedelta(days=30)
    )
    
    return jsonify({
        "message": "登录成功",
        "token": access_token,  # Changed from access_token to token to match frontend expectation
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "avatar": user.avatar,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
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

