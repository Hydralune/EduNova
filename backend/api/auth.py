import jwt as pyjwt
import functools
import datetime
from flask import current_app, request, jsonify, Blueprint
from backend.models.user import User
from backend.extensions import db, jwt
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, verify_jwt_in_request
from werkzeug.utils import secure_filename
import os
import time
from werkzeug.security import generate_password_hash, check_password_hash

# 允许的图片文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_token(user_id):
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # 7天过期
    }
    return pyjwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = pyjwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except pyjwt.ExpiredSignatureError:
        return None
    except pyjwt.InvalidTokenError:
        return None

def login_required(f):
    """登录验证装饰器"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 使用Flask-JWT-Extended验证令牌
            verify_jwt_in_request()
            # 获取当前用户ID
            user_id = get_jwt_identity()
            # 获取用户对象
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({'error': '用户不存在或已被禁用'}), 401
            
            # 将用户对象附加到请求
            request.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"认证错误: {str(e)}")
            return jsonify({'error': '认证失败'}), 401
    
    return decorated_function

def role_required(roles):
    """角色验证装饰器"""
    def decorator(f):
        @functools.wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if request.current_user.role not in roles:
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

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    print(f"尝试登录用户: {username}")
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"用户不存在: {username}")
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not user.check_password(password):
        print(f"密码错误: {username}")
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not user.is_active:
        print(f"账户已禁用: {username}")
        return jsonify({"error": "Account is disabled"}), 403
    
    # 创建访问令牌
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            "username": user.username,
            "role": user.role
        },
        expires_delta=datetime.timedelta(hours=24)  # 延长令牌有效期
    )
    
    # 创建刷新令牌
    refresh_token = create_refresh_token(
        identity=user.id,
        expires_delta=datetime.timedelta(days=30)
    )
    
    print(f"用户 {username} 登录成功")
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
            "avatar_url": user.avatar_url,
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

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    """获取或更新用户个人资料"""
    # 获取当前用户ID
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    if request.method == 'GET':
        return jsonify({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "avatar_url": user.avatar_url,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
        })
    
    # 更新个人资料
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '无效的请求数据'}), 400
            
            # 更新用户信息
            if 'email' in data:
                user.email = data['email']
            if 'full_name' in data:
                user.full_name = data['full_name']
            
            db.session.commit()
            
            return jsonify({
                'message': '个人资料更新成功',
                'user': {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "avatar_url": user.avatar_url,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新个人资料时出错: {str(e)}")
            return jsonify({'error': f'更新个人资料时出错: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改当前用户的密码"""
    # 获取当前用户ID
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({"error": "Old password and new password required"}), 400
    
    # 验证旧密码
    if not user.check_password(old_password):
        return jsonify({"error": "Current password is incorrect"}), 401
    
    # 设置新密码
    user.set_password(new_password)
    user.updated_at = datetime.datetime.utcnow()
    
    # 保存更改
    db.session.commit()
    
    return jsonify({"message": "Password changed successfully"}), 200

@auth_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """专门用于上传头像的路由"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            print(f"用户不存在，ID: {user_id}")
            return jsonify({'error': '用户不存在'}), 404
            
        print(f"开始处理用户 {user.username} 的头像上传请求")
        print(f"请求内容类型: {request.content_type}")
        print(f"请求文件: {list(request.files.keys()) if request.files else '无文件'}")
        print(f"请求表单: {list(request.form.keys()) if request.form else '无表单数据'}")
        
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 生成安全的文件名
        timestamp = int(time.time())
        filename = secure_filename(f"avatar_{user.id}_{timestamp}.png")
        file_path = os.path.join(upload_folder, filename)
        
        # 处理文件上传 - 尝试多种方式
        if 'avatar' in request.files:
            # 标准文件上传
            file = request.files['avatar']
            if file.filename == '':
                return jsonify({'error': '未选择文件'}), 400
                
            print(f"接收到文件: {file.filename}, 类型: {file.content_type}")
            file.save(file_path)
            print(f"文件已保存到: {file_path}")
        elif request.data:
            # 尝试从请求体获取二进制数据
            print("从请求体获取数据")
            with open(file_path, 'wb') as f:
                f.write(request.data)
            print(f"数据已保存到: {file_path}")
        elif len(request.files) > 0:
            # 尝试使用第一个可用的文件
            file_key = list(request.files.keys())[0]
            file = request.files[file_key]
            print(f"使用第一个可用文件: {file_key}, 文件名: {file.filename}")
            file.save(file_path)
            print(f"文件已保存到: {file_path}")
        else:
            return jsonify({'error': '未找到头像文件'}), 400
        
        # 更新用户头像URL
        avatar_url = f"/uploads/avatars/{filename}"
        user.avatar_url = avatar_url
        db.session.commit()
        print(f"用户头像URL已更新: {avatar_url}")
        
        return jsonify({
            'message': '头像上传成功',
            'avatar_url': avatar_url
        })
    except Exception as e:
        db.session.rollback()
        print(f"处理头像上传请求时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500

@auth_bp.route('/test-avatar-upload', methods=['POST'])
def test_avatar_upload():
    """测试头像上传功能，不需要JWT验证"""
    print("开始测试头像上传...")
    try:
        # 检查文件是否存在
        print(f"请求文件: {request.files}")
        if 'avatar' not in request.files:
            print("未找到头像文件")
            return jsonify({'error': '未找到头像文件'}), 400
        
        file = request.files['avatar']
        print(f"接收到文件: {file.filename}, 类型: {file.content_type}")
        
        # 检查文件名
        if file.filename == '':
            print("未选择文件")
            return jsonify({'error': '未选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            print(f"不允许的文件类型: {file.filename}")
            return jsonify({'error': '只允许上传图片文件 (png, jpg, jpeg, gif)'}), 400
        
        try:
            # 确保上传目录存在
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'test')
            os.makedirs(upload_folder, exist_ok=True)
            print(f"上传目录: {upload_folder}")
            
            # 生成安全的文件名
            filename = secure_filename(f"test_avatar_{int(time.time())}.png")
            file_path = os.path.join(upload_folder, filename)
            
            # 保存文件
            print(f"保存文件到: {file_path}")
            file.save(file_path)
            
            return jsonify({
                'message': '测试头像上传成功',
                'avatar_url': f"/uploads/test/{filename}"
            })
        except Exception as e:
            print(f"测试头像上传失败: {str(e)}")
            return jsonify({'error': f'测试头像上传失败: {str(e)}'}), 500
    except Exception as e:
        print(f"处理测试头像上传请求时出错: {str(e)}")
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500

