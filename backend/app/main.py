from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cors
from .models.user import User # Import User model to ensure it's registered with SQLAlchemy

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}) # Allow CORS for all /api/ routes

    # Register blueprints
    from app.api.teacher import teacher_bp
    from app.api.student import student_bp
    from app.api.admin import admin_bp
    from app.api.auth import auth_bp
    
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Shell context for Flask CLI
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User}

    return app 