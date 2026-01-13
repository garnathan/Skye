"""Decorators for consistent error handling"""
from __future__ import annotations
from functools import wraps
from flask import jsonify, current_app
import requests

from utils.circuit_breaker import CircuitOpenError


def handle_api_errors(f):
    """Decorator to handle API errors with structured logging and clear error responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except CircuitOpenError as e:
            # Service temporarily unavailable due to repeated failures
            current_app.logger.warning(
                f"[{f.__name__}] Circuit open: {e.circuit_name} - retry in {e.recovery_in:.0f}s"
            )
            return jsonify({
                'error': 'Service temporarily unavailable',
                'code': 'SERVICE_UNAVAILABLE',
                'service': e.circuit_name,
                'retry_in_seconds': round(e.recovery_in),
                'retryable': True
            }), 503
        except requests.Timeout as e:
            # Request timeout
            current_app.logger.warning(f"[{f.__name__}] Request timeout: {e}")
            return jsonify({
                'error': 'Request timed out',
                'code': 'TIMEOUT',
                'retryable': True
            }), 504
        except requests.RequestException as e:
            # External API failure
            current_app.logger.error(f"[{f.__name__}] External API error: {e}")
            return jsonify({
                'error': 'External service error',
                'code': 'EXTERNAL_API_ERROR',
                'retryable': True
            }), 503
        except Exception as e:
            # Unexpected internal error
            current_app.logger.error(f"[{f.__name__}] Internal error: {e}", exc_info=True)
            return jsonify({
                'error': 'Internal server error',
                'code': 'INTERNAL_ERROR',
                'retryable': False
            }), 500
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
                return jsonify({'error': msg, 'code': 'CONFIG_MISSING', 'retryable': False}), 500
            return f(*args, **kwargs)
        return decorated_function
    return decorator
