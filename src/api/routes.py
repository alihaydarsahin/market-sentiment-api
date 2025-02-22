from flask import Blueprint, jsonify, request
from datetime import datetime
import pandas as pd
import os
import jwt
from sqlalchemy import text
from src.api.auth import token_required, admin_required, generate_tokens, revoke_token, basic_auth_required, generate_token
from src.models.user import User, RefreshToken, db
from src.config import Config
import logging
import joblib
from flask_jwt_extended import jwt_required, create_access_token
from src.api.monitoring import track_request

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Setup logging
logger = logging.getLogger(__name__)

class ModelAPI:
    def __init__(self):
        self.models_dir = 'models'
        self.data_dir = 'data/processed'
        self.figures_dir = 'data/analysis/figures'
        self.load_latest_model()
    
    def load_latest_model(self):
        """Load the latest trained model"""
        try:
            model_files = [f for f in os.listdir(self.models_dir) 
                         if f.endswith('.joblib')]
            if not model_files:
                raise FileNotFoundError("No model files found")
            
            latest_model = sorted(model_files)[-1]
            self.model = joblib.load(os.path.join(self.models_dir, latest_model))
            self.scaler = joblib.load(os.path.join(self.models_dir, 'scaler.joblib'))
            logger.info(f"Loaded model: {latest_model}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.scaler = None

api = ModelAPI()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'message': 'API is running',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': str(e)
        }), 500

@api_bp.route('/auth/login', methods=['POST'])
@basic_auth_required
def login(user):
    """Login endpoint"""
    token = generate_token(user.id)
    return jsonify({
        'message': 'Login successful',
        'access_token': token
    }), 200

@api_bp.route('/auth/refresh', methods=['POST'])
def refresh():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({'error': 'Refresh token required'}), 401
    
    try:
        # Verify token
        data = jwt.decode(
            refresh_token, 
            Config.JWT_SECRET_KEY,
            algorithms=['HS256']
        )
        
        # Check if token is in database and not expired
        token_record = RefreshToken.query.filter_by(
            token=refresh_token,
            user_id=data['user_id']
        ).first()
        
        if not token_record or token_record.expires_at < datetime.utcnow():
            return jsonify({'error': 'Invalid refresh token'}), 401
        
        # Generate new tokens
        access_token, new_refresh_token = generate_tokens(data['user_id'])
        
        # Revoke old refresh token
        revoke_token(refresh_token)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': new_refresh_token
        })
        
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 401

@api_bp.route('/predict', methods=['POST'])
@token_required
def predict(current_user):
    """Make prediction"""
    data = request.get_json()
    
    # Add your prediction logic here
    prediction = {
        'prediction': 0.75,
        'confidence': 0.85
    }
    
    return jsonify(prediction), 200

@api_bp.route('/data/latest', methods=['GET'])
@token_required
def get_latest_data(current_user):
    """Get latest data"""
    # Add your data retrieval logic here
    data = {
        'timestamp': '2025-02-22T19:00:00',
        'market_sentiment': 0.65
    }
    
    return jsonify(data), 200

@api_bp.route('/visualizations', methods=['GET'])
def get_visualizations():
    """Get list of available visualizations"""
    try:
        viz_files = [f for f in os.listdir(api.figures_dir) 
                    if f.endswith('.png')]
        
        return jsonify({
            'visualizations': [
                {
                    'filename': f,
                    'path': f'/static/figures/{f}',
                    'created': datetime.fromtimestamp(
                        os.path.getctime(
                            os.path.join(api.figures_dir, f)
                        )
                    ).isoformat()
                }
                for f in viz_files
            ]
        })
        
    except Exception as e:
        logger.error(f"Visualization listing error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/model/info', methods=['GET'])
@admin_required
def get_model_info(current_user):
    """Admin-only model info endpoint"""
    try:
        if not api.model:
            return jsonify({'error': 'No model loaded'}), 404
        
        return jsonify({
            'model_type': type(api.model).__name__,
            'features': api.model.feature_names_in_.tolist(),
            'parameters': api.model.get_params()
        })
        
    except Exception as e:
        logger.error(f"Model info error: {e}")
        return jsonify({'error': str(e)}), 500 