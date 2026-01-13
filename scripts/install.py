#!/usr/bin/env python3
"""Skye Installation Script - Sets up all dependencies and starts the service"""
import sys
import os
import shutil
import multiprocessing
import pip


def install_package(package):
    """Install a package using pip"""
    try:
        pip.main(['install', package, '--quiet'])
        return True
    except SystemExit as e:
        return e.code == 0
    except Exception:
        return False


def check_brew():
    """Check if Homebrew is installed"""
    return shutil.which('brew') is not None


def find_and_kill_processes(pattern):
    """Find and kill processes matching pattern using psutil"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline') or []
                if cmdline:
                    cmd_str = ' '.join(cmdline)
                    if pattern in cmd_str:
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except ImportError:
        print("  ⚠ psutil not available, skipping process cleanup")


def run_keep_alive():
    """Run keep_alive.py in a background process"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skye_dir = os.path.dirname(script_dir)

    os.chdir(skye_dir)
    sys.path.insert(0, skye_dir)

    # Redirect output for background operation
    log_file = open('/tmp/keep_alive.log', 'w')
    sys.stdout = log_file
    sys.stderr = log_file

    # Import and run keep_alive
    from scripts import keep_alive


def main():
    print("=" * 60)
    print("Skye Installation Script")
    print("=" * 60)

    # Check Python version
    print("\n[1/5] Checking Python version...")
    if sys.version_info < (3, 7):
        print("  ✗ Python 3.7+ required")
        sys.exit(1)
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Install pip packages
    print("\n[2/5] Installing Python packages...")
    packages = [
        'flask',
        'requests',
        'google-generativeai',
        'python-dotenv',
        'psutil',
        'yt-dlp'
    ]

    for pkg in packages:
        print(f"  Installing {pkg}...")
        if not install_package(pkg):
            print(f"  ⚠ Warning: {pkg} installation had issues")
    print("  ✓ Python packages installed")

    # Check for Homebrew (optional)
    print("\n[3/5] Checking system dependencies...")
    if check_brew():
        print("  ✓ Homebrew found")
    else:
        print("  ⚠ Homebrew not found (optional, skipping)")

    # Create .env from example if it doesn't exist
    print("\n[4/5] Setting up configuration...")
    env_example_path = 'config/.env.example'
    env_path = '.env'
    if not os.path.exists(env_path) and os.path.exists(env_example_path):
        shutil.copy(env_example_path, env_path)
        print("  ✓ Created .env from template")
        print("  ⚠ Edit .env to add your API keys")
    elif os.path.exists(env_path):
        print("  ✓ .env already exists")
    else:
        print("  ⚠ No config/.env.example found")

    # Start keep_alive monitor
    print("\n[5/5] Starting Skye monitor...")

    # Kill any existing processes using psutil
    find_and_kill_processes('keep_alive.py')
    find_and_kill_processes('app.py')

    # Start monitor in background using multiprocessing
    try:
        process = multiprocessing.Process(target=run_keep_alive, daemon=True)
        process.start()

        print("  ✓ Skye monitor started")
        print("\n" + "=" * 60)
        print("Installation complete!")
        print("=" * 60)
        print("\nSkye is now running at: http://localhost:5001")
        print("\nMonitor logs: /tmp/keep_alive.log")
        print("Server logs: Check monitor output")
        print("\nTo stop: Use Activity Monitor or 'kill' command")
        print("\nNext steps:")
        print("  1. Edit .env with your API keys")
        print("  2. Restart by running this script again")
    except Exception as e:
        print(f"  ✗ Failed to start monitor: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # Change to parent directory (Skye root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skye_dir = os.path.dirname(script_dir)
    os.chdir(skye_dir)
    main()
