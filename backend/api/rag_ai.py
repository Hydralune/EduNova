from flask import Blueprint, request, jsonify

rag_ai_bp = Blueprint('rag_ai', __name__)

@rag_ai_bp.route('/status', methods=['GET'])
def get_module_status_api():
    """获取RAG和AI模块状态"""
    return jsonify({
        'status': 'success',
        'rag_enabled': False,
        'ai_enabled': False,
        'message': '模块状态获取成功'
    })
