# app/__init__.py

from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager
from .routes.main import main_bp
from .routes.api import api_bp

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    # optionally load instance config: app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
