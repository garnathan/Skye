#!/usr/bin/env python3
"""Skye Installation Script - Sets up all dependencies and starts the service"""
import subprocess
import sys
import os
import shutil

def run(cmd, check=True):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"  ✗ Failed: {result.stderr.strip()}")
            return False
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def check_brew():
    """Check if Homebrew is installed"""
    return shutil.which('brew') is not None

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
        'python-dotenv'
    ]
    
    for pkg in packages:
        print(f"  Installing {pkg}...")
        if not run(f'{sys.executable} -m pip install {pkg} --quiet'):
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
    if not os.path.exists('.env') and os.path.exists('.env.example'):
        shutil.copy('.env.example', '.env')
        print("  ✓ Created .env from template")
        print("  ⚠ Edit .env to add your API keys")
    elif os.path.exists('.env'):
        print("  ✓ .env already exists")
    else:
        print("  ⚠ No .env.example found")
    
    # Start keep_alive monitor
    print("\n[5/5] Starting Skye monitor...")
    
    # Kill any existing processes
    run('pkill -f "python.*keep_alive.py"', check=False)
    run('pkill -f "python.*app.py"', check=False)
    
    # Start monitor in background
    if run(f'nohup {sys.executable} keep_alive.py > /tmp/keep_alive.log 2>&1 &', check=False):
        print("  ✓ Skye monitor started")
        print("\n" + "=" * 60)
        print("Installation complete!")
        print("=" * 60)
        print("\nSkye is now running at: http://localhost:5001")
        print("\nMonitor logs: /tmp/keep_alive.log")
        print("Server logs: Check monitor output")
        print("\nTo stop: pkill -f keep_alive.py")
        print("\nNext steps:")
        print("  1. Edit .env with your API keys")
        print("  2. Restart: pkill -f keep_alive.py && python3 keep_alive.py &")
    else:
        print("  ✗ Failed to start monitor")
        sys.exit(1)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
