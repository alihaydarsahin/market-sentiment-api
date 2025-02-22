from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from src.config import Config
from src.models.user import db
from src.api.routes import api_bp
from src.api.error_handlers import register_error_handlers
from src.api.monitoring import init_monitoring

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per hour"]
    )
    
    # Setup error handlers
    register_error_handlers(app)
    
    # Initialize monitoring
    init_monitoring(app)
    
    # Register blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Add basic health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'API is running'
        })
    
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5000) 