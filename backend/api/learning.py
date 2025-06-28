from flask import Blueprint, request, jsonify, current_app, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import json
from datetime import datetime
from backend.models.user import User, db
from backend.models.course import Course
from backend.models.learning import LearningRecord, ChatHistory

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

# 模拟数据
courses = [
    {
        'id': 1,
        'name': '人工智能基础',
        'description': '介绍人工智能的基本概念和应用，包括机器学习、深度学习、自然语言处理等内容。本课程适合初学者，不需要特别的数学背景。',
        'category': '计算机科学',
        'difficulty': 'beginner',
        'teacher_id': 1,
        'teacher_name': '张教授',
        'student_count': 42,
        'material_count': 12,
        'assessment_count': 5,
        'is_public': True,
        'created_at': '2025-06-01T10:00:00',
        'updated_at': '2025-06-15T14:30:00'
    },
    {
        'id': 2,
        'name': '高等数学',
        'description': '微积分和线性代数基础，涵盖函数、极限、导数、积分等内容。',
        'category': '数学',
        'difficulty': 'intermediate',
        'teacher_id': 1,
        'teacher_name': '李教授',
        'student_count': 35,
        'material_count': 8,
        'assessment_count': 4,
        'is_public': True,
        'created_at': '2025-05-15T09:00:00',
        'updated_at': '2025-06-10T11:20:00'
    },
    {
        'id': 3,
        'name': '英语写作',
        'description': '学术英语写作技巧和方法，包括论文结构、语法、修辞等内容。',
        'category': '语言',
        'difficulty': 'advanced',
        'teacher_id': 2,
        'teacher_name': '王教授',
        'student_count': 28,
        'material_count': 6,
        'assessment_count': 3,
        'is_public': True,
        'created_at': '2025-05-20T14:00:00',
        'updated_at': '2025-06-05T16:45:00'
    }
]

# 课程章节数据
course_chapters = {
    1: [
        {
            'title': '第一章：人工智能概述',
            'duration': 60,
            'sections': [
                {'title': '1.1 什么是人工智能', 'duration': 15},
                {'title': '1.2 人工智能的历史', 'duration': 20},
                {'title': '1.3 人工智能的应用领域', 'duration': 25}
            ]
        },
        {
            'title': '第二章：机器学习基础',
            'duration': 90,
            'sections': [
                {'title': '2.1 机器学习概念', 'duration': 20},
                {'title': '2.2 监督学习', 'duration': 35},
                {'title': '2.3 无监督学习', 'duration': 35}
            ]
        }
    ]
}

# 添加OPTIONS请求处理
@learning_bp.route('/learning/courses', methods=['OPTIONS'])
def courses_options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 课程路由
@learning_bp.route('/learning/courses', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_courses():
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    search = request.args.get('search')
    
    # 过滤课程
    filtered_courses = courses
    if category:
        filtered_courses = [c for c in filtered_courses if c['category'] == category]
    if search:
        filtered_courses = [c for c in filtered_courses if search.lower() in c['name'].lower() or search.lower() in c['description'].lower()]
    
    # 分页
    start = (page - 1) * per_page
    end = start + per_page
    paginated_courses = filtered_courses[start:end]
    
    # 构建响应
    response = jsonify({
        'courses': paginated_courses,
        'total': len(filtered_courses),
        'page': page,
        'per_page': per_page,
        'pages': (len(filtered_courses) + per_page - 1) // per_page
    })
    
    # 添加CORS头
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    return response

@learning_bp.route('/learning/courses/<int:course_id>', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_course(course_id):
    # 查找课程
    course = next((c for c in courses if c['id'] == course_id), None)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 添加章节信息
    course_data = dict(course)
    course_data['chapters'] = course_chapters.get(course_id, [])
    
    return jsonify(course_data)

@learning_bp.route('/learning/courses', methods=['POST'])
# @jwt_required()  # 暂时禁用JWT认证要求
def create_course():
    print("收到创建课程请求")
    print("Content-Type:", request.content_type)
    print("请求数据:", request.get_data())
    
    # 检查是否是multipart/form-data请求
    if request.content_type and 'multipart/form-data' in request.content_type:
        print("处理multipart/form-data请求")
        data_str = request.form.get('data', '{}')
        print("表单数据:", data_str)
        try:
            data = json.loads(data_str)
            print("解析后的JSON数据:", data)
        except Exception as e:
            print("JSON解析错误:", str(e))
            data = {}
        cover_image = request.files.get('cover_image')
        print("上传的图片:", cover_image.filename if cover_image else None)
    else:
        print("处理JSON请求")
        try:
            data = request.json
            print("JSON数据:", data)
        except Exception as e:
            print("JSON解析错误:", str(e))
            data = None
        cover_image = None
    
    if not data:
        error_response = jsonify({'error': 'No data provided'})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 400
    
    # 验证必要字段
    required_fields = ['name', 'description', 'category', 'difficulty']
    for field in required_fields:
        if field not in data:
            error_response = jsonify({'error': f'Missing required field: {field}'})
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            return error_response, 400
    
    # 处理图片上传
    cover_image_path = None
    if cover_image:
        # 确保文件名安全
        import os
        from werkzeug.utils import secure_filename
        filename = secure_filename(cover_image.filename)
        # 创建上传目录
        upload_folder = os.path.join(current_app.root_path, 'uploads', 'course_covers')
        os.makedirs(upload_folder, exist_ok=True)
        # 保存文件
        file_path = os.path.join(upload_folder, filename)
        cover_image.save(file_path)
        # 设置相对路径用于访问
        cover_image_path = f'/uploads/course_covers/{filename}'
    
    # 创建新课程
    # user_id = get_jwt_identity()  # 暂时注释掉
    user_id = 1  # 使用默认ID
    new_course = {
        'id': len(courses) + 1,
        'name': data['name'],
        'description': data['description'],
        'category': data['category'],
        'difficulty': data['difficulty'],
        'teacher_id': user_id,
        'teacher_name': '当前教师',  # 实际应用中应该从数据库获取
        'student_count': 0,
        'material_count': 0,
        'assessment_count': 0,
        'is_public': data.get('is_public', True),
        'cover_image': cover_image_path,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    courses.append(new_course)
    print("课程创建成功:", new_course)
    
    # 构建响应
    response = jsonify(new_course)
    
    # 添加CORS头
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    return response, 201

@learning_bp.route('/learning/courses/<int:course_id>', methods=['PUT'])
# @jwt_required()  # 暂时禁用JWT认证要求
def update_course(course_id):
    # 查找课程
    course_index = next((i for i, c in enumerate(courses) if c['id'] == course_id), None)
    if course_index is None:
        return jsonify({'error': 'Course not found'}), 404
    
    # 检查是否是multipart/form-data请求
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = json.loads(request.form.get('data', '{}'))
        cover_image = request.files.get('cover_image')
    else:
        data = request.json
        cover_image = None
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 检查权限 - 暂时注释掉
    # user_id = get_jwt_identity()
    # claims = get_jwt()
    # role = claims.get('role')
    
    # if role != 'admin' and courses[course_index]['teacher_id'] != user_id:
    #     return jsonify({'error': 'Permission denied'}), 403
    
    # 处理图片上传
    if cover_image:
        # 确保文件名安全
        import os
        from werkzeug.utils import secure_filename
        filename = secure_filename(cover_image.filename)
        # 创建上传目录
        upload_folder = os.path.join(current_app.root_path, 'uploads', 'course_covers')
        os.makedirs(upload_folder, exist_ok=True)
        # 保存文件
        file_path = os.path.join(upload_folder, filename)
        cover_image.save(file_path)
        # 设置相对路径用于访问
        data['cover_image'] = f'/uploads/course_covers/{filename}'
    
    # 更新课程信息
    for key in ['name', 'description', 'category', 'difficulty', 'is_public', 'cover_image']:
        if key in data:
            courses[course_index][key] = data[key]
    
    # 更新时间戳
    courses[course_index]['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify(courses[course_index])

@learning_bp.route('/learning/courses/<int:course_id>', methods=['DELETE'])
# @jwt_required()  # 暂时禁用JWT认证要求
def delete_course(course_id):
    # 查找课程
    course_index = next((i for i, c in enumerate(courses) if c['id'] == course_id), None)
    if course_index is None:
        return jsonify({'error': 'Course not found'}), 404
    
    # 检查权限 - 暂时注释掉
    # user_id = get_jwt_identity()
    # claims = get_jwt()
    # role = claims.get('role')
    
    # if role != 'admin' and courses[course_index]['teacher_id'] != user_id:
    #     return jsonify({'error': 'Permission denied'}), 403
    
    # 删除课程
    deleted_course = courses.pop(course_index)
    
    return jsonify({'message': 'Course deleted successfully', 'course': deleted_course})

@learning_bp.route('/my-courses', methods=['GET'])
# @jwt_required()  # 暂时禁用JWT认证要求
def get_my_courses():
    # user_id = get_jwt_identity()  # 暂时注释掉
    user_id = 1  # 使用默认ID
    
    # 模拟获取用户的课程
    # 在实际应用中，这应该从数据库查询
    my_courses = [c for c in courses if c['teacher_id'] == user_id]
    
    return jsonify({
        'courses': my_courses,
        'total': len(my_courses)
    })

