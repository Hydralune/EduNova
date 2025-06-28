from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.models.user import User, db
from backend.models.config import SystemConfig
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# 添加OPTIONS请求处理
@admin_bp.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@admin_bp.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 特别为/users添加OPTIONS处理
@admin_bp.route('/users', methods=['OPTIONS'])
def users_options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 检查管理员权限的辅助函数
def admin_required():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"error": "管理员权限需要"}), 403
    return None

# 获取所有用户
@admin_bp.route('/users', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_users():
    # 检查权限
    # admin_check = admin_required()
    # if admin_check:
    #     return admin_check
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    search = request.args.get('search')
    
    # 构建查询
    query = User.query
    
    # 应用过滤条件
    if role:
        query = query.filter(User.role == role)
    
    if search:
        query = query.filter(
            (User.username.like(f'%{search}%')) |
            (User.email.like(f'%{search}%')) |
            (User.full_name.like(f'%{search}%'))
        )
    
    # 执行分页查询
    users_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 构建响应
    response = jsonify({
        'users': [user.to_dict() for user in users_pagination.items],
        'total': users_pagination.total,
        'pages': users_pagination.pages,
        'current_page': users_pagination.page
    })
    
    # 添加CORS头
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    return response

# 获取单个用户
@admin_bp.route('/users/<int:user_id>', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_user(user_id):
    # 检查权限
    # admin_check = admin_required()
    # if admin_check:
    #     return admin_check
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    
    return jsonify(user.to_dict()), 200

# 创建用户
@admin_bp.route('/users', methods=['POST'])
# @jwt_required()
def create_user():
    # 检查权限
    # admin_check = admin_required()
    # if admin_check:
    #     return admin_check
    
    data = request.get_json()
    
    # 验证必填字段
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "用户名、邮箱和密码为必填项"}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "用户名已存在"}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "邮箱已存在"}), 409
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name', ''),
        role=data.get('role', 'student')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "用户创建成功",
        "user": user.to_dict()
    }), 201

# 更新用户
@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
# @jwt_required()
def update_user(user_id):
    # 检查权限
    # admin_check = admin_required()
    # if admin_check:
    #     return admin_check
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效的数据"}), 400
    
    # 更新用户信息
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "邮箱已存在"}), 409
        user.email = data['email']
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    if 'role' in data:
        user.role = data['role']
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        "message": "用户更新成功",
        "user": user.to_dict()
    }), 200

# 删除用户
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
# @jwt_required()
def delete_user(user_id):
    # 检查权限
    # admin_check = admin_required()
    # if admin_check:
    #     return admin_check
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    
    # 防止删除自己
    # current_user_id = get_jwt_identity()
    # if user_id == current_user_id:
    #     return jsonify({"error": "不能删除自己的账户"}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "用户删除成功"}), 200

# 系统统计
@admin_bp.route('/stats', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_stats():
    # 检查权限
    # admin_check = admin_required()
    # if admin_check:
    #     return admin_check
    
    # 用户统计
    total_users = User.query.count()
    admin_count = User.query.filter_by(role='admin').count()
    teacher_count = User.query.filter_by(role='teacher').count()
    student_count = User.query.filter_by(role='student').count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # 返回统计数据
    return jsonify({
        "users": {
            "total": total_users,
            "admin_count": admin_count,
            "teacher_count": teacher_count,
            "student_count": student_count,
            "active_users": active_users
        }
    }), 200

# 系统配置
@admin_bp.route('/config', methods=['GET'])
@jwt_required()
def get_config():
    # 获取JWT声明
    claims = get_jwt()
    is_admin = claims.get('role') == 'admin'
    
    # 构建查询
    query = SystemConfig.query
    
    # 非管理员只能查看公开配置
    if not is_admin:
        query = query.filter_by(is_public=True)
    
    configs = query.all()
    
    # 按类别组织配置
    config_by_category = {}
    for config in configs:
        category = config.category
        if category not in config_by_category:
            config_by_category[category] = []
        config_by_category[category].append(config.to_dict())
    
    return jsonify({
        "config": config_by_category
    }), 200

# 更新系统配置
@admin_bp.route('/config', methods=['PUT'])
@jwt_required()
def update_config():
    # 检查权限
    admin_check = admin_required()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效的数据"}), 400
    
    current_user_id = get_jwt_identity()
    updated_configs = []
    
    # 更新配置
    for key, value in data.items():
        if isinstance(value, dict):
            config_value = value.get('value')
            description = value.get('description')
            category = value.get('category', 'general')
            is_public = value.get('is_public', False)
        else:
            config_value = value
            description = None
            category = 'general'
            is_public = False
        
        config = SystemConfig.set_value(
            key=key,
            value=config_value,
            description=description,
            category=category,
            is_public=is_public,
            user_id=current_user_id
        )
        updated_configs.append(config.to_dict())
    
    return jsonify({
        "message": "配置更新成功",
        "updated_configs": updated_configs
    }), 200 