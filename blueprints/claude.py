"""
Claude API blueprint
Handles Anthropic Claude AI chat
"""
import os
from flask import Blueprint, jsonify, request, current_app
from utils import load_config, get_config_value, handle_api_errors, require_config_key

claude_bp = Blueprint('claude', __name__)

# Lazy import anthropic to avoid startup errors if not installed
_anthropic_client = None


def get_anthropic_client():
    """Get or create Anthropic client"""
    global _anthropic_client
    if _anthropic_client is None:
        try:
            import anthropic
            api_key = get_config_value('anthropic_api_key') or os.environ.get('ANTHROPIC_API_KEY')
            if api_key:
                _anthropic_client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            current_app.logger.error("anthropic package not installed")
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    return _anthropic_client


@claude_bp.route('/api/claude/models', methods=['GET'])
def list_claude_models():
    """List available Claude models"""
    # Return static list of available models
    models = [
        {'name': 'claude-sonnet-4-20250514', 'display_name': 'Claude Sonnet 4'},
        {'name': 'claude-opus-4-20250514', 'display_name': 'Claude Opus 4'},
        {'name': 'claude-3-5-haiku-20241022', 'display_name': 'Claude 3.5 Haiku'},
        {'name': 'claude-3-5-sonnet-20241022', 'display_name': 'Claude 3.5 Sonnet'},
        {'name': 'claude-3-opus-20240229', 'display_name': 'Claude 3 Opus'},
    ]
    return jsonify({'models': models})


@claude_bp.route('/api/claude/chat', methods=['POST'])
@require_config_key(
    'anthropic_api_key',
    'Anthropic API key not configured. Please set ANTHROPIC_API_KEY in .env or config.json'
)
@handle_api_errors
def claude_chat():
    """Handle Claude chat requests"""

    data = request.get_json()
    message = data.get('message', '').strip()
    model_name = data.get('model', 'claude-sonnet-4-20250514')
    history = data.get('history', [])

    current_app.logger.info(
        f"Claude chat request with model: {model_name}, "
        f"message length: {len(message)}, history length: {len(history)}"
    )

    if not message:
        current_app.logger.warning("Claude chat request failed: No message provided")
        return jsonify({'error': 'No message provided'}), 400

    try:
        client = get_anthropic_client()
        if client is None:
            return jsonify({'error': 'Anthropic client not initialized. Check API key.'}), 500

        # Build messages array with history
        messages = []
        for msg in history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Add current message
        messages.append({
            'role': 'user',
            'content': message
        })

        # Make API call
        response = client.messages.create(
            model=model_name,
            max_tokens=4096,
            messages=messages
        )

        if response.content and len(response.content) > 0:
            response_text = response.content[0].text
            current_app.logger.info(
                f"Claude chat response generated, length: {len(response_text)}"
            )
            return jsonify({'response': response_text})

        current_app.logger.error("Claude chat failed: No response generated")
        return jsonify({'error': 'No response generated'}), 500

    except ImportError as e:
        current_app.logger.error(f"Claude import error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Claude chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500
