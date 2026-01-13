# Skye

A personal dashboard and assistant that brings together the tools and information I use daily into a single, locally-hosted interface.

## What It Does

- **Stock Market Dashboard** - Track portfolio value, stock prices (AMZN, ORCL), EUR/USD rates, XRP, and gold with interactive charts
- **Music Recommendations** - Discover new music based on listening history
- **Weather** - Local weather and sunrise/sunset times
- **Gemini AI Chat** - Chat interface for Google's Gemini AI
- **YouTube Tools** - Playlist management and audio downloading
- **To-Do List** - Simple task tracking
- **Logs Viewer** - Monitor application logs

## Is This For You?

Probably not as-is. Skye is built for my specific needs - tracking my particular stocks, my portfolio configuration, my preferred tools. The included pages are tailored to how I work.

**However**, the architecture is designed to be easily adapted. The page system auto-discovers modules, so you can:
1. Delete the pages you don't need
2. Add your own pages with your own functionality
3. Keep the infrastructure (caching, error handling, dark mode, etc.)

Think of it as a template for building your own personal dashboard.

## Documentation

- [API Reference](docs/API.md) - Complete API endpoint documentation
- [Development Guide](docs/DEVELOPMENT.md) - Setup, architecture, and how to add pages

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp config/.env.example .env
# Edit .env with your API keys

# Run
python3 app.py
```

Visit http://localhost:5001

## Configuration

### API Keys

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Gemini AI chat |
| `YOUTUBE_API_KEY` | YouTube features |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth |

### Portfolio (for Market Dashboard)

| Variable | Purpose |
|----------|---------|
| `AMZN_SHARES` | Amazon shares owned |
| `CASH_ASSETS_EUR` | EUR cash holdings |
| `XRP_QUANTITY` | XRP quantity |

## Adding Your Own Pages

Create a directory in `pages/` with:

**config.py:**
```python
PAGE_NAME = "My Page"
PAGE_DESCRIPTION = "What it does"
PAGE_ICON = "fas fa-star"
```

**Either** `content.html` (static) **or** `page.py` (dynamic):
```python
def get_content():
    return {'html': '<h2>Hello</h2>'}
```

Pages are auto-discovered on startup.

## Features

- **Auto-discovery** - Drop a page folder in `pages/`, it appears automatically
- **Dark mode** - Toggle with the moon icon or press `D`
- **Keyboard shortcuts** - Press `?` to see them
- **Caching** - API responses are cached for performance
- **Circuit breaker** - Graceful handling when external APIs fail
- **Health endpoint** - `/health` for monitoring
- **Keep-alive** - Optional scripts to auto-restart on crash

## Running Options

```bash
# Simple
python3 app.py

# With auto-restart on crash
./scripts/launch_skye.sh

# Manual control
./scripts/start_skye.sh start|stop|status|restart
```
