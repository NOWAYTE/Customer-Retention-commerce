# app/__init__.py

from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    # optionally load instance config: app.config.from_pyfile('config.py', silent=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Import and register blueprints
    from .routes.main import main_bp
    from .routes.api import api_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Import models to ensure they are registered with SQLAlchemy
    from . import models  # This will trigger model registration
    
    return app

