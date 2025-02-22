from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            response = {
                'error': e.name,
                'message': e.description,
                'status_code': e.code
            }
            return jsonify(response), e.code
            
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        response = {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }
        return jsonify(response), 500

    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404

    @app.errorhandler(429)
    def ratelimit_error(e):
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded',
            'status_code': 429
        }), 429 