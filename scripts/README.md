# Scripts Directory

This directory contains all startup and utility scripts for the Skye application.

## Scripts

### Startup Scripts

- **`launch_skye.sh`** - Quick launcher with keep-alive monitoring
  ```bash
  ./scripts/launch_skye.sh
  ```
  Starts Skye with automatic restart on failure. Press Ctrl+C to stop.

- **`start_skye.sh`** - System service-style manager
  ```bash
  ./scripts/start_skye.sh start    # Start Skye in background
  ./scripts/start_skye.sh stop     # Stop Skye
  ./scripts/start_skye.sh restart  # Restart Skye
  ./scripts/start_skye.sh status   # Check if running
  ```

- **`keep_alive.py`** - Monitor process that auto-restarts Skye
  - Checks every 30 seconds if Skye is responding
  - Automatically restarts on failure
  - Can be triggered manually via `/tmp/skye_restart` file

### Installation

- **`install.py`** - One-command setup script
  ```bash
  python3 scripts/install.py
  ```
  - Checks Python version
  - Installs dependencies
  - Creates `.env` from template
  - Starts the keep-alive monitor

### Utility Scripts

- **`youtube_audio_downloader.py`** - Download YouTube videos as MP3 audio
  ```bash
  python3 scripts/youtube_audio_downloader.py <youtube_url>
  ```
  - Downloads best quality audio from YouTube
  - Converts to MP3 (320kbps)
  - Used by the YouTube playlist copier feature

## Usage

### Quick Start (Recommended)
```bash
./scripts/launch_skye.sh
```

### Background Service
```bash
./scripts/start_skye.sh start
```

### Full Installation
```bash
python3 scripts/install.py
```

## Notes

- All scripts automatically detect the Skye root directory
- PID and log files are stored in the Skye root directory
- Scripts should be run from the Skye root directory or directly via path
