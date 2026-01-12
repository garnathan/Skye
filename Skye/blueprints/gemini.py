"""
Gemini API blueprint
Handles Gemini AI chat and model listing, plus pipeline stats
"""
import os
import sys
import subprocess
from flask import Blueprint, jsonify, request, current_app, Response
import google.generativeai as genai
from utils import load_config, get_config_value, handle_api_errors, require_config_key

gemini_bp = Blueprint('gemini', __name__)


@gemini_bp.route('/api/gemini/models', methods=['GET'])
def list_gemini_models():
    """List available Gemini models"""
    try:
        # Get API key from config file or environment
        config = load_config()
        api_key = config.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            return jsonify({'error': 'Gemini API key not configured'}), 500

        # Configure Gemini
        genai.configure(api_key=api_key)

        # List models
        models = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                models.append({
                    'name': model.name,
                    'display_name': model.display_name or model.name
                })

        return jsonify({'models': models})

    except Exception as e:
        current_app.logger.error(f"Gemini models list error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@gemini_bp.route('/api/gemini/chat', methods=['POST'])
@require_config_key(
    'gemini_api_key',
    'Gemini API key not configured. Please set your API key in config.json'
)
@handle_api_errors
def gemini_chat():
    """Handle Gemini chat requests"""

    data = request.get_json()
    message = data.get('message', '').strip()
    model_name = data.get('model', 'models/gemini-pro')

    current_app.logger.info(
        f"Gemini chat request with model: {model_name}, "
        f"message length: {len(message)}"
    )

    if not message:
        current_app.logger.warning("Gemini chat request failed: No message provided")
        return jsonify({'error': 'No message provided'}), 400

    api_key = get_config_value('gemini_api_key') or os.environ.get('GEMINI_API_KEY')
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(message)

    if response.text:
        current_app.logger.info(
            f"Gemini chat response generated, length: {len(response.text)}"
        )
        return jsonify({'response': response.text})

    current_app.logger.error("Gemini chat failed: No response generated")
    return jsonify({'error': 'No response generated'}), 500


@gemini_bp.route('/api/pipeline-stats', methods=['GET'])
def run_pipeline_stats():
    """Run the critical pipeline stats script with streaming output"""

    def generate():
        script_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'PipelineStats',
            'critical_pipeline_stats.py'
        )

        if not os.path.exists(script_path):
            yield (
                f"data: {{\"output\": \"Script not found at: {script_path}\", "
                f"\"status\": \"error\"}}\\n\\n"
            )
            return

        try:
            yield (
                f"data: {{\"output\": \"Starting pipeline analysis...\\n\", "
                f"\"status\": \"running\"}}\\n\\n"
            )

            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=os.path.dirname(script_path)
            )

            # Read output line by line
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Escape quotes and newlines for JSON
                    escaped_line = (
                        output.strip()
                        .replace('\\', '\\\\')
                        .replace('"', '\\"')
                    )
                    yield (
                        f"data: {{\"output\": \"{escaped_line}\\n\", "
                        f"\"status\": \"running\"}}\\n\\n"
                    )

            # Check for any remaining output
            remaining_output = process.stdout.read()
            if remaining_output:
                escaped_output = (
                    remaining_output.strip()
                    .replace('\\', '\\\\')
                    .replace('"', '\\"')
                )
                yield (
                    f"data: {{\"output\": \"{escaped_output}\\n\", "
                    f"\"status\": \"running\"}}\\n\\n"
                )

            # Check for errors
            stderr_output = process.stderr.read()
            if stderr_output:
                escaped_error = (
                    stderr_output.strip()
                    .replace('\\', '\\\\')
                    .replace('"', '\\"')
                )
                yield (
                    f"data: {{\"output\": \"Error: {escaped_error}\\n\", "
                    f"\"status\": \"error\"}}\\n\\n"
                )

            return_code = process.poll()
            if return_code == 0:
                yield (
                    f"data: {{\"output\": \"\\nScript completed successfully.\", "
                    f"\"status\": \"success\"}}\\n\\n"
                )
            else:
                yield (
                    f"data: {{\"output\": \"\\nScript failed with return code: "
                    f"{return_code}\", \"status\": \"error\"}}\\n\\n"
                )

        except Exception as e:
            current_app.logger.error(f"Pipeline stats error: {str(e)}")
            yield f"data: {{\"output\": \"Error: {str(e)}\", \"status\": \"error\"}}\\n\\n"

    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control'
    })
