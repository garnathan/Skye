#!/usr/bin/env python3
import subprocess
import time
import requests
import os
import sys

# Force unbuffered output for logging
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

# Get the Skye root directory (parent of scripts directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKYE_DIR = os.path.dirname(SCRIPT_DIR)

def is_responding():
    try:
        return requests.get('http://localhost:5001', timeout=3).status_code == 200
    except:
        return False

def restart_skye():
    try:
        # Kill existing process
        subprocess.run('pkill -f "python.*app.py"', shell=True, capture_output=True)
        time.sleep(1)

        # Start app.py from the Skye root directory
        subprocess.Popen(['python3', 'app.py'], cwd=SKYE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[{time.strftime('%H:%M:%S')}] Restarted Skye from {SKYE_DIR}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Failed to restart Skye: {e}")

print("Skye monitor started (checking every 30s)")

if not is_responding():
    restart_skye()

while True:
    try:
        if os.path.exists('/tmp/skye_restart'):
            os.remove('/tmp/skye_restart')
            restart_skye()
        elif not is_responding():
            print(f"[{time.strftime('%H:%M:%S')}] Skye not responding")
            restart_skye()
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nMonitor stopped")
        sys.exit(0)
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")
        time.sleep(30)