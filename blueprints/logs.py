"""
Logs API blueprint
Handles log viewing, filtering, and clearing
"""
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from utils.logging_setup import log_storage, log_storage_lock

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/api/test-log', methods=['GET'])
def test_log():
    """Test endpoint to verify logging works"""
    current_app.logger.info("TEST INFO LOG")
    current_app.logger.warning("TEST WARNING LOG")
    current_app.logger.error("TEST ERROR LOG")
    return jsonify({'message': 'Test logs generated', 'storage_size': len(log_storage)})


@logs_bp.route('/api/logs', methods=['GET'])
def get_logs():
    """Get filtered logs"""
    try:
        time_filter = request.args.get('time', '5')
        level_filter = request.args.get('level', 'all')
        search_filter = request.args.get('search', '').lower()

        with log_storage_lock:
            logs = list(log_storage)

        # Time filtering
        if time_filter != 'all':
            try:
                minutes = int(time_filter)
                cutoff_time = datetime.now() - timedelta(minutes=minutes)
                logs = [
                    log for log in logs
                    if datetime.fromisoformat(log['timestamp']) >= cutoff_time
                ]
            except ValueError:
                pass

        # Level filtering
        if level_filter != 'all':
            logs = [log for log in logs if log['level'] == level_filter]

        # Search filtering
        if search_filter:
            logs = [log for log in logs if search_filter in log['message'].lower()]

        # Calculate stats
        stats = {
            'total': len(logs),
            'errors': sum(1 for log in logs if log['level'] == 'ERROR'),
            'warnings': sum(1 for log in logs if log['level'] == 'WARNING')
        }

        # Return most recent logs first
        logs.reverse()

        return jsonify({
            'logs': logs,
            'stats': stats
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching logs: {str(e)}")
        return jsonify({'error': str(e)}), 500


@logs_bp.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Clear all logs"""
    try:
        with log_storage_lock:
            log_storage.clear()

        current_app.logger.info("Logs cleared by user")

        return jsonify({'success': True})

    except Exception as e:
        current_app.logger.error(f"Error clearing logs: {str(e)}")
        return jsonify({'error': str(e)}), 500
