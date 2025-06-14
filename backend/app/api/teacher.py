from flask import Blueprint

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/teacher/dashboard')
def dashboard():
    return "Teacher Dashboard" 