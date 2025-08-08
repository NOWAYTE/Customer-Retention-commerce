# app/__init__.py

from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager
from datetime import timedelta

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    # optionally load instance config: app.config.from_pyfile('config.py', silent=True)

    # JWT configuration
    app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure login manager
    @login_manager.user_loader
    def load_user(user_id):
        from .models import get_model
        User = get_model('User')
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    from .routes.main import main_bp
    from .routes.api import api_bp
    from .routes.auth import auth_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Import models to ensure they are registered with SQLAlchemy
    from . import models  # This will trigger model registration
    
    return app
