from flask import Blueprint, jsonify

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
def dashboard():
    return jsonify({"message": "Student Dashboard"}) 