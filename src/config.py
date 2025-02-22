import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@db:5432/market_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Token settings
    ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Flask settings
    DEBUG = False
    TESTING = False 