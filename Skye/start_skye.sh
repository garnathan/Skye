#!/bin/bash

SKYE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SKYE_DIR/skye.pid"
LOG_FILE="$SKYE_DIR/skye.log"

start_skye() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Skye is already running (PID: $(cat $PID_FILE))"
        return 0
    fi
    
    echo "Starting Skye..."
    cd "$SKYE_DIR"
    nohup python3 app.py > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Skye started (PID: $!)"
    echo "Access at: http://localhost:5001"
}

stop_skye() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm -f "$PID_FILE"
            echo "Skye stopped"
        else
            echo "Skye was not running"
            rm -f "$PID_FILE"
        fi
    else
        echo "Skye is not running"
    fi
}

status_skye() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Skye is running (PID: $(cat $PID_FILE))"
        echo "Access at: http://localhost:5001"
    else
        echo "Skye is not running"
    fi
}

case "$1" in
    start)
        start_skye
        ;;
    stop)
        stop_skye
        ;;
    restart)
        stop_skye
        sleep 2
        start_skye
        ;;
    status)
        status_skye
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac