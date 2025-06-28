import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from datetime import datetime, timedelta
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdf#FGSgvasgf$5$WGT'

def generate_token(user_id):
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

def login_required(f):
    """验证用户是否已登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从Authorization头获取令牌
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': '未提供令牌或令牌无效'}), 401
        
        # 解码令牌
        payload = decode_token(token)
        if 'error' in payload:
            return jsonify({'error': payload['error']}), 401
        
        # 获取用户信息
        from backend.models.user import User
        user = User.query.get(payload['user_id'])
        
        if not user:
            return jsonify({'error': '用户不存在'}), 401
        
        if not user.is_active:
            return jsonify({'error': '账户已被禁用'}), 401
        
        # 将用户对象存储到请求上下文中
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """验证用户是否为管理员的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从Authorization头获取令牌
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': '未提供令牌或令牌无效'}), 401
        
        # 解码令牌
        payload = decode_token(token)
        if 'error' in payload:
            return jsonify({'error': payload['error']}), 401
        
        # 获取用户信息
        from backend.models.user import User
        user = User.query.get(payload['user_id'])
        
        if not user:
            return jsonify({'error': '用户不存在'}), 401
        
        if not user.is_active:
            return jsonify({'error': '账户已被禁用'}), 401
        
        if user.role != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        
        # 将用户对象存储到请求上下文中
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def teacher_required(f):
    """验证用户是否为教师或管理员的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从Authorization头获取令牌
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': '未提供令牌或令牌无效'}), 401
        
        # 解码令牌
        payload = decode_token(token)
        if 'error' in payload:
            return jsonify({'error': payload['error']}), 401
        
        # 获取用户信息
        from backend.models.user import User
        user = User.query.get(payload['user_id'])
        
        if not user:
            return jsonify({'error': '用户不存在'}), 401
        
        if not user.is_active:
            return jsonify({'error': '账户已被禁用'}), 401
        
        if user.role not in ['teacher', 'admin']:
            return jsonify({'error': '需要教师或管理员权限'}), 403
        
        # 将用户对象存储到请求上下文中
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function 