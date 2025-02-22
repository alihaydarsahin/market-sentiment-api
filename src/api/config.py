import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv('RATE_LIMIT', '100/hour')
    
    # Logging
    LOGGING_CONFIG = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'data/logs/production.log',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['file']
        }
    } 