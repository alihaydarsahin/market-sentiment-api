import os

def create_directories():
    """Create all necessary directories"""
    directories = [
        'data/raw/github',
        'data/raw/news',
        'data/raw/reddit',
        'data/raw/market',
        'data/analysis/figures',
        'data/logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

if __name__ == "__main__":
    create_directories() 