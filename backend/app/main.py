from flask import Flask
from app.api.teacher import teacher_bp
from app.api.student import student_bp
from app.api.admin import admin_bp

app = Flask(__name__)

app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>" 