from functools import wraps
from flask import request, jsonify
import jwt
import datetime
import os
from src.models.user import User, RefreshToken, db
from src.config import Config
from werkzeug.security import check_password_hash

# Security key
SECRET_KEY = os.getenv('API_SECRET_KEY', 'default-secret-key')

def generate_token(user_id):
    """Generate JWT token"""
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm='HS256')
    
    return token

def token_required(f):
    """Decorator for token verification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                else:
                    token = auth_header
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

def basic_auth_required(f):
    """Decorator for basic auth verification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        
        if not auth or not auth.username or not auth.password:
            return jsonify({'error': 'Login required'}), 401
            
        user = User.query.filter_by(username=auth.username).first()
        if not user or not check_password_hash(user.password_hash, auth.password):
            return jsonify({'error': 'Invalid credentials'}), 401
            
        return f(user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator for admin role verification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token not found!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            
            if data['role'] != 'admin':
                return jsonify({'error': 'Admin privileges required!'}), 403
                
            current_user = data['user']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated 

def generate_tokens(user_id):
    """Generate both access and refresh tokens"""
    # Access token
    access_token = jwt.encode({
        'user_id': user_id,
        'type': 'access',
        'exp': datetime.datetime.utcnow() + Config.ACCESS_TOKEN_EXPIRES
    }, Config.JWT_SECRET_KEY)
    
    # Refresh token
    refresh_token = jwt.encode({
        'user_id': user_id,
        'type': 'refresh',
        'exp': datetime.datetime.utcnow() + Config.REFRESH_TOKEN_EXPIRES
    }, Config.JWT_SECRET_KEY)
    
    # Store refresh token in database
    token_record = RefreshToken(
        token=refresh_token,
        user_id=user_id,
        expires_at=datetime.datetime.utcnow() + Config.REFRESH_TOKEN_EXPIRES
    )
    db.session.add(token_record)
    db.session.commit()
    
    return access_token, refresh_token

def revoke_token(token):
    """Revoke a refresh token"""
    token_record = RefreshToken.query.filter_by(token=token).first()
    if token_record:
        db.session.delete(token_record)
        db.session.commit() 