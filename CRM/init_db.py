"""
Database initialization script.
Run this file to create all database tables.
"""
import os
import sys
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
        
        # Create all database tables
        print("Creating database tables...")
        db.create_all()
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("\nDatabase initialized successfully!")
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\nTables created:")
        for table in tables:
            print(f"- {table}")
        
        # Verify users table has the correct columns
        if 'users' in tables:
            print("\nUsers table columns:")
            columns = [c['name'] for c in inspector.get_columns('users')]
            for col in columns:
                print(f"- {col}")

if __name__ == '__main__':
    init_db()
