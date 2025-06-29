import jwt as pyjwt
import functools
import datetime
from flask import current_app, request, jsonify, Blueprint, make_response
from backend.models.user import User
from backend.extensions import db, jwt
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, verify_jwt_in_request, get_jwt
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

# 角色验证装饰器 - 使用Flask-JWT-Extended
def role_required(roles):
    """角色验证装饰器 - 使用Flask-JWT-Extended"""
    def wrapper(fn):
        @functools.wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            # 获取当前用户ID
            user_id = get_jwt_identity()
            # 获取JWT声明
            claims = get_jwt()
            # 获取用户角色
            user_role = claims.get('role')
            
            # 检查角色权限
            if user_role not in roles:
                return jsonify({'error': '权限不足'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

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
    try:
        # 添加用户信息到JWT声明
        additional_claims = {
            "username": user.username,
            "role": user.role,
            "email": user.email
        }
        
        print(f"为用户 {username} 创建令牌，声明: {additional_claims}")
        
        # 确保用户ID是字符串类型
        user_id_str = str(user.id)
        
        access_token = create_access_token(
            identity=user_id_str,  # 使用字符串类型的用户ID
            additional_claims=additional_claims,
            expires_delta=datetime.timedelta(days=1)  # 延长令牌有效期到1天
        )
        
        # 创建刷新令牌
        refresh_token = create_refresh_token(
            identity=user_id_str,  # 使用字符串类型的用户ID
            expires_delta=datetime.timedelta(days=30)
        )
        
        print(f"用户 {username} 登录成功，令牌已创建")
        
        # 返回用户信息和令牌
        return jsonify({
            "message": "登录成功",
            "token": access_token,
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
    except Exception as e:
        print(f"创建令牌时出错: {str(e)}")
        return jsonify({"error": f"Authentication error: {str(e)}"}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    role = data.get('role', 'student')  # 从请求数据中获取角色，默认为student
    
    if not username or not email or not password:
        return jsonify({"error": "Username, email and password required"}), 400
    
    # 检查用户名或邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409
    
    # 验证角色是否有效
    if role not in ['student', 'teacher']:
        return jsonify({"error": "Invalid role"}), 400
    
    # 创建新用户
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role  # 使用请求中指定的角色
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

@auth_bp.route('/profile', methods=['OPTIONS'])
def profile_options():
    response = make_response()
    origin = request.headers.get('Origin', '')
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    """获取或更新用户个人资料"""
    try:
        # 获取当前用户ID
        user_id_str = get_jwt_identity()
        print(f"获取用户资料，用户ID字符串: {user_id_str}, 类型: {type(user_id_str)}")
        
        # 将字符串ID转换为整数
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            print(f"无法将用户ID转换为整数: {user_id_str}")
            return jsonify({'error': '无效的用户ID'}), 400
        
        user = User.query.get(user_id)
        if not user:
            print(f"用户不存在，ID: {user_id}")
            return jsonify({'error': '用户不存在'}), 404
        
        if request.method == 'GET':
            print(f"返回用户 {user.username} 的资料")
            response = jsonify({
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
            # 添加CORS头
            origin = request.headers.get('Origin', '')
            allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
            
            if origin in allowed_origins:
                response.headers.add('Access-Control-Allow-Origin', origin)
            else:
                response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
                
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        
        # 更新个人资料
        if request.method == 'PUT':
            try:
                print(f"更新用户 {user.username} 的资料，内容类型: {request.content_type}")
                print(f"请求头: {request.headers}")
                
                # 检查是否是表单数据（包含头像上传）
                if request.content_type and 'multipart/form-data' in request.content_type:
                    print("检测到表单数据，处理文件上传")
                    
                    # 处理表单数据
                    if 'email' in request.form:
                        user.email = request.form['email']
                    if 'full_name' in request.form:
                        user.full_name = request.form['full_name']
                    
                    # 处理头像上传
                    if 'avatar' in request.files:
                        file = request.files['avatar']
                        if file and file.filename:
                            if allowed_file(file.filename):
                                # 确保上传目录存在
                                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
                                os.makedirs(upload_folder, exist_ok=True)
                                
                                # 生成安全的文件名
                                timestamp = int(time.time())
                                filename = secure_filename(f"avatar_{user.id}_{timestamp}.png")
                                file_path = os.path.join(upload_folder, filename)
                                
                                # 保存文件
                                file.save(file_path)
                                print(f"头像已保存到: {file_path}")
                                
                                # 更新用户头像URL
                                avatar_url = f"/uploads/avatars/{filename}"
                                user.avatar_url = avatar_url
                            else:
                                return jsonify({'error': '只允许上传图片文件 (png, jpg, jpeg, gif)'}), 400
                else:
                    # 处理JSON数据
                    try:
                        # 尝试获取JSON数据
                        data = request.get_json(force=True, silent=True)
                        print(f"解析的JSON数据: {data}")
                        
                        if not data:
                            # 如果无法解析JSON，尝试读取原始请求体
                            raw_data = request.get_data()
                            print(f"原始请求体: {raw_data}")
                            return jsonify({'error': '无效的JSON数据格式'}), 422
                        
                        # 更新用户信息
                        if 'email' in data:
                            user.email = data['email']
                        if 'full_name' in data:
                            user.full_name = data['full_name']
                    except Exception as json_err:
                        print(f"JSON解析错误: {str(json_err)}")
                        return jsonify({'error': f'无法解析JSON数据: {str(json_err)}'}), 422
                
                # 更新时间戳
                user.updated_at = datetime.datetime.utcnow()
                db.session.commit()
                
                print(f"用户 {user.username} 资料更新成功: email={user.email}, full_name={user.full_name}")
                
                response = jsonify({
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
                # 添加CORS头
                origin = request.headers.get('Origin', '')
                allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
                
                if origin in allowed_origins:
                    response.headers.add('Access-Control-Allow-Origin', origin)
                else:
                    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
                    
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Credentials', 'true')
                return response
            except Exception as e:
                db.session.rollback()
                print(f"更新个人资料时出错: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'更新个人资料时出错: {str(e)}'}), 500
    except Exception as e:
        print(f"处理个人资料请求时出错: {str(e)}")
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改当前用户的密码"""
    # 获取当前用户ID
    user_id_str = get_jwt_identity()
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        return jsonify({'error': '无效的用户ID'}), 400
        
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

@auth_bp.route('/avatar', methods=['OPTIONS'])
def avatar_options():
    response = make_response()
    origin = request.headers.get('Origin', '')
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@auth_bp.route('/avatar', methods=['POST'])
def upload_avatar():
    """专门用于上传头像的路由"""
    try:
        # 手动获取并验证令牌
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '未提供有效的认证令牌'}), 401
        
        token = auth_header.split(' ')[1]
        
        # 手动解码令牌
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = decoded_token['sub']
            if not user_id:
                return jsonify({'error': '无效的用户令牌'}), 401
        except Exception as jwt_err:
            print(f"JWT解码错误: {str(jwt_err)}")
            return jsonify({'error': f'令牌验证失败: {str(jwt_err)}'}), 401
            
        print(f"处理头像上传，用户ID: {user_id}")
        
        user = User.query.get(user_id)
        if not user:
            print(f"用户不存在，ID: {user_id}")
            return jsonify({'error': '用户不存在'}), 404
            
        print(f"开始处理用户 {user.username} 的头像上传请求")
        print(f"请求内容类型: {request.content_type}")
        print(f"请求文件: {list(request.files.keys()) if request.files else '无文件'}")
        
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 处理文件上传
        if 'avatar' not in request.files:
            print("请求中没有找到'avatar'文件")
            return jsonify({'error': '未找到头像文件'}), 400
            
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
            
        print(f"接收到文件: {file.filename}, 类型: {file.content_type}")
        
        # 检查文件类型
        if not allowed_file(file.filename):
            print(f"不允许的文件类型: {file.filename}")
            return jsonify({'error': '只允许上传图片文件 (png, jpg, jpeg, gif)'}), 400
        
        # 生成安全的文件名
        timestamp = int(time.time())
        filename = secure_filename(f"avatar_{user.id}_{timestamp}.png")
        file_path = os.path.join(upload_folder, filename)
        
        # 保存文件
        file.save(file_path)
        print(f"文件已保存到: {file_path}")
        
        # 更新用户头像URL
        avatar_url = f"/uploads/avatars/{filename}"
        user.avatar_url = avatar_url
        db.session.commit()
        print(f"用户头像URL已更新: {avatar_url}")
        
        # 添加CORS头
        response = jsonify({
            'message': '头像上传成功',
            'avatar_url': avatar_url
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
            
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

@auth_bp.route('/test-jwt', methods=['GET'])
@jwt_required()
def test_jwt():
    """测试JWT令牌是否有效"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        # 获取JWT声明
        claims = get_jwt()
        
        return jsonify({
            'message': 'JWT令牌有效',
            'user_id': user_id,
            'claims': claims
        })
    except Exception as e:
        print(f"JWT测试错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'JWT测试失败: {str(e)}'}), 500

@auth_bp.route('/simple-avatar-test', methods=['POST'])
def simple_avatar_test():
    """最简单的头像上传测试，无需认证"""
    try:
        print("开始简单头像上传测试...")
        
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'test')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 处理文件上传
        if 'avatar' not in request.files:
            print("请求中没有找到'avatar'文件")
            return jsonify({'error': '未找到头像文件'}), 400
            
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
            
        print(f"接收到文件: {file.filename}, 类型: {file.content_type}")
        
        # 生成安全的文件名
        timestamp = int(time.time())
        filename = secure_filename(f"test_simple_{timestamp}.png")
        file_path = os.path.join(upload_folder, filename)
        
        # 保存文件
        file.save(file_path)
        print(f"文件已保存到: {file_path}")
        
        # 添加CORS头
        response = jsonify({
            'message': '简单头像上传测试成功',
            'avatar_url': f"/uploads/test/{filename}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
            
    except Exception as e:
        print(f"简单头像上传测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'简单头像上传测试失败: {str(e)}'}), 500

@auth_bp.route('/upload-avatar/<int:user_id>', methods=['OPTIONS'])
def upload_avatar_options(user_id):
    response = make_response()
    origin = request.headers.get('Origin', '')
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@auth_bp.route('/upload-avatar/<int:user_id>', methods=['POST'])
def upload_avatar_direct(user_id):
    """直接通过用户ID上传头像，不使用JWT验证"""
    try:
        print(f"处理头像上传，用户ID: {user_id}")
        
        user = User.query.get(user_id)
        if not user:
            print(f"用户不存在，ID: {user_id}")
            return jsonify({'error': '用户不存在'}), 404
            
        print(f"开始处理用户 {user.username} 的头像上传请求")
        print(f"请求内容类型: {request.content_type}")
        print(f"请求文件: {list(request.files.keys()) if request.files else '无文件'}")
        
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 处理文件上传
        if 'avatar' not in request.files:
            print("请求中没有找到'avatar'文件")
            return jsonify({'error': '未找到头像文件'}), 400
            
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
            
        print(f"接收到文件: {file.filename}, 类型: {file.content_type}")
        
        # 检查文件类型
        if not allowed_file(file.filename):
            print(f"不允许的文件类型: {file.filename}")
            return jsonify({'error': '只允许上传图片文件 (png, jpg, jpeg, gif)'}), 400
        
        # 生成安全的文件名
        timestamp = int(time.time())
        filename = secure_filename(f"avatar_{user.id}_{timestamp}.png")
        file_path = os.path.join(upload_folder, filename)
        
        # 保存文件
        file.save(file_path)
        print(f"文件已保存到: {file_path}")
        
        # 更新用户头像URL
        avatar_url = f"/uploads/avatars/{filename}"
        user.avatar_url = avatar_url
        db.session.commit()
        print(f"用户头像URL已更新: {avatar_url}")
        
        # 添加CORS头
        response = jsonify({
            'message': '头像上传成功',
            'avatar_url': avatar_url
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
            
    except Exception as e:
        db.session.rollback()
        print(f"处理头像上传请求时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500

@auth_bp.route('/simple-avatar-upload', methods=['POST', 'OPTIONS'])
def simple_avatar_upload():
    """简单的头像上传端点，不需要认证"""
    if request.method == 'OPTIONS':
        response = make_response()
        origin = request.headers.get('Origin', '')
        allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
        
        if origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
            
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    try:
        print("开始处理简单头像上传请求")
        
        # 获取用户ID
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'error': '缺少用户ID'}), 400
            
        print(f"上传头像，用户ID: {user_id}")
        
        # 查找用户
        user = User.query.get(user_id)
        if not user:
            print(f"用户不存在，ID: {user_id}")
            return jsonify({'error': '用户不存在'}), 404
        
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 处理文件上传
        if 'avatar' not in request.files:
            print("请求中没有找到'avatar'文件")
            return jsonify({'error': '未找到头像文件'}), 400
            
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
            
        print(f"接收到文件: {file.filename}, 类型: {file.content_type}")
        
        # 检查文件类型
        if not allowed_file(file.filename):
            print(f"不允许的文件类型: {file.filename}")
            return jsonify({'error': '只允许上传图片文件 (png, jpg, jpeg, gif)'}), 400
        
        # 生成安全的文件名
        timestamp = int(time.time())
        filename = secure_filename(f"avatar_{user_id}_{timestamp}.png")
        file_path = os.path.join(upload_folder, filename)
        
        # 保存文件
        file.save(file_path)
        print(f"文件已保存到: {file_path}")
        
        # 更新用户头像URL
        avatar_url = f"/uploads/avatars/{filename}"
        user.avatar_url = avatar_url
        db.session.commit()
        print(f"用户头像URL已更新: {avatar_url}")
        
        # 添加CORS头
        response = jsonify({
            'message': '头像上传成功',
            'avatar_url': avatar_url
        })
        
        # 使用请求的Origin而不是通配符
        origin = request.headers.get('Origin', '')
        allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
        
        if origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
            
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
            
    except Exception as e:
        db.session.rollback()
        print(f"处理头像上传请求时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500

