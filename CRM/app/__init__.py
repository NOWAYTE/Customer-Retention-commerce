# app/__init__.py

from flask import Flask, jsonify
from .config import Config
from .extensions import db, migrate, login_manager
from datetime import timedelta
import sys

def create_app(config_class=Config):
    """Application factory function."""
    print("\n=== Initializing Flask application ===", file=sys.stderr)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    
    # Debug prints for config
    print("\n=== App Configuration ===", file=sys.stderr)
    print(f"SECRET_KEY: {'set' if app.config.get('SECRET_KEY') else 'NOT SET'}", file=sys.stderr)
    print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}", file=sys.stderr)
    
    # JWT configuration
    app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Initialize extensions
    print("\n=== Initializing Extensions ===", file=sys.stderr)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    print("✓ Extensions initialized", file=sys.stderr)
    
    # Configure login manager
    @login_manager.user_loader
    def load_user(user_id):
        from .models import get_model
        User = get_model('User')
        return User.query.get(int(user_id))
    
    # Import and register blueprints with error handling
    print("\n=== Registering Blueprints ===", file=sys.stderr)
    
    try:
        from .routes.main import main_bp
        app.register_blueprint(main_bp)
        print(f"✓ Registered blueprint: {main_bp.name} at /", file=sys.stderr)
        print(f"  - Routes: {', '.join([str(rule) for rule in main_bp.url_map._rules])}", file=sys.stderr)
    except Exception as e:
        print(f"✗ Error registering main blueprint: {str(e)}", file=sys.stderr)
    
    try:
        from .routes.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        print(f"✓ Registered blueprint: {api_bp.name} at /api", file=sys.stderr)
        print(f"  - Routes: {', '.join([str(rule) for rule in api_bp.url_map._rules])}", file=sys.stderr)
    except Exception as e:
        print(f"✗ Error registering API blueprint: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
    try:
        from .routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        print(f"✓ Registered blueprint: {auth_bp.name} at /auth", file=sys.stderr)
        print(f"  - Routes: {', '.join([str(rule) for rule in auth_bp.url_map._rules])}", file=sys.stderr)
        
        # Add debug route to list all registered routes
        @app.route('/debug/routes')
        def list_routes():
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': sorted(rule.methods),
                    'path': str(rule)
                })
            return jsonify(routes)
            
        print("✓ Added debug route: /debug/routes", file=sys.stderr)
        
    except Exception as e:
        print(f"✗ Error registering auth blueprint: {str(e)}", file=sys.stderr)
        raise  # Re-raise to see full traceback
    
    # Import models to ensure they are registered with SQLAlchemy
    print("\n=== Initializing Models ===", file=sys.stderr)
    try:
        from . import models
        print("✓ Models initialized", file=sys.stderr)
    except Exception as e:
        print(f"✗ Error initializing models: {str(e)}", file=sys.stderr)
    
    print("\n=== Application Initialization Complete ===\n", file=sys.stderr)
    return app
