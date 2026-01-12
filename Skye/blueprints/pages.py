"""
Pages API blueprint
Handles page discovery and content loading for dynamic pages
"""
import os
import importlib.util
from flask import Blueprint, jsonify, current_app

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/api/pages')
def api_pages():
    """Get list of all available pages"""
    # Import discover_pages from main app to avoid circular imports
    from app import discover_pages
    return jsonify(discover_pages())


@pages_bp.route('/page/<page_id>')
def page_content(page_id):
    """Load content for a specific page"""
    pages_dir = os.path.join(
        os.path.dirname(__file__), '..', 'pages', page_id
    )

    if not os.path.exists(pages_dir):
        return jsonify({'error': 'Page not found'}), 404

    # Try to load the page's Python module
    page_file = os.path.join(pages_dir, 'page.py')
    if os.path.exists(page_file):
        try:
            spec = importlib.util.spec_from_file_location(
                f"{page_id}_page", page_file
            )
            page_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(page_module)

            if hasattr(page_module, 'get_content'):
                return jsonify(page_module.get_content())
        except Exception as e:
            return jsonify({'error': f'Error loading page: {str(e)}'}), 500

    # Fallback to static HTML if available
    html_file = os.path.join(pages_dir, 'content.html')
    if os.path.exists(html_file):
        with open(html_file, 'r') as f:
            return jsonify({'html': f.read()})

    return jsonify({
        'html': f'<h2>Page: {page_id}</h2><p>No content available</p>'
    })
