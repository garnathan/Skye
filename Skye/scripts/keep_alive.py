#!/usr/bin/env python3
import time
import requests
import os
import sys
import psutil
import multiprocessing

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


def find_skye_processes():
    """Find all running Skye app.py processes"""
    skye_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            # Check if this is a python process running app.py
            if cmdline and len(cmdline) >= 2:
                cmd_str = ' '.join(cmdline)
                if 'python' in cmdline[0].lower() and 'app.py' in cmd_str:
                    # Make sure it's our Skye app.py, not some other app.py
                    if SKYE_DIR in cmd_str or any('app.py' in arg for arg in cmdline):
                        skye_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return skye_processes


def kill_skye_processes():
    """Kill all running Skye app.py processes"""
    for proc in find_skye_processes():
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def run_skye_app():
    """Run the Skye Flask app (called in subprocess)"""
    os.chdir(SKYE_DIR)
    sys.path.insert(0, SKYE_DIR)

    # Redirect stdout/stderr to devnull for background operation
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    # Import and run the app
    import app
    app.app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)


def restart_skye():
    try:
        # Kill existing processes
        kill_skye_processes()
        time.sleep(1)

        # Start app.py in a new process
        process = multiprocessing.Process(target=run_skye_app, daemon=True)
        process.start()

        print(f"[{time.strftime('%H:%M:%S')}] Restarted Skye from {SKYE_DIR}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Failed to restart Skye: {e}")


if __name__ == '__main__':
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
