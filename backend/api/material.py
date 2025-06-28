import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from datetime import datetime
from backend.models.material import Material, db
from backend.models.course import Course
from backend.models.user import User
from backend.extensions import db

material_bp = Blueprint('material', __name__, url_prefix='/api/material')

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """根据文件扩展名获取文件类型"""
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['pdf']:
        return 'pdf'
    elif ext in ['ppt', 'pptx']:
        return 'ppt'
    elif ext in ['doc', 'docx']:
        return 'doc'
    elif ext in ['txt']:
        return 'text'
    else:
        return 'other'

# 检查是否为教师或管理员的辅助函数
def teacher_or_admin_required():
    claims = get_jwt()
    role = claims.get('role')
    if role not in ['teacher', 'admin']:
        return jsonify({"error": "需要教师或管理员权限"}), 403
    return None

@material_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_material():
    """上传课件文件"""
    # 检查权限
    auth_check = teacher_or_admin_required()
    if auth_check:
        return auth_check
    
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
    
    # 获取课程ID
    course_id = request.form.get('course_id')
    if not course_id:
        return jsonify({'error': '缺少课程ID'}), 400
    
    # 验证课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': '课程不存在'}), 404
    
    # 检查用户是否有权限上传到此课程
    user_id = get_jwt_identity()
    if course.teacher_id != user_id:
        # 如果不是课程教师，检查是否为管理员
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': '没有权限上传到此课程'}), 403
    
    try:
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加唯一标识符避免文件名冲突
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(os.path.dirname(current_app.root_path), 'uploads', 'materials')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # 创建材料记录
        material = Material(
            title=request.form.get('title', filename),
            material_type=get_file_type(filename),
            file_path=unique_filename,
            course_id=course_id,
            content=request.form.get('description', '')
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'material': material.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@material_bp.route('/download/<int:material_id>', methods=['GET'])
@jwt_required()
def download_material(material_id):
    """下载课件文件"""
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': '材料不存在'}), 404
    
    if not material.file_path:
        return jsonify({'error': '文件不存在'}), 404
    
    # 检查用户权限（学生可以下载，教师和管理员可以下载）
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 如果是学生，检查是否已注册该课程
    if user.role == 'student':
        # 这里可以添加检查学生是否已注册该课程的逻辑
        pass
    
    try:
        file_path = os.path.join(os.path.dirname(current_app.root_path), 'uploads', 'materials', material.file_path)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=material.title)
        
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@material_bp.route('/list/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_materials(course_id):
    """获取课程的所有材料"""
    # 验证课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': '课程不存在'}), 404
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 查询材料
    materials = Material.query.filter_by(course_id=course_id)\
        .order_by(Material.order, Material.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'materials': [material.to_dict() for material in materials.items],
        'total': materials.total,
        'pages': materials.pages,
        'current_page': materials.page
    }), 200

@material_bp.route('/<int:material_id>', methods=['GET'])
@jwt_required()
def get_material(material_id):
    """获取单个材料详情"""
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': '材料不存在'}), 404
    
    return jsonify(material.to_dict()), 200

@material_bp.route('/<int:material_id>', methods=['PUT'])
@jwt_required()
def update_material(material_id):
    """更新材料信息"""
    # 检查权限
    auth_check = teacher_or_admin_required()
    if auth_check:
        return auth_check
    
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': '材料不存在'}), 404
    
    # 检查用户权限
    user_id = get_jwt_identity()
    if material.course.teacher_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': '没有权限修改此材料'}), 403
    
    data = request.json
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    # 更新材料信息
    if 'title' in data:
        material.title = data['title']
    if 'content' in data:
        material.content = data['content']
    if 'order' in data:
        material.order = data['order']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '材料更新成功',
        'material': material.to_dict()
    }), 200

@material_bp.route('/<int:material_id>', methods=['DELETE'])
@jwt_required()
def delete_material(material_id):
    """删除材料"""
    # 检查权限
    auth_check = teacher_or_admin_required()
    if auth_check:
        return auth_check
    
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': '材料不存在'}), 404
    
    # 检查用户权限
    user_id = get_jwt_identity()
    if material.course.teacher_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': '没有权限删除此材料'}), 403
    
    try:
        # 删除文件
        if material.file_path:
            file_path = os.path.join(os.path.dirname(current_app.root_path), 'uploads', 'materials', material.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # 删除数据库记录
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '材料删除成功'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

@material_bp.route('/reorder', methods=['POST'])
@jwt_required()
def reorder_materials():
    """重新排序材料"""
    # 检查权限
    auth_check = teacher_or_admin_required()
    if auth_check:
        return auth_check
    
    data = request.json
    if not data or 'materials' not in data:
        return jsonify({'error': '没有提供排序数据'}), 400
    
    try:
        for item in data['materials']:
            material_id = item.get('id')
            order = item.get('order')
            if material_id and order is not None:
                material = Material.query.get(material_id)
                if material:
                    material.order = order
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '材料排序更新成功'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'排序更新失败: {str(e)}'}), 500 