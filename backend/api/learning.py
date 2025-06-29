from flask import Blueprint, request, jsonify, current_app, make_response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from backend.models.user import User, db
from backend.models.course import Course
from backend.models.learning import LearningRecord, ChatHistory
from backend.models.material import Material

learning_bp = Blueprint('learning', __name__)

# 检查是否为教师或管理员的辅助函数
def teacher_or_admin_required():
    claims = get_jwt()
    role = claims.get('role')
    if role not in ['teacher', 'admin']:
        return jsonify({"error": "需要教师或管理员权限"}), 403
    return None

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
@learning_bp.route('/learning/courses', methods=['OPTIONS'])
def courses_options():
    return '', 200

# 获取课程列表
@learning_bp.route('/learning/courses', methods=['GET'])
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
@learning_bp.route('/learning/courses/<int:course_id>', methods=['GET'])
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
@learning_bp.route('/learning/courses', methods=['POST'])
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
@learning_bp.route('/learning/courses/<int:course_id>', methods=['PUT'])
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
@learning_bp.route('/learning/courses/<int:course_id>', methods=['DELETE'])
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
        content=f'Original filename: {original_filename}',
        course_id=course_id
    )
    
    # 添加到数据库
    db.session.add(new_material)
    db.session.commit()
    
    # 返回创建的材料
    material_dict = new_material.to_dict()
    material_dict['size'] = size_str  # 添加文件大小信息
    
    return jsonify(material_dict), 201

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
@learning_bp.route('/learning/courses/<int:course_id>/students', methods=['GET'])
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
@learning_bp.route('/learning/courses/<int:course_id>/available-students', methods=['GET'])
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
@learning_bp.route('/learning/courses/<int:course_id>/students', methods=['POST'])
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
@learning_bp.route('/learning/courses/<int:course_id>/students/<int:student_id>', methods=['DELETE'])
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

