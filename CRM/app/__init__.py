# app/__init__.py

from flask import Flask, jsonify, request
from .config import Config
from .extensions import db, migrate, login_manager
from datetime import timedelta
import sys
import os

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
    
    # First, try to register the test blueprint
    try:
        print("\n--- Registering TEST API blueprint ---", file=sys.stderr)
        from .routes.test_api import test_bp
        print(f"✓ Successfully imported test_bp: {test_bp}", file=sys.stderr)
        app.register_blueprint(test_bp, url_prefix='/test-api')
        print(f"✓ Registered TEST API blueprint: {test_bp.name} at /test-api", file=sys.stderr)
        
        # Add a direct route to verify registration
        @app.route('/test-direct')
        def test_direct():
            return jsonify({"status": "success", "message": "Direct test route works!"})
            
    except Exception as e:
        print(f"✗ Error registering TEST API blueprint: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
    # Then try the main API blueprint
    try:
        print("\n--- Registering main API blueprint ---", file=sys.stderr)
        from .routes.api import api_bp
        print(f"✓ Successfully imported api_bp: {api_bp}", file=sys.stderr)
        app.register_blueprint(api_bp, url_prefix='/api')
        print(f"✓ Registered main API blueprint: {api_bp.name} at /api", file=sys.stderr)
    except Exception as e:
        print(f"✗ Error registering main API blueprint: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
    # Register other blueprints
    try:
        print("\n--- Registering main blueprint ---", file=sys.stderr)
        from .routes.main import main_bp
        print(f"✓ Successfully imported main_bp: {main_bp}", file=sys.stderr)
        app.register_blueprint(main_bp)
        print(f"✓ Registered main blueprint: {main_bp.name} at /", file=sys.stderr)
    except Exception as e:
        print(f"✗ Error registering main blueprint: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
    try:
        print("\n--- Registering auth blueprint ---", file=sys.stderr)
        from .routes.auth import auth_bp
        print(f"✓ Successfully imported auth_bp: {auth_bp}", file=sys.stderr)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        print(f"✓ Registered auth blueprint: {auth_bp.name} at /auth", file=sys.stderr)
    except Exception as e:
        print(f"✗ Error registering auth blueprint: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
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
    
    # Print all registered routes after all blueprints are registered
    @app.after_request
    def log_routes(response):
        if request.endpoint == 'list_routes':
            return response
            
        if not hasattr(app, 'routes_logged'):
            print("\n=== Registered Routes ===", file=sys.stderr)
            for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
                methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
                print(f"{rule.endpoint}: {methods} {rule.rule}", file=sys.stderr)
            app.routes_logged = True
            
        return response
    
    # Import models to ensure they are registered with SQLAlchemy
    print("\n=== Initializing Models ===", file=sys.stderr)
    try:
        from . import models
        print("✓ Models initialized", file=sys.stderr)
    except Exception as e:
        print(f"✗ Error initializing models: {str(e)}", file=sys.stderr)
    
    print("\n=== Application Initialization Complete ===\n", file=sys.stderr)
    return app
