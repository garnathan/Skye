"""
Todo API blueprint
Handles saving and loading todo list data from config/todo_data.json
"""
import json
import os
from flask import Blueprint, jsonify, request

todo_bp = Blueprint('todo', __name__)

TODO_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'todo_data.json')

DEFAULT_TODO_DATA = {'todos': [], 'notes': ''}


def ensure_todo_file_exists():
    """Create todo_data.json if it doesn't exist"""
    if not os.path.exists(TODO_FILE):
        # Ensure config directory exists
        os.makedirs(os.path.dirname(TODO_FILE), exist_ok=True)
        with open(TODO_FILE, 'w') as f:
            json.dump(DEFAULT_TODO_DATA, f, indent=2)


def load_todo_data():
    """Load todo data from file"""
    ensure_todo_file_exists()
    try:
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return DEFAULT_TODO_DATA.copy()


def save_todo_data(data):
    """Save todo data to file"""
    with open(TODO_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@todo_bp.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos and notes"""
    data = load_todo_data()
    return jsonify(data)


@todo_bp.route('/api/todos', methods=['POST'])
def save_todos():
    """Save todos and notes"""
    data = request.get_json()
    if data:
        save_todo_data(data)
        return jsonify({'success': True})
    return jsonify({'error': 'No data provided'}), 400
