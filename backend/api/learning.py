from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import json
from datetime import datetime
from backend.models.user import User, db
from backend.models.course import Course
from backend.models.learning import LearningRecord, ChatHistory

learning_bp = Blueprint('learning', __name__, url_prefix='/api/learning')

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

# 课程路由
@learning_bp.route('/courses', methods=['GET'])
@jwt_required()
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
    
    return jsonify({
        'courses': paginated_courses,
        'total': len(filtered_courses),
        'page': page,
        'per_page': per_page,
        'pages': (len(filtered_courses) + per_page - 1) // per_page
    })

@learning_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    # 查找课程
    course = next((c for c in courses if c['id'] == course_id), None)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # 添加章节信息
    course_data = dict(course)
    course_data['chapters'] = course_chapters.get(course_id, [])
    
    return jsonify(course_data)

@learning_bp.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 验证必要字段
    required_fields = ['name', 'description', 'category', 'difficulty']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # 创建新课程
    user_id = get_jwt_identity()
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
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    courses.append(new_course)
    
    return jsonify(new_course), 201

@learning_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    user_id = get_jwt_identity()
    
    # 模拟获取用户的课程
    # 在实际应用中，这应该从数据库查询
    my_courses = [c for c in courses if c['teacher_id'] == user_id]
    
    return jsonify({
        'courses': my_courses,
        'total': len(my_courses)
    })

