"""Decorators for consistent error handling"""
from functools import wraps
from flask import jsonify

def handle_api_errors(f):
    """Decorator to handle API errors consistently"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return decorated_function

def require_config_key(key, error_message=None):
    """Decorator to check if config key exists"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from utils import get_config_value
            value = get_config_value(key)
            if not value or value in ['your_gemini_api_key_here', 'your_youtube_api_key_here', 
                                      'your_client_id.apps.googleusercontent.com', 'your_client_secret']:
                msg = error_message or f'{key} not configured'
                return jsonify({'error': msg}), 500
            return f(*args, **kwargs)
        return decorated_function
    return decorator
