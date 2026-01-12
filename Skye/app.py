#!/usr/bin/env python3
# Standard library imports
import os
import importlib.util

# Flask imports
from flask import Flask, render_template, jsonify, request

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

app = Flask(__name__)

# ============================================================================
# LOG MANAGEMENT SYSTEM - Must be set up immediately after app creation
# ============================================================================

# Import logging system
from utils.logging_setup import setup_logging, log_storage, log_storage_lock
setup_logging(app)

# Import utilities
from utils import load_config, get_config_value, handle_api_errors, require_config_key

# ============================================================================
# BLUEPRINTS
# ============================================================================

# Import and register blueprints
from blueprints.weather import weather_bp
from blueprints.logs import logs_bp
from blueprints.tools import tools_bp
from blueprints.pages import pages_bp
from blueprints.music_next import music_next_bp
from blueprints.gemini import gemini_bp
from blueprints.youtube import youtube_bp
from blueprints.dashboard import dashboard_bp

app.register_blueprint(weather_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(tools_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(music_next_bp)
app.register_blueprint(gemini_bp)
app.register_blueprint(youtube_bp)
app.register_blueprint(dashboard_bp)

def discover_pages():
    """Automatically discover pages from the pages directory"""
    pages = []
    pages_dir = os.path.join(os.path.dirname(__file__), 'pages')
    
    if os.path.exists(pages_dir):
        for item in os.listdir(pages_dir):
            page_path = os.path.join(pages_dir, item)
            if os.path.isdir(page_path) and not item.startswith('_'):
                # Check if page has a config.py file
                config_file = os.path.join(page_path, 'config.py')
                if os.path.exists(config_file):
                    try:
                        spec = importlib.util.spec_from_file_location(f"{item}_config", config_file)
                        config = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(config)
                        
                        # Skip hidden pages
                        if getattr(config, 'HIDDEN', False):
                            continue
                        
                        pages.append({
                            'id': item,
                            'name': getattr(config, 'NAME', getattr(config, 'PAGE_NAME', item.title())),
                            'description': getattr(config, 'PAGE_DESCRIPTION', ''),
                            'icon': getattr(config, 'ICON', getattr(config, 'PAGE_ICON', 'fas fa-file'))
                        })
                    except Exception as e:
                        print(f"Error loading config for {item}: {e}")
                        pages.append({
                            'id': item,
                            'name': item.title(),
                            'description': '',
                            'icon': 'fas fa-file'
                        })
    
    # Sort pages with home first, then by ORDER if specified, then alphabetically
    def sort_key(page):
        if page['id'] == 'home':
            return '0'  # Home comes first
        # Check if page has ORDER attribute from config
        page_path = os.path.join(pages_dir, page['id'])
        config_file = os.path.join(page_path, 'config.py')
        if os.path.exists(config_file):
            try:
                spec = importlib.util.spec_from_file_location(f"{page['id']}_config", config_file)
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)
                order = getattr(config, 'ORDER', 999)
                return f"{order:03d}_{page['name']}"
            except:
                pass
        return f"999_{page['name']}"
    
    return sorted(pages, key=sort_key)

@app.route('/')
def index():
    app.logger.info(f"Home page accessed from {request.remote_addr}")
    pages = discover_pages()
    return render_template('index.html', pages=pages)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.svg')

# ============================================================================
# All API routes have been moved to blueprints for better organization:
# - blueprints/weather.py, logs.py, tools.py, pages.py
# - blueprints/music_next.py, gemini.py, youtube.py, dashboard.py
# ============================================================================

@app.route('/api/restart', methods=['POST'])
def restart_server():
    """Restart the Skye server"""
    try:
        app.logger.warning("Server restart requested by user")
        # Send restart signal to keep_alive.py
        os.system('touch /tmp/skye_restart')
        return jsonify({'status': 'restarting'})
    except Exception as e:
        app.logger.error(f"Server restart failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/vrt-calculator')
def vrt_calculator_standalone():
    """Standalone VRT Calculator page"""
    pages_dir = os.path.join(os.path.dirname(__file__), 'pages', '_vrt-calculator')
    page_file = os.path.join(pages_dir, 'page.py')
    
    if os.path.exists(page_file):
        try:
            spec = importlib.util.spec_from_file_location("vrt_page", page_file)
            page_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(page_module)
            
            if hasattr(page_module, 'get_content'):
                content = page_module.get_content()
                return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VRT Calculator - Skye</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
    </style>
</head>
<body>
    {content['html']}
</body>
</html>
                '''
        except Exception as e:
            return f'<h1>Error loading VRT Calculator: {str(e)}</h1>', 500
    
    return '<h1>VRT Calculator not found</h1>', 404


# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

# Configure session for OAuth (YouTube playlist copying)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')

# Log application startup
app.logger.info("Skye application started")

if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=True, reloader_type='stat')