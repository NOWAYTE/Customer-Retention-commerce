"""
Database initialization script.
Run this file to create all database tables.
"""
import os
import sys
import traceback
from sqlalchemy import inspect, text
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
            from app.models.customer import Customer
            from app.models.segment import CustomerSegment
            print("✓ Models imported successfully")
        except Exception as e:
            print(f"Error importing models: {str(e)}")
            traceback.print_exc()
        
        # Create all database tables
        print("\nCreating database tables...")
        try:
            # Drop all tables first (be careful with this in production!)
            db.drop_all()
            print("✓ Dropped all existing tables")
            
            # Create all tables
            db.create_all()
            print("✓ Created all tables")
            
            # Verify tables were created
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\nDatabase initialized successfully!")
            print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("\nTables created:")
            for table in tables:
                print(f"- {table}")
                
            # Print table columns for verification
            for table in tables:
                print(f"\nTable: {table}")
                columns = [c['name'] for c in inspector.get_columns(table)]
                for col in columns:
                    print(f"  - {col}")
                    
        except Exception as e:
            print(f"Error during database initialization: {str(e)}")
            traceback.print_exc()
            
            # Try to get more details about the database state
            try:
                print("\nChecking database connection...")
                with db.engine.connect() as conn:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                    tables = [row[0] for row in result]
                    print("\nExisting tables:", tables)
            except Exception as db_error:
                print(f"Error checking database: {str(db_error)}")

if __name__ == '__main__':
    init_db()