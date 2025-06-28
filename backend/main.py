import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, request, make_response
from backend.extensions import db, jwt, cors

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# JWT配置
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 令牌过期时间1小时
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # 刷新令牌过期时间7天

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with app
db.init_app(app)
jwt.init_app(app)
cors.init_app(app, resources={r"/*": {
    "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
    "supports_credentials": True,
    "allow_headers": ["Content-Type", "Authorization"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
}})

# 全局OPTIONS处理
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Create upload directory
upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(upload_dir, exist_ok=True)
os.makedirs(os.path.join(upload_dir, 'materials'), exist_ok=True)

# Create database directory
db_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_dir, exist_ok=True)

# Import models - Fix import order to prevent circular imports
from backend.models.user import User
from backend.models.course import Course
from backend.models.learning import LearningRecord, ChatHistory
from backend.models.material import Material
from backend.models.assessment import Assessment, StudentAnswer

# Import and register blueprints
from backend.api.user import user_bp
from backend.api.admin import admin_bp
from backend.api.learning import learning_bp
from backend.api.rag_ai import rag_ai_bp
from backend.api.auth import auth_bp

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(learning_bp)  # url_prefix already defined in blueprint
app.register_blueprint(rag_ai_bp, url_prefix='/api/rag')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': '教育管理系统后端运行正常'})

# Create database tables
# For Flask 2.0+, use app context instead of before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5001, debug=True)

