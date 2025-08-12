"""
Database initialization script.
Run this file to create all database tables.
"""
import os
import sys
import traceback
from app import create_app
from app.extensions import db

def init_db():
    print("Initializing database...")
    
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        # Create the database directory if it doesn't exist
        db_dir = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(db_dir, exist_ok=True)
        
        # Explicitly import all models
        print("\nImporting models...")
        try:
            from app.models.user import User
            print("✓ User model imported successfully")
        except Exception as e:
            print(f"Error importing User model: {str(e)}")
            traceback.print_exc()
        
        # Verify models are registered with SQLAlchemy
        print("\nModels registered with SQLAlchemy:")
        for model in db.Model._decl_class_registry.values():
            if hasattr(model, '__tablename__'):
                print(f"- {model.__name__} (table: {model.__tablename__})")
        
        # Create all database tables
        print("\nCreating database tables...")
        try:
            db.create_all()
            print("✓ Database tables created")
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            traceback.print_exc()
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("\nDatabase initialized successfully!")
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\nTables created:")
        for table in tables:
            print(f"- {table}")

if __name__ == '__main__':
    init_db()