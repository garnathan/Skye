"""
Logging system for Skye application
In-memory log storage with custom handler for Flask app
"""
import logging
import threading
from datetime import datetime
from collections import deque

# In-memory log storage (with max size to prevent memory issues)
# Storing last 500 logs - approximately 50-100KB memory usage
log_storage = deque(maxlen=500)
log_storage_lock = threading.Lock()


class MemoryLogHandler(logging.Handler):
    """Custom log handler that stores logs in memory"""

    def emit(self, record):
        try:
            message = record.getMessage()

            # Skip werkzeug HTTP request/response logs (they're too noisy)
            if record.name == 'werkzeug' and (' - - [' in message or '"GET ' in message or '"POST ' in message):
                return

            # Remove localhost IP addresses but preserve the context
            # Replace "from 127.0.0.1" with just "locally"
            message = message.replace(' from 127.0.0.1', ' locally')
            message = message.replace('127.0.0.1', 'localhost')

            # Remove excessive whitespace
            message = ' '.join(message.split())

            # Skip if message is empty after cleaning
            if not message:
                return

            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'message': message,
                'logger': record.name,
                'module': record.module
            }

            with log_storage_lock:
                log_storage.append(log_entry)
        except Exception:
            self.handleError(record)


def setup_logging(app):
    """
    Set up logging for Flask app with custom memory handler

    Args:
        app: Flask application instance
    """
    # Create and configure memory handler
    memory_handler = MemoryLogHandler()
    memory_handler.setLevel(logging.DEBUG)
    # Use simple formatter since we do custom message cleaning in the handler
    formatter = logging.Formatter('%(message)s')
    memory_handler.setFormatter(formatter)

    # Add handler to Flask app logger only (not root logger to avoid duplicates)
    app.logger.addHandler(memory_handler)
    app.logger.setLevel(logging.INFO)  # Ensure app logger captures INFO and above

    # Disable werkzeug HTTP request logs (too noisy)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    app.logger.info("Logging system initialized")
