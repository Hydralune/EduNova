from flask import Blueprint, request, jsonify, current_app, make_response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import json
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from backend.models.user import User, db
from backend.models.course import Course
from backend.models.learning import LearningRecord, ChatHistory
from backend.models.material import Material
from backend.models.assessment import Assessment, StudentAnswer, AssessmentSubmission
import hashlib
import requests
import openai
import re
from dotenv import load_dotenv
import time
import uuid
import threading
import functools
from backend.api.rag_ai import get_api_config
from sqlalchemy import func, desc, and_

learning_bp = Blueprint('learning', __name__)

# 检查是否为教师或管理员的辅助函数
def teacher_or_admin_required():
    claims = get_jwt()
    role = claims.get('role')
    if role not in ['teacher', 'admin']:
        return jsonify({"error": "需要教师或管理员权限"}), 403
    return None

# 通用错误处理装饰器
def api_error_handler(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"API异常: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            
            # 创建错误响应
            response = jsonify({
                'status': 'error',
                'message': f'服务器处理请求时出错: {str(e)}',
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            })
            
            # 添加CORS头
            origin = request.headers.get('Origin', '')
            allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
            
            if origin in allowed_origins:
                response.headers.add('Access-Control-Allow-Origin', origin)
            else:
                response.headers.add('Access-Control-Allow-Origin', '*')
                
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,GET,PUT,DELETE,OPTIONS')
            response.headers.add('Content-Type', 'application/json')
            
            return response, 500
    return decorated_function

# 应用错误处理装饰器到关键API端点
@learning_bp.route('/assessments/ai-generate', methods=['POST', 'OPTIONS'])
@api_error_handler
def generate_ai_assessment():
    """使用AI自动生成评估内容"""
    # 调试信息：记录完整请求详情
    current_app.logger.info(f"收到请求: {request.method} {request.path} (完整URL: {request.url})")
    current_app.logger.info(f"请求头: {request.headers}")
    
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        current_app.logger.info("处理OPTIONS请求")
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Content-Type', 'application/json')
        return response
        
    data = request.json
    current_app.logger.info(f"收到AI自动生成评估请求: {data}")
    
    # 验证必要数据
    required_fields = ['course_name', 'course_description']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # 获取课程信息
    course_name = data['course_name']
    course_description = data['course_description']
    extra_info = data.get('extra_info', '')
    assessment_type = data.get('assessment_type', 'quiz')
    difficulty = data.get('difficulty', 'medium')
    course_id = data.get('course_id')
    
    # 创建唯一的请求ID (使用时间戳+课程ID)
    request_id = f"{int(time.time())}_{course_id}_{str(uuid.uuid4())[:8]}"
    
    # 创建保存目录
    ai_assessments_dir = os.path.join(current_app.root_path, 'uploads', 'ai_assessments')
    os.makedirs(ai_assessments_dir, exist_ok=True)
    
    # 构建文件路径
    file_path = os.path.join(ai_assessments_dir, f"assessment_{request_id}.json")
    
    # 保存请求信息
    request_data = {
        'status': 'processing',
        'request_id': request_id,
        'course_name': course_name,
        'course_description': course_description,
        'extra_info': extra_info,
        'assessment_type': assessment_type,
        'difficulty': difficulty,
        'course_id': course_id,
        'timestamp': datetime.now().isoformat()
    }
    
    # 先保存请求信息
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(request_data, f, ensure_ascii=False, indent=2)
    
    current_app.logger.info(f"请求信息已保存到: {file_path}")
    
    # 在后台线程中处理AI生成，避免长时间阻塞
    # 获取当前的应用实例，以便在线程中使用
    app = current_app._get_current_object()
    
    def generate_in_background():
        # 在线程中使用应用上下文
        with app.app_context():
            try:
                # 调用AI生成评估
                generated_assessment = generate_assessment_with_ai(
                    course_name, 
                    course_description, 
                    extra_info, 
                    assessment_type, 
                    difficulty
                )
                
                # 添加课程ID（如果提供）
                if course_id:
                    generated_assessment['course_id'] = course_id
                
                # 添加请求ID用于跟踪
                generated_assessment['request_id'] = request_id
                
                # 保存生成的评估
                result_data = {
                    'status': 'success',
                    'request_id': request_id,
                    'assessment': generated_assessment,
                    'timestamp': datetime.now().isoformat()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                
                app.logger.info(f"生成的评估已保存到: {file_path}")
                
            except Exception as e:
                # 保存错误信息
                error_data = {
                    'status': 'error',
                    'request_id': request_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(error_data, f, ensure_ascii=False, indent=2)
                
                app.logger.error(f"生成评估失败: {str(e)}")
    
    # 启动后台线程
    thread = threading.Thread(target=generate_in_background)
    thread.daemon = True
    thread.start()
    
    # 立即返回请求ID，让前端可以用它来后续查询结果
    response_data = {
        'status': 'processing',
        'message': '正在生成评估，请稍后查询结果',
        'request_id': request_id
    }
    
    response = jsonify(response_data)
    
    # 添加CORS头
    origin = request.headers.get('Origin', '')
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')
        
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,GET,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Content-Type', 'application/json')
    
    # 调试输出
    current_app.logger.info(f"返回响应: {response_data}")
    
    return response

@learning_bp.route('/record', methods=['POST'])
def record_learning_activity():
    """记录学习活动"""
    data = request.json
    
    # 验证必要数据
    required_fields = ['student_id', 'course_id', 'activity_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    learning_record = LearningRecord(
        student_id=data['student_id'],
        course_id=data['course_id'],
        activity_type=data['activity_type'],
        activity_detail=json.dumps(data.get('activity_detail', {})),
        duration=data.get('duration')
    )
    
    db.session.add(learning_record)
    db.session.commit()
    
    return jsonify({'success': True, 'record_id': learning_record.id}), 201

@learning_bp.route('/history/<int:student_id>', methods=['GET'])
def get_learning_history(student_id):
    """获取学生的学习历史记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    records = LearningRecord.query.filter_by(student_id=student_id)\
        .order_by(LearningRecord.timestamp.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'records': [record.to_dict() for record in records.items],
        'total': records.total,
        'pages': records.pages,
        'page': page
    }), 200

# 添加OPTIONS请求处理
@learning_bp.route('/courses', methods=['OPTIONS'])
def courses_options():
    return '', 200

# 获取课程列表
@learning_bp.route('/courses', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_courses():
    """获取课程列表"""
    # 获取查询参数
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = Course.query
    
    # 应用过滤条件
    if category:
        query = query.filter_by(category=category)
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(Course.name.ilike(search_term) | Course.description.ilike(search_term))
    
    # 执行分页查询
    courses_pagination = query.paginate(page=page, per_page=per_page)
    
    # 准备响应数据
    courses_data = []
    for course in courses_pagination.items:
        course_dict = course.to_dict()
        # 添加额外信息
        course_dict['material_count'] = Material.query.filter_by(course_id=course.id).count()
        courses_data.append(course_dict)
    
    return jsonify({
        'courses': courses_data,
        'total': courses_pagination.total,
        'pages': courses_pagination.pages,
        'current_page': page
    })

# 获取课程详情
@learning_bp.route('/courses/<int:course_id>', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_course(course_id):
    """获取课程详情"""
    # 查找课程
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 获取课程详情
    course_data = course.to_dict()
    
    # 添加额外信息
    course_data['material_count'] = Material.query.filter_by(course_id=course.id).count()
    course_data['teacher_name'] = User.query.get(course.teacher_id).full_name if course.teacher_id else None
    
    return jsonify(course_data)

# 创建课程
@learning_bp.route('/courses', methods=['POST'])
# @jwt_required()  # 暂时禁用JWT认证要求
def create_course():
    """创建新课程"""
    # 检查是否有表单数据（包含文件上传）或JSON数据
    if request.content_type and 'multipart/form-data' in request.content_type:
        # 处理表单数据和文件上传
        if 'data' not in request.form:
            return jsonify({'error': 'Missing course data'}), 400
        
        try:
            # 解析JSON字符串
            data = json.loads(request.form['data'])
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # 处理封面图片
        cover_image_path = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # 创建课程封面目录
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'courses', 'covers')
                os.makedirs(upload_folder, exist_ok=True)
                
                # 保存文件
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # 设置相对路径
                cover_image_path = f'/uploads/courses/covers/{filename}'
    else:
        # 处理JSON数据
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        cover_image_path = None
    
    # 验证必要字段
    if 'name' not in data:
        return jsonify({'error': 'Course name is required'}), 400
    
    # 设置教师ID
    # user_id = get_jwt_identity()  # 暂时注释掉
    user_id = 2  # 使用默认教师ID
    
    # 创建新课程
    new_course = Course(
        name=data['name'],
        description=data.get('description', ''),
        category=data.get('category', ''),
        difficulty=data.get('difficulty', 'beginner'),
        is_public=data.get('is_public', True),
        cover_image=cover_image_path,
        teacher_id=user_id
    )
    
    db.session.add(new_course)
    db.session.commit()
    
    return jsonify(new_course.to_dict()), 201

# 更新课程
@learning_bp.route('/courses/<int:course_id>', methods=['PUT'])
# @jwt_required()  # 暂时禁用JWT认证要求
def update_course(course_id):
    """更新课程信息"""
    # 查找课程
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 检查权限
    # user_id = get_jwt_identity()
    # claims = get_jwt()
    # role = claims.get('role')
    
    # if role != 'admin' and course.teacher_id != user_id:
    #     return jsonify({'error': 'Permission denied'}), 403
    
    # 检查是否有表单数据（包含文件上传）或JSON数据
    if request.content_type and 'multipart/form-data' in request.content_type:
        # 处理表单数据和文件上传
        if 'data' not in request.form:
            return jsonify({'error': 'Missing course data'}), 400
        
        try:
            # 解析JSON字符串
            data = json.loads(request.form['data'])
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # 处理封面图片
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # 创建课程封面目录
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'courses', 'covers')
                os.makedirs(upload_folder, exist_ok=True)
                
                # 保存文件
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # 设置相对路径
                course.cover_image = f'/uploads/courses/covers/{filename}'
    else:
        # 处理JSON数据
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
    
    # 更新课程信息
    if 'name' in data:
        course.name = data['name']
    
    if 'description' in data:
        course.description = data['description']
    
    if 'category' in data:
        course.category = data['category']
    
    if 'difficulty' in data:
        course.difficulty = data['difficulty']
    
    if 'is_public' in data:
        course.is_public = data['is_public']
    
    # 保存更改
    db.session.commit()
    
    return jsonify(course.to_dict())

# 删除课程
@learning_bp.route('/courses/<int:course_id>', methods=['DELETE'])
# @jwt_required()  # 暂时禁用JWT认证要求
def delete_course(course_id):
    """删除课程"""
    # 查找课程
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 检查权限
    # user_id = get_jwt_identity()
    # claims = get_jwt()
    # role = claims.get('role')
    
    # if role != 'admin' and course.teacher_id != user_id:
    #     return jsonify({'error': 'Permission denied'}), 403
    
    # 删除课程
    course_data = course.to_dict()
    db.session.delete(course)
    db.session.commit()
    
    return jsonify({'message': 'Course deleted successfully', 'course': course_data})

@learning_bp.route('/my-courses', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_my_courses():
    # user_id = get_jwt_identity()  # 暂时注释掉
    user_id = 2  # 使用默认ID
    
    # 查询教师的课程
    my_courses = Course.query.filter_by(teacher_id=user_id).all()
    
    return jsonify({
        'courses': [course.to_dict() for course in my_courses],
        'total': len(my_courses)
    })

# 获取课程的所有课件
@learning_bp.route('/courses/<int:course_id>/materials', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_course_materials(course_id):
    """获取课程的所有课件资源"""
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 获取课程的所有课件
    materials = Material.query.filter_by(course_id=course_id).all()
    
    return jsonify({
        'materials': [material.to_dict() for material in materials],
        'total': len(materials)
    })

# 上传课件
@learning_bp.route('/courses/<int:course_id>/materials', methods=['POST'])
# @jwt_required()  # 暂时禁用JWT认证要求
def upload_material(course_id):
    """上传课件资源"""
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # 如果用户没有选择文件，浏览器也会提交一个没有文件名的空部分
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 获取文件信息
    original_filename = file.filename
    
    # 创建上传目录
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'materials', str(course_id))
    os.makedirs(upload_folder, exist_ok=True)
    
    # 保存文件，使用原始文件名
    file_path = os.path.join(upload_folder, original_filename)
    file.save(file_path)
    
    # 计算文件哈希值
    def calculate_file_hash(file_path):
        """计算文件的SHA256哈希值"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    file_hash = calculate_file_hash(file_path)
    
    # 检查是否已存在相同哈希值的文件
    existing_material = Material.query.filter_by(
        file_hash=file_hash, 
        course_id=course_id
    ).first()
    
    if existing_material:
        # 删除刚上传的重复文件
        try:
            os.remove(file_path)
        except:
            pass
        
        # 返回已存在的文件信息
        material_dict = existing_material.to_dict()
        
        # 添加文件大小信息
        if existing_material.file_path:
            existing_file_path = os.path.join(current_app.root_path, existing_material.file_path.lstrip('/'))
            if os.path.exists(existing_file_path):
                size = os.path.getsize(existing_file_path)
                size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
                material_dict['size'] = size_str
            else:
                material_dict['size'] = '文件不存在'
        else:
            material_dict['size'] = '未知'
        
        return jsonify({
            'status': 'duplicate',
            'message': f'文件 "{original_filename}" 已存在，避免重复上传',
            'material': material_dict
        }), 200
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    size_str = ''
    if file_size < 1024:
        size_str = f"{file_size}B"
    elif file_size < 1024 * 1024:
        size_str = f"{file_size / 1024:.1f}KB"
    else:
        size_str = f"{file_size / (1024 * 1024):.1f}MB"
    
    # 根据文件扩展名确定文件类型
    _, file_ext = os.path.splitext(original_filename)
    file_extension = file_ext.lower()
    
    # 文件扩展名映射到类型
    extension_to_type = {
        '.pdf': 'PDF',
        '.doc': 'Word', '.docx': 'Word',
        '.ppt': 'PowerPoint', '.pptx': 'PowerPoint',
        '.xls': 'Excel', '.xlsx': 'Excel',
        '.jpg': 'Image', '.jpeg': 'Image', '.png': 'Image', 
        '.gif': 'Image', '.bmp': 'Image', '.webp': 'Image',
        '.mp4': 'Video', '.avi': 'Video', '.mov': 'Video',
        '.wmv': 'Video', '.flv': 'Video', '.mkv': 'Video',
        '.webm': 'Video', '.m4v': 'Video', '.3gp': 'Video',
        '.zip': 'Archive', '.rar': 'Archive', '.7z': 'Archive',
        '.txt': 'Text', 
        '.md': 'Markdown', '.markdown': 'Markdown',
        '.json': 'Text', '.xml': 'Text', '.csv': 'Text',
        '.html': 'Text', '.css': 'Text', '.js': 'Text'
    }
    
    # 获取文件类型
    material_type = extension_to_type.get(file_extension, 'Other')
    
    # 如果类型是Other，使用文件扩展名作为类型（不带点）
    if material_type == 'Other' and file_extension:
        material_type = file_extension[1:].upper()
    
    # 创建新的Material对象
    new_material = Material(
        title=original_filename,
        material_type=material_type,
        file_path=f'/uploads/materials/{course_id}/{original_filename}',
        file_hash=file_hash,  # 添加文件哈希值
        content=f'Original filename: {original_filename}',
        course_id=course_id
    )
    
    # 添加到数据库
    db.session.add(new_material)
    db.session.commit()
    
    # 返回创建的材料
    material_dict = new_material.to_dict()
    material_dict['size'] = size_str  # 添加文件大小信息
    
    return jsonify({
        'status': 'success',
        'message': f'文件 "{original_filename}" 上传成功',
        'material': material_dict
    }), 201

# 获取单个课件详情
@learning_bp.route('/materials/<int:material_id>', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_material(material_id):
    """获取单个课件详情"""
    # 查找材料
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404
    
    # 返回材料详情
    material_dict = material.to_dict()
    
    # 添加文件大小信息
    if material.file_path:
        file_path = os.path.join(current_app.root_path, material.file_path.lstrip('/'))
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
            material_dict['size'] = size_str
        else:
            material_dict['size'] = '文件不存在'
    else:
        material_dict['size'] = '未知'
    
    return jsonify(material_dict)

# 更新课件
@learning_bp.route('/materials/<int:material_id>', methods=['PUT'])
# @jwt_required()  # 暂时禁用JWT认证要求
def update_material(material_id):
    """更新课件信息"""
    # 查找材料
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404
    
    # 获取请求数据
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新材料信息
    if 'title' in data:
        material.title = data['title']
    if 'description' in data:
        material.description = data['description']
    if 'content' in data:
        material.content = data['content']
    
    # 保存更改
    db.session.commit()
    
    # 返回更新后的材料信息
    material_dict = material.to_dict()
    
    # 添加文件大小信息
    if material.file_path:
        file_path = os.path.join(current_app.root_path, material.file_path.lstrip('/'))
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
            material_dict['size'] = size_str
        else:
            material_dict['size'] = '文件不存在'
    else:
        material_dict['size'] = '未知'
    
    return jsonify(material_dict)

# 下载课件
@learning_bp.route('/materials/<int:material_id>/download', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def download_material(material_id):
    """下载课件资源"""
    # 查找材料
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404
    
    # 获取文件路径
    file_path = os.path.join(current_app.root_path, material.file_path.lstrip('/'))
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # 获取原始文件名
    original_filename = None
    if material.content and material.content.startswith('Original filename:'):
        original_filename = material.content.replace('Original filename:', '').strip()
    
    # 如果没有原始文件名，使用路径中的文件名
    download_name = original_filename or os.path.basename(file_path)
    
    # 发送文件 - 确保以二进制模式发送
    try:
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=download_name,
            mimetype='application/octet-stream'  # 使用通用的二进制MIME类型
        )
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

# 删除课件
@learning_bp.route('/materials/<int:material_id>', methods=['DELETE'])
# @jwt_required()  # 暂时禁用JWT认证要求
def delete_material(material_id):
    """删除课件资源"""
    # 查找材料
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404
    
    # 获取文件路径
    file_path = os.path.join(current_app.root_path, material.file_path.lstrip('/'))
    
    # 尝试删除文件
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Warning: Failed to delete file {file_path}: {str(e)}")
    
    # 从数据库中删除材料记录
    material_dict = material.to_dict()
    db.session.delete(material)
    db.session.commit()
    
    return jsonify({
        'message': 'Material deleted successfully',
        'material': material_dict
    })

# 获取课程的所有学生
@learning_bp.route('/courses/<int:course_id>/students', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_course_students(course_id):
    """获取课程的所有学生"""
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 获取查询参数
    search = request.args.get('search', '')
    
    # 获取课程的所有学生
    students = course.students
    
    # 如果有搜索参数，过滤学生
    if search:
        search = search.lower()
        filtered_students = []
        for student in students:
            if search in student.username.lower() or search in student.email.lower() or (student.full_name and search in student.full_name.lower()):
                filtered_students.append(student)
        students = filtered_students
    
    # 准备响应数据
    students_data = []
    for student in students:
        # 获取学生的学习记录
        learning_records = LearningRecord.query.filter_by(
            student_id=student.id, 
            course_id=course_id
        ).order_by(LearningRecord.timestamp.desc()).first()
        
        # 计算学生进度（这里简化为随机值，实际应用中应该基于完成的材料和评估）
        progress = 0
        if learning_records:
            # 这里可以实现更复杂的进度计算逻辑
            progress = 50  # 示例值
        
        # 获取最后活动时间
        last_activity = None
        if learning_records:
            last_activity = learning_records.timestamp.strftime('%Y-%m-%d %H:%M')
        
        # 构建学生数据
        student_data = {
            'id': student.id,
            'name': student.full_name or student.username,
            'email': student.email,
            'progress': progress,
            'last_activity': last_activity or '未活动'
        }
        students_data.append(student_data)
    
    return jsonify({
        'students': students_data,
        'total': len(students_data)
    })

# 获取可添加到课程的学生
@learning_bp.route('/courses/<int:course_id>/available-students', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_available_students(course_id):
    """获取可添加到课程的学生"""
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 获取当前课程的所有学生ID
    current_student_ids = [student.id for student in course.students]
    
    # 获取所有学生角色的用户，但不包括已在课程中的学生
    available_students = User.query.filter(
        User.role == 'student',
        ~User.id.in_(current_student_ids) if current_student_ids else True
    ).all()
    
    # 准备响应数据
    students_data = []
    for student in available_students:
        student_data = {
            'id': student.id,
            'name': student.full_name or student.username,
            'email': student.email,
            'role': student.role
        }
        students_data.append(student_data)
    
    return jsonify({
        'students': students_data,
        'total': len(students_data)
    })

# 添加学生到课程
@learning_bp.route('/courses/<int:course_id>/students', methods=['POST'])
# @jwt_required()  # 暂时禁用JWT认证要求
def add_students_to_course(course_id):
    """添加学生到课程"""
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 获取请求数据
    data = request.json
    if not data or 'student_ids' not in data:
        return jsonify({'error': 'Missing student_ids'}), 400
    
    student_ids = data['student_ids']
    if not isinstance(student_ids, list):
        return jsonify({'error': 'student_ids must be a list'}), 400
    
    # 获取当前课程的学生ID
    current_student_ids = [student.id for student in course.students]
    
    # 添加新学生
    added_students = []
    for student_id in student_ids:
        if student_id not in current_student_ids:
            student = User.query.get(student_id)
            if student and student.role == 'student':
                course.students.append(student)
                
                # 记录学习活动
                record = LearningRecord(
                    student_id=student.id,
                    course_id=course.id,
                    activity_type='enrolled',
                    activity_detail='Enrolled to course'
                )
                db.session.add(record)
                
                # 构建学生数据
                student_data = {
                    'id': student.id,
                    'name': student.full_name or student.username,
                    'email': student.email,
                    'progress': 0,
                    'last_activity': datetime.utcnow().strftime('%Y-%m-%d %H:%M')
                }
                added_students.append(student_data)
    
    # 保存更改
    db.session.commit()
    
    return jsonify({
        'message': f'Added {len(added_students)} students to the course',
        'students': added_students
    }), 201

# 从课程中移除学生
@learning_bp.route('/courses/<int:course_id>/students/<int:student_id>', methods=['DELETE'])
# @jwt_required()  # 暂时禁用JWT认证要求
def remove_student_from_course(course_id, student_id):
    """从课程中移除学生"""
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 查找学生
    student = User.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # 检查学生是否在课程中
    if student not in course.students:
        return jsonify({'error': 'Student not enrolled in this course'}), 404
    
    # 构建学生数据（用于返回）
    student_data = {
        'id': student.id,
        'name': student.full_name or student.username,
        'email': student.email
    }
    
    # 从课程中移除学生
    course.students.remove(student)
    
    # 记录学习活动
    record = LearningRecord(
        student_id=student.id,
        course_id=course.id,
        activity_type='unenrolled',
        activity_detail='Removed from course'
    )
    db.session.add(record)
    
    # 保存更改
    db.session.commit()
    
    return jsonify({
        'message': 'Student removed from course successfully',
        'student': student_data
    })

# ============ 评估相关API ============

@learning_bp.route('/assessments', methods=['GET', 'OPTIONS'])
# @jwt_required()  # 暂时禁用JWT认证要求
@api_error_handler
def get_assessments():
    """获取评估列表"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
        
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        course_id = request.args.get('course_id', type=int)
        
        # 构建查询
        query = Assessment.query
        
        # 如果指定了课程ID，筛选该课程的评估
        if course_id:
            query = query.filter_by(course_id=course_id)
            
        # 按创建时间降序排序
        query = query.order_by(Assessment.created_at.desc())
        
        # 分页
        try:
            assessments_pagination = query.paginate(page=page, per_page=per_page)
        except Exception as e:
            current_app.logger.error(f"分页查询失败: {str(e)}")
            # 尝试不使用created_by字段进行查询
            assessments = query.all()
            total = len(assessments)
            start = (page - 1) * per_page
            end = start + per_page
            assessments = assessments[start:end]
            
            # 创建自定义分页结果
            result = {
                'items': [a.to_dict() for a in assessments],
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page  # 向上取整
            }
        else:
            # 使用标准分页结果
            result = {
                'items': [a.to_dict() for a in assessments_pagination.items],
                'page': assessments_pagination.page,
                'per_page': assessments_pagination.per_page,
                'total': assessments_pagination.total,
                'pages': assessments_pagination.pages
            }
        
        # 创建响应
        response = jsonify({
            'status': 'success',
            'assessments': result['items'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
        
        # 添加CORS头
        origin = request.headers.get('Origin', '')
        allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
        
        if origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', '*')
            
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"获取评估列表失败: {str(e)}")
        
        # 创建错误响应
        response = jsonify({
            'status': 'error',
            'message': f'获取评估列表失败: {str(e)}'
        })
        
        # 添加CORS头
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        
        return response, 500

@learning_bp.route('/assessments/<int:assessment_id>', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_assessment(assessment_id):
    """获取单个评估详情"""
    assessment = Assessment.query.get(assessment_id)
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404
    
    return jsonify(assessment.to_dict())

@learning_bp.route('/assessments', methods=['OPTIONS'])
def assessments_options():
    """处理评估接口的OPTIONS请求"""
    response = make_response()
    origin = request.headers.get('Origin', '')
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')
        
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

@learning_bp.route('/assessments', methods=['POST'])
# @jwt_required()  # 暂时禁用JWT认证要求
@api_error_handler
def create_assessment():
    """创建新的评估"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
        
    try:
        data = request.json
        current_app.logger.info(f"接收到创建评估请求: {data}")
        
        # 验证必要字段
        required_fields = ['title', 'course_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 处理日期字段
        start_date = None
        if data.get('start_date'):
            try:
                start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except:
                start_date = None
                
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except:
                due_date = None
        
        # 确保questions字段不为NULL
        questions_json = '[]'
        if 'questions' in data and data['questions']:
            questions_json = json.dumps(data['questions'])
        
        # 创建评估对象
        assessment = Assessment(
            title=data['title'],
            description=data.get('description', ''),
            course_id=data['course_id'],
            total_score=data.get('total_score', 100),
            duration=data.get('duration'),
            start_date=start_date,
            due_date=due_date,
            max_attempts=data.get('max_attempts'),
            is_published=data.get('is_published', False),
            is_active=data.get('is_active', True),
            questions=questions_json,  # 直接设置questions字段
            created_by=1  # 暂时硬编码为1，实际应该使用 get_jwt_identity()
        )
        
        # 保存评估
        db.session.add(assessment)
        db.session.commit()
        
        # 创建响应
        response = jsonify({
            'status': 'success',
            'message': '评估创建成功',
            'assessment_id': assessment.id,
            'assessment': assessment.to_dict()
        })
        
        # 添加CORS头
        origin = request.headers.get('Origin', '')
        allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
        
        if origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', '*')
            
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"创建评估失败: {str(e)}")
        db.session.rollback()
        
        # 创建错误响应
        response = jsonify({
            'status': 'error',
            'message': f'创建评估失败: {str(e)}'
        })
        
        # 添加CORS头
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        
        return response, 500

@learning_bp.route('/assessments/<int:assessment_id>', methods=['PUT', 'OPTIONS'])
# @jwt_required()  # 暂时禁用JWT认证要求
@api_error_handler
def update_assessment(assessment_id):
    """更新评估"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'PUT,OPTIONS')
        return response
        
    try:
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        data = request.json
        current_app.logger.info(f"接收到更新评估请求: {assessment_id}, 数据: {data}")
        
        # 处理日期字段
        if 'start_date' in data:
            try:
                assessment.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')) if data['start_date'] else None
            except:
                pass
                
        if 'due_date' in data:
            try:
                assessment.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data['due_date'] else None
            except:
                pass
        
        # 更新基本信息
        assessment.title = data.get('title', assessment.title)
        assessment.description = data.get('description', assessment.description)
        assessment.total_score = data.get('total_score', assessment.total_score)
        assessment.duration = data.get('duration', assessment.duration)
        assessment.max_attempts = data.get('max_attempts', assessment.max_attempts)
        assessment.is_published = data.get('is_published', assessment.is_published)
        assessment.is_active = data.get('is_active', assessment.is_active)
        
        # 更新题目
        if 'questions' in data and data['questions'] is not None:
            # 将题目列表转换为JSON字符串
            assessment.questions = json.dumps(data['questions'])
        
        db.session.commit()
        
        # 创建响应
        response = jsonify({
            'status': 'success',
            'message': '评估更新成功',
            'assessment_id': assessment.id,
            'assessment': assessment.to_dict()
        })
        
        # 添加CORS头
        origin = request.headers.get('Origin', '')
        allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
        
        if origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', '*')
            
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'PUT')
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"更新评估失败: {str(e)}")
        db.session.rollback()
        
        # 创建错误响应
        response = jsonify({
            'status': 'error',
            'message': f'更新评估失败: {str(e)}'
        })
        
        # 添加CORS头
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        
        return response, 500

@learning_bp.route('/assessments/<int:assessment_id>', methods=['OPTIONS'])
def assessment_options(assessment_id):
    """处理评估相关的OPTIONS请求"""
    response = make_response()
    origin = request.headers.get('Origin', '')
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')
        
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@learning_bp.route('/assessments/<int:assessment_id>', methods=['DELETE'])
# @jwt_required()  # 暂时禁用JWT认证要求
@api_error_handler
def delete_assessment(assessment_id):
    """删除评估"""
    assessment = Assessment.query.get(assessment_id)
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404
    
    assessment_data = assessment.to_dict()
    db.session.delete(assessment)
    db.session.commit()
    
    response = jsonify({'message': 'Assessment deleted successfully', 'assessment': assessment_data})
    
    # 添加CORS头
    origin = request.headers.get('Origin', '')
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')
        
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    return response

@learning_bp.route('/assessments/<int:assessment_id>/submit', methods=['POST', 'OPTIONS'])
# @jwt_required()  # 暂时禁用JWT认证要求
@api_error_handler
def submit_assessment(assessment_id):
    """提交评估答案"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
        
    try:
        data = request.json
        current_app.logger.info(f"收到评估提交请求: assessment_id={assessment_id}, data={data}")
        
        # 详细记录请求数据结构
        current_app.logger.info(f"请求数据类型: {type(data)}")
        if 'answers' in data:
            current_app.logger.info(f"answers类型: {type(data['answers'])}")
            current_app.logger.info(f"answers内容: {data['answers']}")
        else:
            current_app.logger.info("请求中没有answers字段")
        
        # 在实际应用中，应该从JWT中获取学生ID
        # student_id = get_jwt_identity()
        student_id = data.get('student_id', 1)  # 临时使用请求中的学生ID或默认值
        current_app.logger.info(f"学生ID: {student_id}")
        
        # 验证评估是否存在
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            current_app.logger.error(f"评估不存在: assessment_id={assessment_id}")
            response = jsonify({'error': 'Assessment not found'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 404
        
        # 验证截止日期
        if assessment.due_date and datetime.utcnow() > assessment.due_date:
            current_app.logger.warning(f"评估截止日期已过: assessment_id={assessment_id}")
            response = jsonify({'error': 'Assessment submission deadline has passed'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # 验证尝试次数
        existing_attempts = StudentAnswer.query.filter_by(
            student_id=student_id,
            assessment_id=assessment_id
        ).count()
        
        # 检查评估的最大尝试次数设置
        max_attempts = assessment.max_attempts or 3
        if existing_attempts >= max_attempts:
            current_app.logger.warning(f"超过最大尝试次数: student_id={student_id}, assessment_id={assessment_id}")
            response = jsonify({'error': 'Maximum number of attempts reached'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # 创建学生答案记录
        answers_json = json.dumps(data.get('answers', {}))
        current_app.logger.info(f"答案JSON长度: {len(answers_json)}")
        
        # 确保answers是有效的JSON格式
        try:
            # 尝试解析answers，确保它是有效的JSON
            answers_data = data.get('answers', {})
            if isinstance(answers_data, list):
                # 如果是列表，直接使用
                processed_answers = answers_data
            elif isinstance(answers_data, dict):
                # 如果是字典，转换为列表
                processed_answers = list(answers_data.values())
            else:
                # 其他情况，尝试转换为JSON字符串
                processed_answers = answers_data
                
            # 重新序列化为JSON字符串
            answers_json = json.dumps(processed_answers)
            current_app.logger.info(f"处理后的答案JSON: {answers_json[:100]}...")
        except Exception as e:
            current_app.logger.error(f"处理答案数据时出错: {str(e)}")
            return jsonify({'error': 'Invalid answers format'}), 400
        
        student_answer = StudentAnswer(
            student_id=student_id,
            assessment_id=assessment_id,
            answers=answers_json,
            submitted_at=datetime.utcnow()
        )
        
        # 自动评分逻辑
        score = 0
        assessment_data = assessment.get_questions()
        student_answers = data.get('answers', [])
        
        current_app.logger.info(f"题目数据类型: {type(assessment_data)}")
        current_app.logger.info(f"学生答案类型: {type(student_answers)}")
        
        # 确保student_answers是列表
        if isinstance(student_answers, dict):
            student_answers = list(student_answers.values())
        
        # 确保assessment_data是一个字典，包含sections字段
        if isinstance(assessment_data, dict) and 'sections' in assessment_data:
            sections = assessment_data['sections']
        else:
            # 如果不是新格式，将问题列表转换为单个section
            sections = [{
                'questions': assessment_data if isinstance(assessment_data, list) else [],
                'score_per_question': assessment.total_score / len(assessment_data) if isinstance(assessment_data, list) and len(assessment_data) > 0 else 0
            }]

        question_index = 0
        question_scores = []  # 存储每道题的得分
        question_feedback = []  # 存储每道题的反馈
        
        for section in sections:
            for question in section['questions']:
                if question_index >= len(student_answers):
                    question_scores.append(0)
                    question_feedback.append('')
                    question_index += 1
                    continue

                user_answer = student_answers[question_index]
                is_correct = False
                question_score = 0

                # 客观题自动评分
                if question['type'] in ['multiple_choice', 'true_false', 'multiple_select', 'fill_in_blank']:
                    if question['type'] == 'multiple_choice':
                        # 检查选项是否匹配（考虑字母和数字格式）
                        if isinstance(user_answer, str) and len(user_answer) == 1:
                            correct_index = int(question['answer'])
                            user_index = ord(user_answer) - ord('A')
                            is_correct = correct_index == user_index
                        else:
                            is_correct = str(user_answer) == str(question['answer'])

                    elif question['type'] == 'multiple_select':
                        # 多选题比较（转换为集合进行比较）
                        if isinstance(user_answer, list) and isinstance(question['answer'], list):
                            user_set = set(str(x) for x in user_answer)
                            correct_set = set(str(x) for x in question['answer'])
                            is_correct = user_set == correct_set

                    elif question['type'] == 'fill_in_blank':
                        # 填空题比较（考虑多个空的情况）
                        if isinstance(question['answer'], list):
                            if isinstance(user_answer, list) and len(user_answer) == len(question['answer']):
                                is_correct = all(
                                    str(u).lower().strip() == str(c).lower().strip()
                                    for u, c in zip(user_answer, question['answer'])
                                )
                        else:
                            # 单个答案的情况
                            if isinstance(user_answer, list):
                                user_answer = user_answer[0] if user_answer else ''
                            is_correct = str(user_answer).lower().strip() == str(question['answer']).lower().strip()

                    elif question['type'] == 'true_false':
                        # 判断题比较
                        is_correct = str(user_answer).lower() == str(question['answer']).lower()

                    # 如果正确，加分
                    if is_correct:
                        question_score = section['score_per_question']
                        score += question_score
                
                # 主观题需要人工评分，暂时不给分
                else:
                    question_score = 0
                
                # 记录每道题的得分和反馈
                question_scores.append(question_score)
                question_feedback.append('')
                question_index += 1

        # 设置总分和题目得分
        student_answer.score = score
        student_answer.question_scores = json.dumps(question_scores)
        student_answer.question_feedback = json.dumps(question_feedback)
        
        current_app.logger.info(f"保存学生答案: student_id={student_id}, assessment_id={assessment_id}, score={score}")
        
        # 保存到数据库
        db.session.add(student_answer)
        db.session.commit()
        
        current_app.logger.info(f"学生答案保存成功: submission_id={student_answer.id}")
        
        response = jsonify({
            'status': 'success',
            'message': 'Assessment submitted successfully',
            'submission_id': student_answer.id,
            'submitted_at': student_answer.submitted_at.isoformat(),
            'score': student_answer.score,
            'total_score': assessment.total_score,
            'question_scores': question_scores
        })
    except Exception as e:
        current_app.logger.error(f"提交评估失败: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        
        db.session.rollback()
        
        response = jsonify({
            'status': 'error',
            'message': f'Failed to submit assessment: {str(e)}'
        })
    
    # 添加CORS头
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    
    return response

@learning_bp.route('/submissions/<int:submission_id>/grade', methods=['POST'])
# @jwt_required()  # 暂时禁用JWT认证要求
def grade_submission(submission_id):
    """评分提交"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 获取评分数据
        score = data.get('score')
        feedback = data.get('feedback')
        question_scores = data.get('question_scores')
        question_feedback = data.get('question_feedback')
        grader_id = data.get('grader_id')
        
        # 查找提交记录
        submission = StudentAnswer.query.get(submission_id)
        if not submission:
            return jsonify({'error': '找不到提交记录'}), 404
        
        # 更新评分信息
        submission.score = score
        submission.feedback = feedback
        submission.question_scores = json.dumps(question_scores) if isinstance(question_scores, list) else question_scores
        submission.question_feedback = json.dumps(question_feedback) if isinstance(question_feedback, list) else question_feedback
        submission.grader_id = grader_id
        submission.graded_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '评分已保存',
            'submission_id': submission_id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'评分失败: {str(e)}'}), 500

@learning_bp.route('/submissions/<int:submission_id>/ai-grade-question', methods=['POST'])
# @jwt_required()  # 暂时禁用JWT认证要求
@api_error_handler
def ai_grade_question(submission_id):
    """使用AI评分单个题目"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        question_index = data.get('question_index')
        question_data = data.get('question_data')
        
        if question_index is None or not question_data:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 查找提交记录
        submission = StudentAnswer.query.get(submission_id)
        if not submission:
            return jsonify({'error': '找不到提交记录'}), 404
            
        # 获取题目和学生答案
        question = question_data.get('question')
        student_answer = question_data.get('student_answer')
        max_score = question_data.get('max_score', 10)  # 默认10分
        
        # 构建AI评分提示
        prompt = f"""
        你是一位专业的教育评分助手，请根据以下信息为学生的答案打分：
        
        题目：{question.get('stem', '')}
        题型：{question.get('section_type', '简答题')}
        满分：{max_score}分
        
        参考答案：{question.get('reference_answer') or question.get('answer') or '未提供参考答案'}
        
        学生答案：{student_answer}
        
        请根据学生答案与参考答案的匹配度、准确性、完整性和表达清晰度进行评分。
        分数应为整数或0.5的倍数，最高分为{max_score}分。
        
        请以JSON格式返回评分结果，格式如下：
        {{
          "score": 分数值(数字),
          "feedback": "评语"
        }}
        
        只返回JSON格式，不要有其他解释。
        """
        
        # 调用AI API进行评分
        api_key, api_base, model_name = get_api_config()
        
        if not api_key:
            return jsonify({'error': 'API密钥未配置'}), 500
        
        # 设置API客户端
        if api_base:
            client = openai.OpenAI(api_key=api_key, base_url=api_base)
        else:
            client = openai.OpenAI(api_key=api_key)
        
        # 调用AI API
        response = client.chat.completions.create(
            model=model_name or "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位专业的教育评分助手，根据题目和参考答案为学生答案打分。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # 提取AI响应
        ai_response = response.choices[0].message.content.strip()
        
        # 解析JSON响应
        try:
            # 使用正则表达式找到JSON部分
            json_match = re.search(r'({[\s\S]*})', ai_response)
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
            else:
                # 尝试直接解析整个响应
                result = json.loads(ai_response)
                
            # 确保分数在有效范围内
            score = result.get('score', 0)
            if score < 0:
                score = 0
            elif score > max_score:
                score = max_score
                
            # 四舍五入到最接近的0.5
            score = round(score * 2) / 2
            
            return jsonify({
                'status': 'success',
                'score': score,
                'feedback': result.get('feedback', '')
            })
            
        except (json.JSONDecodeError, ValueError) as e:
            current_app.logger.error(f"AI响应解析错误: {str(e)}, 响应: {ai_response}")
            return jsonify({
                'error': '无法解析AI响应',
                'raw_response': ai_response
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"AI评分错误: {str(e)}")
        return jsonify({'error': f'AI评分失败: {str(e)}'}), 500

@learning_bp.route('/submissions/<int:submission_id>/ai-grade-all', methods=['POST'])
# @jwt_required()  # 暂时禁用JWT认证要求
@api_error_handler
def ai_grade_all_subjective(submission_id):
    """使用AI评分所有主观题"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        questions_data = data.get('questions_data')
        
        if not questions_data or not isinstance(questions_data, list):
            return jsonify({'error': '缺少必要参数或格式错误'}), 400
        
        # 查找提交记录
        submission = StudentAnswer.query.get(submission_id)
        if not submission:
            return jsonify({'error': '找不到提交记录'}), 404
            
        # 获取当前的分数和反馈
        try:
            current_scores = json.loads(submission.question_scores) if submission.question_scores else []
            current_feedback = json.loads(submission.question_feedback) if submission.question_feedback else []
        except:
            current_scores = []
            current_feedback = []
            
        # 确保分数和反馈数组足够长
        while len(current_scores) < len(questions_data):
            current_scores.append(0)
        while len(current_feedback) < len(questions_data):
            current_feedback.append("")
            
        # 获取API配置
        api_key, api_base, model_name = get_api_config()
        
        if not api_key:
            return jsonify({'error': 'API密钥未配置'}), 500
        
        # 设置API客户端
        if api_base:
            client = openai.OpenAI(api_key=api_key, base_url=api_base)
        else:
            client = openai.OpenAI(api_key=api_key)
            
        # 对每个主观题进行评分
        for question_data in questions_data:
            index = question_data.get('index')
            question = question_data.get('question')
            student_answer = question_data.get('student_answer')
            max_score = question_data.get('max_score', 10)
            
            # 构建AI评分提示
            prompt = f"""
            你是一位专业的教育评分助手，请根据以下信息为学生的答案打分：
            
            题目：{question.get('stem', '')}
            题型：{question.get('section_type', '简答题')}
            满分：{max_score}分
            
            参考答案：{question.get('reference_answer') or question.get('answer') or '未提供参考答案'}
            
            学生答案：{student_answer}
            
            请根据学生答案与参考答案的匹配度、准确性、完整性和表达清晰度进行评分。
            分数应为整数或0.5的倍数，最高分为{max_score}分。
            
            请以JSON格式返回评分结果，格式如下：
            {{
              "score": 分数值(数字),
              "feedback": "评语"
            }}
            
            只返回JSON格式，不要有其他解释。
            """
            
            # 调用AI API
            response = client.chat.completions.create(
                model=model_name or "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一位专业的教育评分助手，根据题目和参考答案为学生答案打分。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # 提取AI响应
            ai_response = response.choices[0].message.content.strip()
            
            # 解析JSON响应
            try:
                # 使用正则表达式找到JSON部分
                json_match = re.search(r'({[\s\S]*})', ai_response)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                else:
                    # 尝试直接解析整个响应
                    result = json.loads(ai_response)
                    
                # 确保分数在有效范围内
                score = result.get('score', 0)
                if score < 0:
                    score = 0
                elif score > max_score:
                    score = max_score
                    
                # 四舍五入到最接近的0.5
                score = round(score * 2) / 2
                
                # 更新分数和反馈
                current_scores[index] = score
                current_feedback[index] = result.get('feedback', '')
                
            except (json.JSONDecodeError, ValueError) as e:
                current_app.logger.error(f"AI响应解析错误: {str(e)}, 响应: {ai_response}")
                # 跳过这个问题，继续处理下一个
                continue
                
        # 计算总分
        total_score = sum(filter(None, current_scores))
        # 四舍五入到最接近的0.5
        total_score = round(total_score * 2) / 2
                
        return jsonify({
            'status': 'success',
            'question_scores': current_scores,
            'question_feedback': current_feedback,
            'total_score': total_score
        })
            
    except Exception as e:
        current_app.logger.error(f"AI批量评分错误: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'AI批量评分失败: {str(e)}'}), 500

@learning_bp.route('/submissions/<int:submission_id>', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_submission(submission_id):
    """获取单个提交记录"""
    # 验证提交是否存在
    submission = StudentAnswer.query.get(submission_id)
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    # 获取学生信息
    student = User.query.get(submission.student_id)
    student_name = student.full_name if student else f"Student {submission.student_id}"
    
    # 获取评估信息
    assessment = Assessment.query.get(submission.assessment_id)
    
    # 准备响应数据
    submission_data = submission.to_dict()
    submission_data['student_name'] = student_name
    
    # 如果有评估信息，添加到响应中
    if assessment:
        submission_data['assessment'] = {
            'id': assessment.id,
            'title': assessment.title,
            'description': assessment.description,
            'total_score': assessment.total_score,
            'questions': assessment.get_questions()
        }
    
    return jsonify(submission_data)

@learning_bp.route('/courses/<int:course_id>/assessments', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_course_assessments(course_id):
    """获取课程的所有评估"""
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 获取课程的所有评估
    assessments = Assessment.query.filter_by(course_id=course_id).all()
    
    # 准备响应数据
    assessments_data = []
    for assessment in assessments:
        assessment_dict = assessment.to_dict()
        # 添加提交次数信息
        assessment_dict['submission_count'] = StudentAnswer.query.filter_by(assessment_id=assessment.id).count()
        assessments_data.append(assessment_dict)
    
    return jsonify({
        'assessments': assessments_data,
        'total': len(assessments_data)
    })

# 删除课程章节
@learning_bp.route('/courses/<int:course_id>/chapters', methods=['DELETE'])
def delete_course_chapters(course_id):
    """删除课程章节"""
    current_app.logger.info(f"删除课程章节: 课程ID = {course_id}")
    
    # 查找课程
    course = Course.query.get(course_id)
    if not course:
        current_app.logger.error(f"课程不存在: ID = {course_id}")
        return jsonify({'error': 'Course not found'}), 404
    
    # 获取force参数
    force = request.args.get('force', 'false').lower() == 'true'
    
    # 章节文件路径
    chapters_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'chapters')
    course_chapters_folder = os.path.join(chapters_folder, str(course_id))
    chapters_file_path = os.path.join(course_chapters_folder, 'chapters.json')
    current_app.logger.info(f"章节文件路径: {chapters_file_path}")
    
    # 如果章节文件存在，则删除
    if os.path.exists(chapters_file_path):
        try:
            # 删除文件
            os.remove(chapters_file_path)
            current_app.logger.info(f"成功删除章节文件: {chapters_file_path}")
            return jsonify({
                'status': 'success',
                'message': 'Chapters deleted successfully'
            })
        except Exception as e:
            current_app.logger.error(f"删除章节文件失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'删除章节文件失败: {str(e)}'
            }), 500
    else:
        # 如果是强制删除，则返回成功
        if force:
            current_app.logger.info(f"章节文件不存在，但强制参数为true，返回成功")
            return jsonify({
                'status': 'success',
                'message': 'Chapters file does not exist, nothing to delete'
            })
        else:
            current_app.logger.warning(f"章节文件不存在: {chapters_file_path}")
            return jsonify({
                'status': 'warning',
                'message': 'Chapters file does not exist'
            }), 404

# 修改生成章节函数，使其能使用课程名称和描述作为输入
@learning_bp.route('/courses/<int:course_id>/generate-chapters', methods=['OPTIONS', 'POST'])
def generate_course_chapters(course_id):
    """使用AI生成课程章节"""
    current_app.logger.info(f"收到课程章节生成请求: 课程ID = {course_id}, 方法 = {request.method}")
    
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Cache-Control')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')
        current_app.logger.info("处理OPTIONS请求")
        return response
    
    # 查找课程
    course = Course.query.get(course_id)
    if not course:
        current_app.logger.error(f"课程不存在: ID = {course_id}")
        return jsonify({'error': 'Course not found'}), 404
    
    # 获取请求数据
    data = request.json or {}
    course_name = data.get('course_name') or course.name
    description = data.get('description') or course.description or ''
    
    current_app.logger.info(f"课程名称: {course_name}, 描述长度: {len(description)}")
    
    # 检查章节文件夹是否存在，不存在则创建
    chapters_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'chapters')
    os.makedirs(chapters_folder, exist_ok=True)
    current_app.logger.info(f"章节文件夹路径: {chapters_folder}")
    
    # 检查课程章节文件夹是否存在，不存在则创建
    course_chapters_folder = os.path.join(chapters_folder, str(course_id))
    os.makedirs(course_chapters_folder, exist_ok=True)
    current_app.logger.info(f"课程章节文件夹路径: {course_chapters_folder}")
    
    # 章节文件路径
    chapters_file_path = os.path.join(course_chapters_folder, 'chapters.json')
    current_app.logger.info(f"章节文件路径: {chapters_file_path}")
    
    try:
        current_app.logger.info(f"开始生成章节数据")
        
        # 根据课程名称和描述进行定制
        course_type = "通用"
        
        # 简单的关键词匹配，用于确定课程类型
        if any(keyword in course_name.lower() or (description and keyword in description.lower()) for keyword in ["python", "编程", "程序", "代码", "开发"]):
            course_type = "编程"
        elif any(keyword in course_name.lower() or (description and keyword in description.lower()) for keyword in ["math", "数学", "物理", "chemistry", "化学"]):
            course_type = "理科"
        elif any(keyword in course_name.lower() or (description and keyword in description.lower()) for keyword in ["历史", "文学", "哲学", "艺术", "音乐"]):
            course_type = "文科"
        elif any(keyword in course_name.lower() or (description and keyword in description.lower()) for keyword in ["人工智能", "机器学习", "神经网络", "深度学习", "ai"]):
            course_type = "人工智能"
        
        current_app.logger.info(f"检测到课程类型: {course_type}")
        
        # 根据课程类型选择不同的章节模板
        if course_type == "编程":
            # 编程类课程章节
            chapters_data = [
                {
                    "title": f"第一章：{course_name}基础入门",
                    "duration": 90,
                    "sections": [
                        {
                            "title": "1.1 开发环境搭建",
                            "duration": 30,
                            "content": "学习如何配置开发环境，安装所需工具和库"
                        },
                        {
                            "title": "1.2 基本语法讲解",
                            "duration": 30,
                            "content": "详细讲解编程语言的基础语法和结构"
                        },
                        {
                            "title": "1.3 第一个程序实例",
                            "duration": 30,
                            "content": "编写并运行第一个简单程序，了解基本工作流程"
                        }
                    ]
                },
                {
                    "title": "第二章：数据类型与结构",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "2.1 基本数据类型",
                            "duration": 40,
                            "content": "学习语言中的基本数据类型及其操作方法"
                        },
                        {
                            "title": "2.2 复合数据结构",
                            "duration": 40,
                            "content": "掌握数组、列表、字典等复合数据结构的使用"
                        },
                        {
                            "title": "2.3 数据操作实践",
                            "duration": 40,
                            "content": "通过实例练习各种数据类型和结构的操作"
                        }
                    ]
                },
                {
                    "title": "第三章：流程控制",
                    "duration": 100,
                    "sections": [
                        {
                            "title": "3.1 条件语句",
                            "duration": 30,
                            "content": "学习if-else等条件语句的语法和应用场景"
                        },
                        {
                            "title": "3.2 循环结构",
                            "duration": 40,
                            "content": "掌握for、while等循环结构的使用方法"
                        },
                        {
                            "title": "3.3 控制流实例",
                            "duration": 30,
                            "content": "通过实际案例练习流程控制语句的应用"
                        }
                    ]
                },
                {
                    "title": "第四章：函数编程",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "4.1 函数定义与调用",
                            "duration": 30,
                            "content": "学习如何定义和调用函数，理解参数传递机制"
                        },
                        {
                            "title": "4.2 函数高级特性",
                            "duration": 40,
                            "content": "探讨匿名函数、闭包、装饰器等高级函数特性"
                        },
                        {
                            "title": "4.3 模块化与包管理",
                            "duration": 50,
                            "content": "了解如何组织代码为模块，以及使用包管理工具"
                        }
                    ]
                },
                {
                    "title": "第五章：面向对象编程",
                    "duration": 150,
                    "sections": [
                        {
                            "title": "5.1 类与对象基础",
                            "duration": 50,
                            "content": "理解面向对象的核心概念，学习类的定义和实例化"
                        },
                        {
                            "title": "5.2 继承与多态",
                            "duration": 50,
                            "content": "掌握继承、多态等面向对象高级特性"
                        },
                        {
                            "title": "5.3 设计模式入门",
                            "duration": 50,
                            "content": "了解常见设计模式及其在面向对象编程中的应用"
                        }
                    ]
                },
                {
                    "title": "第六章：文件与异常处理",
                    "duration": 90,
                    "sections": [
                        {
                            "title": "6.1 文件读写操作",
                            "duration": 30,
                            "content": "学习如何进行文件的读写、创建和删除等基本操作"
                        },
                        {
                            "title": "6.2 异常处理机制",
                            "duration": 30,
                            "content": "掌握try-except异常处理语法和最佳实践"
                        },
                        {
                            "title": "6.3 日志记录技术",
                            "duration": 30,
                            "content": "了解如何使用日志模块记录程序运行状态"
                        }
                    ]
                },
                {
                    "title": "第七章：数据库交互",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "7.1 数据库基础",
                            "duration": 40,
                            "content": "了解关系型数据库和NoSQL数据库的基本概念"
                        },
                        {
                            "title": "7.2 SQL语句与ORM",
                            "duration": 40,
                            "content": "学习基本SQL语句和使用ORM框架简化数据库操作"
                        },
                        {
                            "title": "7.3 数据库应用开发",
                            "duration": 40,
                            "content": "实践数据库在实际应用中的集成和使用"
                        }
                    ]
                },
                {
                    "title": "第八章：项目实战",
                    "duration": 180,
                    "sections": [
                        {
                            "title": "8.1 需求分析与设计",
                            "duration": 60,
                            "content": "学习如何分析项目需求并进行系统设计"
                        },
                        {
                            "title": "8.2 项目开发实践",
                            "duration": 60,
                            "content": "按照设计文档实现项目功能，应用所学知识"
                        },
                        {
                            "title": "8.3 测试与部署",
                            "duration": 60,
                            "content": "掌握基本的测试方法和项目部署技术"
                        }
                    ]
                }
            ]
        elif course_type == "人工智能":
            # 人工智能课程章节
            chapters_data = [
                {
                    "title": "第一章：人工智能基础",
                    "duration": 90,
                    "sections": [
                        {
                            "title": "1.1 人工智能概述与历史",
                            "duration": 30,
                            "content": "介绍人工智能的发展历程、关键里程碑和基本概念"
                        },
                        {
                            "title": "1.2 机器学习基础理论",
                            "duration": 30,
                            "content": "讲解机器学习的核心原理、类型和常见算法"
                        },
                        {
                            "title": "1.3 神经网络入门",
                            "duration": 30,
                            "content": "介绍神经网络的基本结构、工作原理和应用场景"
                        }
                    ]
                },
                {
                    "title": "第二章：数学基础",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "2.1 线性代数基础",
                            "duration": 40,
                            "content": "回顾AI所需的向量、矩阵运算和特征分解等知识"
                        },
                        {
                            "title": "2.2 概率与统计",
                            "duration": 40,
                            "content": "学习概率论、贝叶斯理论和假设检验等统计知识"
                        },
                        {
                            "title": "2.3 最优化方法",
                            "duration": 40,
                            "content": "了解梯度下降、牛顿法等常用优化算法"
                        }
                    ]
                },
                {
                    "title": "第三章：监督学习",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "3.1 线性回归与逻辑回归",
                            "duration": 40,
                            "content": "详细讲解回归模型的原理和实现方法"
                        },
                        {
                            "title": "3.2 决策树与随机森林",
                            "duration": 40,
                            "content": "学习基于树的模型及其集成方法"
                        },
                        {
                            "title": "3.3 支持向量机",
                            "duration": 40,
                            "content": "掌握SVM的数学原理和核技巧"
                        }
                    ]
                },
                {
                    "title": "第四章：深度学习基础",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "4.1 前馈神经网络",
                            "duration": 40,
                            "content": "学习多层感知器的结构、前向传播和反向传播算法"
                        },
                        {
                            "title": "4.2 深度网络训练技巧",
                            "duration": 40,
                            "content": "掌握正则化、批量归一化等提升模型性能的方法"
                        },
                        {
                            "title": "4.3 深度学习框架入门",
                            "duration": 40,
                            "content": "了解主流深度学习框架的基本使用方法"
                        }
                    ]
                },
                {
                    "title": "第五章：计算机视觉",
                    "duration": 150,
                    "sections": [
                        {
                            "title": "5.1 卷积神经网络(CNN)",
                            "duration": 50,
                            "content": "深入学习CNN的结构、原理和视觉应用"
                        },
                        {
                            "title": "5.2 图像分类与检测",
                            "duration": 50,
                            "content": "掌握目标检测、图像分类等基本视觉任务"
                        },
                        {
                            "title": "5.3 图像生成与风格迁移",
                            "duration": 50,
                            "content": "探索GAN和风格迁移等高级视觉生成技术"
                        }
                    ]
                },
                {
                    "title": "第六章：自然语言处理",
                    "duration": 150,
                    "sections": [
                        {
                            "title": "6.1 循环神经网络与LSTM",
                            "duration": 50,
                            "content": "学习RNN、LSTM等序列建模的基本网络结构"
                        },
                        {
                            "title": "6.2 注意力机制与Transformer",
                            "duration": 50,
                            "content": "深入研究Transformer架构及其工作原理"
                        },
                        {
                            "title": "6.3 大型语言模型",
                            "duration": 50,
                            "content": "了解BERT、GPT等预训练语言模型的特点"
                        }
                    ]
                },
                {
                    "title": "第七章：强化学习",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "7.1 马尔可夫决策过程",
                            "duration": 40,
                            "content": "了解强化学习的数学基础和理论框架"
                        },
                        {
                            "title": "7.2 基于价值的方法",
                            "duration": 40,
                            "content": "学习Q-learning、DQN等基于价值的强化学习算法"
                        },
                        {
                            "title": "7.3 策略梯度与Actor-Critic",
                            "duration": 40,
                            "content": "掌握基于策略的强化学习方法及其应用"
                        }
                    ]
                },
                {
                    "title": "第八章：AI伦理与实践",
                    "duration": 90,
                    "sections": [
                        {
                            "title": "8.1 AI系统部署与优化",
                            "duration": 30,
                            "content": "学习将AI模型部署到生产环境并进行优化"
                        },
                        {
                            "title": "8.2 AI伦理与公平性",
                            "duration": 30,
                            "content": "探讨AI应用中的伦理问题、偏见与公平性"
                        },
                        {
                            "title": "8.3 AI前沿与未来展望",
                            "duration": 30,
                            "content": "了解AI领域最新研究进展和未来发展方向"
                        }
                    ]
                }
            ]
        else:
            # 通用课程章节
            chapters_data = [
                {
                    "title": f"第一章：{course_name}概述",
                    "duration": 60,
                    "sections": [
                        {
                            "title": "1.1 课程导引与学习目标",
                            "duration": 20,
                            "content": "介绍课程的总体框架、学习目标和预期收获"
                        },
                        {
                            "title": "1.2 核心概念预览",
                            "duration": 20,
                            "content": "概述课程中将要学习的关键概念和重要理论"
                        },
                        {
                            "title": "1.3 学习方法与资源",
                            "duration": 20,
                            "content": "分享有效的学习策略、方法和推荐的学习资源"
                        }
                    ]
                },
                {
                    "title": "第二章：学科基础知识",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "2.1 基本概念与术语",
                            "duration": 40,
                            "content": "系统介绍学科中的基础概念和专业术语"
                        },
                        {
                            "title": "2.2 理论框架与模型",
                            "duration": 40,
                            "content": "讲解该领域的主要理论框架和分析模型"
                        },
                        {
                            "title": "2.3 发展历史与脉络",
                            "duration": 40,
                            "content": "回顾学科的历史发展脉络和重要里程碑"
                        }
                    ]
                },
                {
                    "title": "第三章：核心原理讲解",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "3.1 基本原则与规律",
                            "duration": 40,
                            "content": "详细讲解学科中的基本原则和核心规律"
                        },
                        {
                            "title": "3.2 方法论与工作流程",
                            "duration": 40,
                            "content": "介绍该领域常用的研究方法和标准流程"
                        },
                        {
                            "title": "3.3 案例分析与应用",
                            "duration": 40,
                            "content": "通过案例分析加深对核心原理的理解"
                        }
                    ]
                },
                {
                    "title": "第四章：技术与工具应用",
                    "duration": 90,
                    "sections": [
                        {
                            "title": "4.1 常用工具介绍",
                            "duration": 30,
                            "content": "介绍本领域常用的专业工具和技术平台"
                        },
                        {
                            "title": "4.2 技术操作实践",
                            "duration": 30,
                            "content": "通过实践学习各种技术的具体操作方法"
                        },
                        {
                            "title": "4.3 数据收集与分析",
                            "duration": 30,
                            "content": "学习相关数据的收集、处理和分析方法"
                        }
                    ]
                },
                {
                    "title": "第五章：专业技能培养",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "5.1 专业能力训练",
                            "duration": 40,
                            "content": "系统训练本领域所需的核心专业能力"
                        },
                        {
                            "title": "5.2 问题解决策略",
                            "duration": 40,
                            "content": "学习解决本领域典型问题的方法和策略"
                        },
                        {
                            "title": "5.3 实践项目指导",
                            "duration": 40,
                            "content": "通过实际项目练习应用所学知识和技能"
                        }
                    ]
                },
                {
                    "title": "第六章：行业应用与实践",
                    "duration": 120,
                    "sections": [
                        {
                            "title": "6.1 行业现状分析",
                            "duration": 40,
                            "content": "分析本学科在各行业中的应用现状和特点"
                        },
                        {
                            "title": "6.2 实际案例研究",
                            "duration": 40,
                            "content": "研究行业中的典型成功案例和失败教训"
                        },
                        {
                            "title": "6.3 创新应用探索",
                            "duration": 40,
                            "content": "探讨本学科知识在新兴领域的创新应用"
                        }
                    ]
                },
                {
                    "title": "第七章：前沿研究与发展",
                    "duration": 90,
                    "sections": [
                        {
                            "title": "7.1 学术前沿综述",
                            "duration": 30,
                            "content": "综述本领域当前的学术研究前沿和热点问题"
                        },
                        {
                            "title": "7.2 新技术与新方法",
                            "duration": 30,
                            "content": "介绍领域内新兴的技术手段和研究方法"
                        },
                        {
                            "title": "7.3 跨学科融合趋势",
                            "duration": 30,
                            "content": "探讨本学科与其他学科的交叉融合趋势"
                        }
                    ]
                },
                {
                    "title": "第八章：课程总结与展望",
                    "duration": 60,
                    "sections": [
                        {
                            "title": "8.1 知识体系回顾",
                            "duration": 20,
                            "content": "系统回顾课程所学的全部知识体系"
                        },
                        {
                            "title": "8.2 实践应用指导",
                            "duration": 20,
                            "content": "指导学生如何将所学知识应用到实际工作中"
                        },
                        {
                            "title": "8.3 未来学习路径",
                            "duration": 20,
                            "content": "建议进一步学习的方向和资源获取渠道"
                        }
                    ]
                }
            ]
        
        # 保存到文件
        current_app.logger.info(f"保存章节数据到文件")
        with open(chapters_file_path, 'w', encoding='utf-8') as f:
            json.dump(chapters_data, f, ensure_ascii=False, indent=2)
        
        current_app.logger.info(f"章节生成成功，返回数据")
        return jsonify({
            'status': 'success',
            'message': 'Chapters generated successfully',
            'chapters': chapters_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Generate chapters error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'生成章节失败: {str(e)}'
        }), 500

# 获取课程章节
@learning_bp.route('/courses/<int:course_id>/chapters', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_course_chapters(course_id):
    """获取课程章节"""
    current_app.logger.info(f"获取课程章节: 课程ID = {course_id}")
    
    # 查找课程
    course = Course.query.get(course_id)
    if not course:
        current_app.logger.error(f"课程不存在: ID = {course_id}")
        return jsonify({'error': 'Course not found'}), 404
    
    # 章节文件路径
    chapters_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'chapters')
    course_chapters_folder = os.path.join(chapters_folder, str(course_id))
    chapters_file_path = os.path.join(course_chapters_folder, 'chapters.json')
    current_app.logger.info(f"章节文件路径: {chapters_file_path}")
    
    # 如果章节文件不存在，则返回空列表
    if not os.path.exists(chapters_file_path):
        current_app.logger.info(f"章节文件不存在，返回空列表")
        return jsonify({
            'status': 'success',
            'chapters': []
        })
    
    # 读取章节文件
    try:
        current_app.logger.info(f"读取章节文件")
        with open(chapters_file_path, 'r', encoding='utf-8') as f:
            chapters_data = json.load(f)
        
        current_app.logger.info(f"返回章节数据: {len(chapters_data)} 个章节")
        return jsonify({
            'status': 'success',
            'chapters': chapters_data
        })
    except Exception as e:
        current_app.logger.error(f"Get chapters error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取章节失败: {str(e)}'
        }), 500

# 保存课程章节
@learning_bp.route('/courses/<int:course_id>/chapters', methods=['POST'])
def save_course_chapters(course_id):
    """保存课程章节"""
    current_app.logger.info(f"保存课程章节: 课程ID = {course_id}")
    
    # 查找课程
    course = Course.query.get(course_id)
    if not course:
        current_app.logger.error(f"课程不存在: ID = {course_id}")
        return jsonify({'error': 'Course not found'}), 404
    
    # 获取请求数据
    data = request.json
    if not data or 'chapters' not in data:
        current_app.logger.error(f"请求数据无效，缺少chapters字段")
        return jsonify({'error': 'Invalid request data'}), 400
    
    # 验证章节数据
    chapters = data['chapters']
    if not isinstance(chapters, list):
        current_app.logger.error(f"章节数据不是有效的列表")
        return jsonify({'error': 'Chapters must be a list'}), 400
    
    # 检查章节文件夹是否存在，不存在则创建
    chapters_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'chapters')
    os.makedirs(chapters_folder, exist_ok=True)
    
    # 检查课程章节文件夹是否存在，不存在则创建
    course_chapters_folder = os.path.join(chapters_folder, str(course_id))
    os.makedirs(course_chapters_folder, exist_ok=True)
    
    # 章节文件路径
    chapters_file_path = os.path.join(course_chapters_folder, 'chapters.json')
    
    try:
        # 保存章节到文件
        with open(chapters_file_path, 'w', encoding='utf-8') as f:
            json.dump(chapters, f, ensure_ascii=False, indent=2)
        
        current_app.logger.info(f"章节保存成功: 课程ID = {course_id}, 章节数量 = {len(chapters)}")
        return jsonify({
            'status': 'success',
            'message': 'Chapters saved successfully'
        })
    except Exception as e:
        current_app.logger.error(f"保存章节失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'保存章节失败: {str(e)}'
        }), 500

# 测试API端点
@learning_bp.route('/test-api', methods=['GET', 'POST', 'OPTIONS'])
def test_api():
    """测试API端点"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    return jsonify({
        'status': 'success',
        'message': 'API测试成功',
        'method': request.method
    })

def generate_assessment_with_ai(course_name, course_description, extra_info='', assessment_type='quiz', difficulty='medium'):
    """使用AI生成评估内容"""
    # 加载环境变量
    load_dotenv()
    
    # 尝试获取API配置
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    api_base = os.getenv("LLM_API_BASE") or os.getenv("OPENAI_API_BASE") or os.getenv("DEEPSEEK_API_BASE")
    model_name = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or os.getenv("DEEPSEEK_MODEL") or "gpt-3.5-turbo"
    
    if not api_key:
        raise ValueError("API密钥未配置，请在环境变量中设置LLM_API_KEY或OPENAI_API_KEY")
    
    # 设置API客户端
    if api_base:
        client = openai.OpenAI(api_key=api_key, base_url=api_base)
    else:
        client = openai.OpenAI(api_key=api_key)
    
    current_app.logger.info(f"使用模型 {model_name} 生成评估内容")
    
    # 根据评估类型调整题目数量
    question_count = 10  # 默认值
    if assessment_type == "quiz":
        question_count = 10
    elif assessment_type == "exam":
        question_count = 20
    elif assessment_type == "homework":
        question_count = 8
    
    # 准备提示词
    prompt = f"""
    请根据以下课程信息生成一个完整的{assessment_type}（{question_count}题左右）：
    
    课程名称: {course_name}
    课程描述: {course_description}
    难度级别: {difficulty}
    额外要求: {extra_info}
    
    请按照以下JSON格式返回评估内容，确保格式正确：
    {{
      "title": "评估标题",
      "description": "评估描述",
      "type": "{assessment_type}",
      "total_score": 100,
      "sections": [
        {{
          "type": "multiple_choice",
          "description": "选择题部分",
          "score_per_question": 分数,
          "questions": [
            {{
              "id": 1,
              "stem": "题干内容",
              "type": "multiple_choice",
              "score": 分数,
              "difficulty": "{difficulty}",
              "options": ["A. 选项内容", "B. 选项内容", "C. 选项内容", "D. 选项内容"],
              "answer": "C",
              "explanation": "答案解析"
            }}
            // 更多题目...
          ]
        }},
        // 可以有多个sections，如multiple_choice, fill_in_blank, short_answer等
      ]
    }}
    
    注意：
    1. 请确保生成的题目与课程内容相关，并具有适当的难度级别
    2. 选择题的选项应该使用A、B、C、D等标注，答案也要用对应的字母
    3. 每种题型的分值合理分配，总分为100分
    4. 务必确保JSON格式正确，可以直接被解析
    5. 对于选择题，answer是选项的字母（如"A"、"B"等）
    6. 对于填空题，answer可以是字符串或字符串数组（多个空）
    7. 对于简答题和论述题，提供reference_answer参考答案
    8. 根据课程内容生成真实、准确、有教育意义的题目
    
    请只返回JSON格式的评估内容，不要添加任何额外的解释或说明。
    """
    
    current_app.logger.info("发送AI请求生成评估内容")
    
    # 调用AI API生成内容
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是一个专业的教育内容创建者，擅长根据课程信息生成高质量的测验和考试题目。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        # 提取生成的内容
        ai_response = response.choices[0].message.content.strip()
        current_app.logger.info(f"AI响应内容长度: {len(ai_response)}")
        
        # 尝试解析JSON，提取其中的内容
        try:
            # 使用正则表达式找到JSON部分（从第一个{开始到最后一个}结束）
            json_match = re.search(r'({[\s\S]*})', ai_response)
            if json_match:
                json_str = json_match.group(1)
                assessment_data = json.loads(json_str)
                current_app.logger.info("成功解析AI生成的评估JSON")
                return assessment_data
            else:
                # 尝试直接解析整个响应
                assessment_data = json.loads(ai_response)
                current_app.logger.info("成功解析AI生成的评估JSON")
                return assessment_data
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON解析错误: {str(e)}")
            raise ValueError(f"无法解析AI生成的内容为有效JSON: {str(e)}")
        
    except Exception as e:
        current_app.logger.error(f"调用AI服务失败: {str(e)}")
        raise Exception(f"调用AI服务失败: {str(e)}")

@learning_bp.route('/assessments/ai-generate/<request_id>', methods=['GET', 'OPTIONS'])
@api_error_handler
def get_ai_assessment_status(request_id):
    """获取AI生成评估的状态和结果"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
    
    current_app.logger.info(f"查询AI生成评估状态: request_id={request_id}")
    
    # 查找对应的文件
    ai_assessments_dir = os.path.join(current_app.root_path, 'uploads', 'ai_assessments')
    file_path = os.path.join(ai_assessments_dir, f"assessment_{request_id}.json")
    
    if not os.path.exists(file_path):
        current_app.logger.error(f"找不到评估文件: {file_path}")
        response = jsonify({
            'status': 'error',
            'message': '找不到指定的评估请求',
            'request_id': request_id
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 404
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 判断是否已完成
        if 'assessment' in data:
            current_app.logger.info(f"评估已生成完成: request_id={request_id}")
            response = jsonify(data)
        elif 'error' in data:
            current_app.logger.info(f"评估生成失败: request_id={request_id}")
            response = jsonify(data)
        else:
            # 计算进行了多长时间
            start_time = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
            current_time = datetime.now()
            elapsed_seconds = (current_time - start_time).total_seconds()
            
            # 根据经过的时间估算进度
            progress_info = ""
            if elapsed_seconds < 30:
                progress_info = "准备模型资源中..."
            elif elapsed_seconds < 60:
                progress_info = "正在分析课程内容..."
            elif elapsed_seconds < 90:
                progress_info = "正在构思评估题目..."
            else:
                progress_info = "正在组装评估内容，即将完成..."
            
            current_app.logger.info(f"评估正在生成中: request_id={request_id}, elapsed={elapsed_seconds:.1f}秒")
            response = jsonify({
                'status': 'processing',
                'message': f'评估正在生成中，请稍后再查询',
                'progress': progress_info,
                'elapsed_seconds': int(elapsed_seconds),
                'request_id': request_id
            })
            
        # 添加CORS头
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Content-Type', 'application/json')
        return response
    
    except Exception as e:
        current_app.logger.error(f"读取评估文件失败: {str(e)}")
        response = jsonify({
            'status': 'error',
            'message': f'读取评估状态失败: {str(e)}',
            'request_id': request_id
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@learning_bp.route('/assessments/ai-file/<request_id>', methods=['GET', 'OPTIONS'])
@api_error_handler
def get_ai_assessment_file(request_id):
    """直接获取AI生成评估文件的内容"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
    
    current_app.logger.info(f"直接请求AI评估文件内容: request_id={request_id}")
    
    # 查找对应的文件
    ai_assessments_dir = os.path.join(current_app.root_path, 'uploads', 'ai_assessments')
    file_path = os.path.join(ai_assessments_dir, f"assessment_{request_id}.json")
    
    if not os.path.exists(file_path):
        current_app.logger.error(f"找不到评估文件: {file_path}")
        response = jsonify({
            'status': 'error',
            'message': '找不到指定的评估文件',
            'request_id': request_id
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 404
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 直接返回文件内容，无论处理状态如何
        current_app.logger.info(f"成功读取评估文件: request_id={request_id}")
        response = jsonify(data)
        
        # 添加CORS头
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Content-Type', 'application/json')
        return response
    
    except Exception as e:
        current_app.logger.error(f"读取评估文件失败: {str(e)}")
        response = jsonify({
            'status': 'error',
            'message': f'读取评估文件失败: {str(e)}',
            'request_id': request_id
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@learning_bp.route('/assessments/<int:assessment_id>/submissions', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_assessment_submissions(assessment_id):
    """获取评估的所有提交"""
    current_app.logger.info(f"获取评估提交: assessment_id={assessment_id}, args={request.args}")
    
    # 验证评估是否存在
    assessment = Assessment.query.get(assessment_id)
    if not assessment:
        current_app.logger.error(f"评估不存在: assessment_id={assessment_id}")
        return jsonify({'error': 'Assessment not found'}), 404
    
    # 获取查询参数
    student_id = request.args.get('student_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    graded = request.args.get('graded')
    
    current_app.logger.info(f"查询参数: student_id={student_id}, page={page}, per_page={per_page}, graded={graded}")
    
    # 构建查询
    query = StudentAnswer.query.filter_by(assessment_id=assessment_id)
    
    if student_id:
        current_app.logger.info(f"按学生ID过滤: student_id={student_id}")
        query = query.filter_by(student_id=student_id)
    
    # 根据评分状态过滤
    if graded == 'true':
        current_app.logger.info("只查询已评分的提交")
        query = query.filter(StudentAnswer.graded_at != None)
    elif graded == 'false':
        current_app.logger.info("只查询未评分的提交")
        query = query.filter(StudentAnswer.graded_at == None)
    
    try:
        # 执行分页查询
        submissions_pagination = query.paginate(page=page, per_page=per_page)
        
        current_app.logger.info(f"找到 {submissions_pagination.total} 条提交记录")
        
        # 准备响应数据
        submissions_data = []
        for submission in submissions_pagination.items:
            submission_dict = submission.to_dict()
            
            # 添加学生信息
            student = User.query.get(submission.student_id)
            if student:
                submission_dict['student_name'] = student.full_name
                submission_dict['student_username'] = student.username
                current_app.logger.info(f"添加学生信息: student_id={submission.student_id}, name={student.full_name}")
            
            submissions_data.append(submission_dict)
        
        response_data = {
            'submissions': submissions_data,
            'total': submissions_pagination.total,
            'pages': submissions_pagination.pages,
            'current_page': page
        }
        
        current_app.logger.info(f"返回 {len(submissions_data)} 条提交记录")
        
        # 添加CORS头
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        
        return response
    except Exception as e:
        current_app.logger.error(f"获取评估提交失败: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        
        # 添加CORS头
        response = jsonify({
            'error': f'Failed to get submissions: {str(e)}',
            'submissions': []
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        
        return response, 500

@learning_bp.route('/students/<int:student_id>/submissions', methods=['GET', 'OPTIONS'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_student_submissions(student_id):
    """获取学生的所有提交"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
        
    # 记录请求信息
    current_app.logger.info(f"获取学生提交记录: student_id={student_id}, args={request.args}")
    
    # 验证学生是否存在
    student = User.query.get(student_id)
    if not student:
        current_app.logger.warning(f"学生不存在: student_id={student_id}")
        response = jsonify({'error': 'Student not found'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 404
    
    # 获取查询参数
    assessment_id = request.args.get('assessment_id', type=int)
    course_id = request.args.get('course_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    graded = request.args.get('graded')
    
    current_app.logger.info(f"查询参数: assessment_id={assessment_id}, course_id={course_id}, page={page}, per_page={per_page}, graded={graded}")
    
    # 构建查询
    query = StudentAnswer.query.filter_by(student_id=student_id)
    
    if assessment_id:
        current_app.logger.info(f"按评估ID过滤: assessment_id={assessment_id}")
        query = query.filter_by(assessment_id=assessment_id)
    
    if course_id:
        # 需要联表查询
        current_app.logger.info(f"按课程ID过滤: course_id={course_id}")
        query = query.join(Assessment).filter(Assessment.course_id == course_id)
    
    # 根据评分状态过滤
    if graded == 'true':
        current_app.logger.info("只查询已评分的提交")
        query = query.filter(StudentAnswer.graded_at != None)
    elif graded == 'false':
        current_app.logger.info("只查询未评分的提交")
        query = query.filter(StudentAnswer.graded_at == None)
    
    # 按提交时间降序排序
    query = query.order_by(StudentAnswer.submitted_at.desc())
    
    try:
        # 执行分页查询
        submissions_pagination = query.paginate(page=page, per_page=per_page)
        
        current_app.logger.info(f"找到 {submissions_pagination.total} 条提交记录")
        
        # 准备响应数据
        submissions_data = []
        for submission in submissions_pagination.items:
            submission_dict = submission.to_dict()
            
            # 添加评估信息
            assessment = Assessment.query.get(submission.assessment_id)
            if assessment:
                submission_dict['assessment_title'] = assessment.title
                submission_dict['assessment_total_score'] = assessment.total_score
            
            submissions_data.append(submission_dict)
        
        response = jsonify({
            'submissions': submissions_data,
            'total': submissions_pagination.total,
            'pages': submissions_pagination.pages,
            'current_page': page
        })
    except Exception as e:
        current_app.logger.error(f"获取学生提交记录失败: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        response = jsonify({
            'error': f'Failed to get submissions: {str(e)}',
            'submissions': []
        })
    
    # 添加CORS头
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

@learning_bp.route('/assessments/<int:assessment_id>/submission-count', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_assessment_submission_count(assessment_id):
    """获取评估的提交数量"""
    # 验证评估是否存在
    assessment = Assessment.query.get(assessment_id)
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404
    
    # 计算提交数量
    count = StudentAnswer.query.filter_by(assessment_id=assessment_id).count()
    
    # 获取已评分和未评分的数量
    graded_count = StudentAnswer.query.filter_by(assessment_id=assessment_id).filter(StudentAnswer.graded_at != None).count()
    ungraded_count = count - graded_count
    
    # 返回数量信息
    response = jsonify({
        'count': count,
        'graded_count': graded_count,
        'ungraded_count': ungraded_count,
        'assessment_id': assessment_id
    })
    
    # 添加CORS头
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    return response

@learning_bp.route('/analytics/student/<int:student_id>', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_student_analytics(student_id):
    """获取单个学生的学习分析数据"""
    try:
        # 检查学生是否存在
        student = User.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
            
        # 获取学生的总体学习进度
        # 这里简化计算，实际应该基于课程完成情况计算
        student_courses = db.session.query(Course).join(
            Course.students
        ).filter(User.id == student_id).all()
        
        total_courses = len(student_courses)
        completed_courses = 0
        in_progress_courses = 0
        not_started_courses = 0
        
        # 获取学生的学习记录
        learning_records = LearningRecord.query.filter_by(student_id=student_id).all()
        
        # 按课程ID分组学习记录
        course_records = {}
        for record in learning_records:
            if record.course_id not in course_records:
                course_records[record.course_id] = []
            course_records[record.course_id].append(record)
        
        # 计算每个课程的进度
        course_progress = {}
        for course in student_courses:
            # 这里简化计算，实际应该基于完成的材料和评估来计算
            records = course_records.get(course.id, [])
            if not records:
                course_progress[course.id] = 0
                not_started_courses += 1
            else:
                # 简单计算进度：基于活动记录数量
                materials_count = db.session.query(Material).filter_by(course_id=course.id).count()
                if materials_count == 0:
                    materials_count = 1  # 避免除以零
                
                # 查看过的材料数量
                viewed_materials = len(set([r.activity_detail for r in records if r.activity_type == 'view_material']))
                progress = min(100, int((viewed_materials / materials_count) * 100))
                course_progress[course.id] = progress
                
                if progress == 100:
                    completed_courses += 1
                elif progress > 0:
                    in_progress_courses += 1
                else:
                    not_started_courses += 1
        
        # 计算总体进度
        overall_progress = 0
        if total_courses > 0:
            overall_progress = int(sum(course_progress.values()) / total_courses)
        
        # 计算本周和上周的学习时间
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        last_week_start = week_start - timedelta(days=7)
        last_week_end = week_start - timedelta(days=1)
        
        # 本周学习时间
        weekly_learning_time = db.session.query(func.sum(LearningRecord.duration)).filter(
            LearningRecord.student_id == student_id,
            LearningRecord.timestamp >= week_start,
            LearningRecord.timestamp <= week_end
        ).scalar() or 0
        
        # 上周学习时间
        previous_week_time = db.session.query(func.sum(LearningRecord.duration)).filter(
            LearningRecord.student_id == student_id,
            LearningRecord.timestamp >= last_week_start,
            LearningRecord.timestamp <= last_week_end
        ).scalar() or 0
        
        # 转换为小时
        weekly_learning_time = round(weekly_learning_time / 3600, 1)
        previous_week_time = round(previous_week_time / 3600, 1)
        
        # 获取学习趋势数据（最近7天）
        trend_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            day_learning_time = db.session.query(func.sum(LearningRecord.duration)).filter(
                LearningRecord.student_id == student_id,
                func.date(LearningRecord.timestamp) == date
            ).scalar() or 0
            
            # 转换为小时
            day_learning_time = round(day_learning_time / 3600, 1)
            
            # 格式化日期标签
            if i == 0:
                label = "今天"
            elif i == 1:
                label = "昨天"
            else:
                label = date.strftime("%m-%d")
                
            trend_data.append({
                "label": label,
                "value": day_learning_time
            })
        
        # 获取课程详情
        courses_details = []
        for course in student_courses:
            # 计算学习时间
            course_learning_time = db.session.query(func.sum(LearningRecord.duration)).filter(
                LearningRecord.student_id == student_id,
                LearningRecord.course_id == course.id
            ).scalar() or 0
            
            # 转换为小时
            course_learning_time = round(course_learning_time / 3600, 1)
            
            # 最后学习时间
            last_activity = db.session.query(LearningRecord).filter(
                LearningRecord.student_id == student_id,
                LearningRecord.course_id == course.id
            ).order_by(LearningRecord.timestamp.desc()).first()
            
            last_activity_date = last_activity.timestamp.strftime("%Y-%m-%d") if last_activity else "未学习"
            
            # 评分（基于评估成绩）
            submissions = db.session.query(AssessmentSubmission).join(
                Assessment, Assessment.id == AssessmentSubmission.assessment_id
            ).filter(
                AssessmentSubmission.student_id == student_id,
                Assessment.course_id == course.id
            ).all()
            
            score = 0
            if submissions:
                total_score = sum([s.score for s in submissions if s.score is not None])
                score = int(total_score / len(submissions))
            
            courses_details.append({
                "id": course.id,
                "name": course.name,
                "category": course.category,
                "progress": course_progress.get(course.id, 0),
                "learningTime": course_learning_time,
                "lastActivity": last_activity_date,
                "score": score
            })
        
        # 模拟知识点掌握情况数据
        # 实际应该基于评估题目的知识点标签和得分情况计算
        knowledge_points = [
            {"label": "编程基础", "value": 85},
            {"label": "数据结构", "value": 65},
            {"label": "算法设计", "value": 70},
            {"label": "数据库", "value": 90},
            {"label": "网络原理", "value": 60},
            {"label": "软件工程", "value": 75}
        ]
        
        return jsonify({
            "overallProgress": overall_progress,
            "weeklyLearningTime": weekly_learning_time,
            "previousWeekTime": previous_week_time,
            "completedCourses": completed_courses,
            "inProgressCourses": in_progress_courses,
            "notStartedCourses": not_started_courses,
            "trendData": {
                "week": trend_data,
                # 简化版本，实际应该计算月和年的数据
                "month": [{"label": f"第{i+1}周", "value": 20 + i*5} for i in range(4)],
                "year": [{"label": f"{i+1}月", "value": 15 + i*3} for i in range(6)]
            },
            "courseDetails": courses_details,
            "knowledgePoints": knowledge_points
        })
    except Exception as e:
        current_app.logger.error(f"获取学生学习分析数据失败: {str(e)}")
        return jsonify({'error': f'获取学习分析数据失败: {str(e)}'}), 500

@learning_bp.route('/analytics/course/<int:course_id>', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
@api_error_handler
def get_course_analytics(course_id):
    """获取课程的整体学习分析数据"""
    try:
        current_app.logger.info(f"获取课程学情分析数据: 课程ID = {course_id}")
        
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            current_app.logger.error(f"课程不存在: ID = {course_id}")
            return jsonify({'error': 'Course not found'}), 404
            
        # 获取课程的学生
        students = course.students if hasattr(course, 'students') else []
        current_app.logger.info(f"课程学生数量: {len(students)}")
        
        # 学生完成情况统计
        total_students = len(students)
        completed_students = 0
        in_progress_students = 0
        not_started_students = 0
        
        # 学生进度数据
        student_progress = []
        
        for student in students:
            try:
                # 获取学生在此课程的学习记录
                records = LearningRecord.query.filter_by(
                    student_id=student.id,
                    course_id=course_id
                ).all()
                
                if not records:
                    not_started_students += 1
                    progress = 0
                else:
                    # 简单计算进度：基于活动记录数量
                    materials_count = db.session.query(Material).filter_by(course_id=course_id).count()
                    if materials_count == 0:
                        materials_count = 1  # 避免除以零
                    
                    # 查看过的材料数量
                    viewed_materials = len(set([r.activity_detail for r in records if r.activity_type == 'view_material']))
                    progress = min(100, int((viewed_materials / materials_count) * 100))
                    
                    if progress == 100:
                        completed_students += 1
                    else:
                        in_progress_students += 1
                
                # 计算学习时间
                learning_time = db.session.query(func.sum(LearningRecord.duration)).filter(
                    LearningRecord.student_id == student.id,
                    LearningRecord.course_id == course_id
                ).scalar() or 0
                
                # 转换为小时
                learning_time = round(learning_time / 3600, 1)
                
                student_progress.append({
                    "id": student.id,
                    "name": student.full_name if hasattr(student, 'full_name') else f"学生{student.id}",
                    "progress": progress,
                    "learningTime": learning_time
                })
            except Exception as e:
                current_app.logger.error(f"处理学生数据时出错: 学生ID = {student.id}, 错误 = {str(e)}")
                # 继续处理下一个学生
        
        # 按进度排序
        student_progress.sort(key=lambda x: x["progress"], reverse=True)
        
        # 获取评估数据
        assessment_data = []
        try:
            # 直接查询数据库获取评估数据
            current_app.logger.info("使用直接查询获取评估数据")
            assessments = Assessment.query.filter_by(course_id=course_id).all()
            current_app.logger.info(f"课程评估数量: {len(assessments)}")
            
            for assessment in assessments:
                try:
                    # 获取提交数量 - 使用StudentAnswer而不是AssessmentSubmission
                    submissions_count = db.session.query(StudentAnswer).filter_by(
                        assessment_id=assessment.id
                    ).count()
                    
                    # 获取平均分 - 使用StudentAnswer而不是AssessmentSubmission
                    avg_score_result = db.session.query(func.avg(StudentAnswer.score)).filter(
                        StudentAnswer.assessment_id == assessment.id,
                        StudentAnswer.score != None
                    ).scalar()
                    
                    avg_score = 0
                    if avg_score_result is not None:
                        avg_score = round(float(avg_score_result), 1)
                    
                    assessment_data.append({
                        "id": assessment.id,
                        "title": assessment.title,
                        "submissionsCount": submissions_count,
                        "averageScore": avg_score
                    })
                    current_app.logger.info(f"添加评估: ID={assessment.id}, 标题={assessment.title}, 提交数={submissions_count}, 平均分={avg_score}")
                except Exception as e:
                    current_app.logger.error(f"处理评估数据时出错: 评估ID = {assessment.id}, 错误 = {str(e)}")
                    # 继续处理下一个评估
        except Exception as e:
            current_app.logger.error(f"获取评估列表时出错: {str(e)}")
        
        # 知识点掌握情况（基于评估结果）
        # 这里简化处理，实际应该基于评估题目的知识点标签和得分情况计算
        knowledge_points = [
            {"label": "编程基础", "value": 78},
            {"label": "数据结构", "value": 62},
            {"label": "算法设计", "value": 68},
            {"label": "数据库", "value": 85},
            {"label": "网络原理", "value": 55},
            {"label": "软件工程", "value": 70}
        ]
        
        response_data = {
            "totalStudents": total_students,
            "completedStudents": completed_students,
            "inProgressStudents": in_progress_students,
            "notStartedStudents": not_started_students,
            "studentProgress": student_progress,
            "assessments": assessment_data,
            "knowledgePoints": knowledge_points
        }
        
        current_app.logger.info(f"成功获取课程学情分析数据: 课程ID = {course_id}, 评估数量: {len(assessment_data)}")
        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"获取课程学习分析数据失败: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'获取学习分析数据失败: {str(e)}'}), 500

