import os

def create_project_structure():
    """Create all necessary directories for the project"""
    directories = [
        'data/raw',
        'data/processed',
        'data/analysis/figures',
        'models',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

if __name__ == "__main__":
    create_project_structure() 