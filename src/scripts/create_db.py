import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.api.app import create_app
from src.models.user import db, User

def init_db():
    """Initialize database and create admin user"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')  # Change in production!
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")

if __name__ == '__main__':
    print("Creating database...")
    init_db()
    print("Database initialization completed!") 