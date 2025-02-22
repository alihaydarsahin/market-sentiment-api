import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.models.user import db, User
from src.api.app import create_app

def init_db():
    """Initialize database and create admin user"""
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password(os.getenv('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")

if __name__ == '__main__':
    init_db() 