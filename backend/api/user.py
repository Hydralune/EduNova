from flask import Blueprint, request, jsonify
from backend.models.user import User
from backend.extensions import db
from backend.utils.auth import generate_token, login_required, admin_required
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    if not user.is_active:
        return jsonify({'error': '账户已被禁用'}), 401
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 生成令牌
    token = generate_token(user.id)
    
    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': user.to_dict()
    })

@user_bp.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供注册信息'}), 400
    
    required_fields = ['username', 'email', 'password', 'full_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 不能为空'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data['full_name'],
        role=data.get('role', 'student')  # 默认为学生角色
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '注册失败，请稍后重试'}), 500

@user_bp.route('/auth/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户信息"""
    return jsonify({
        'user': request.current_user.to_dict()
    })

@user_bp.route('/auth/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户信息"""
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供更新信息'}), 400
    
    user = request.current_user
    
    # 更新允许的字段
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        # 检查邮箱是否已被其他用户使用
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': '邮箱已被其他用户使用'}), 400
        user.email = data['email']
    
    try:
        db.session.commit()
        return jsonify({
            'message': '信息更新成功',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新失败，请稍后重试'}), 500

@user_bp.route('/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    data = request.get_json()
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': '请提供旧密码和新密码'}), 400
    
    user = request.current_user
    
    if not user.check_password(data['old_password']):
        return jsonify({'error': '旧密码错误'}), 400
    
    user.set_password(data['new_password'])
    
    try:
        db.session.commit()
        return jsonify({'message': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '密码修改失败，请稍后重试'}), 500

@user_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """获取用户列表（管理员）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    
    query = User.query
    if role:
        query = query.filter_by(role=role)
    
    users = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    })

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """更新用户信息（管理员）"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '请提供更新信息'}), 400
    
    # 更新允许的字段
    if 'role' in data:
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    try:
        db.session.commit()
        return jsonify({
            'message': '用户信息更新成功',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新失败，请稍后重试'}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户（管理员）"""
    user = User.query.get_or_404(user_id)
    
    # 不能删除自己
    if user.id == request.current_user.id:
        return jsonify({'error': '不能删除自己的账户'}), 400
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': '用户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除失败，请稍后重试'}), 500 