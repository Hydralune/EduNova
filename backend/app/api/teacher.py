from flask import Blueprint, jsonify

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/dashboard')
def dashboard():
    return jsonify({"message": "Teacher Dashboard"}) 