# Development Guide

## Prerequisites

- Python 3.9+
- pip

## Quick Setup

```bash
# Clone and enter directory
cd Skye

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp config/.env.example .env

# Edit .env with your API keys
# (see Configuration section below)

# Run the app
python3 app.py
```

Visit http://localhost:5001

## Configuration

### Required API Keys

| Key | Purpose | How to Get |
|-----|---------|------------|
| `GEMINI_API_KEY` | AI chat functionality | [Google AI Studio](https://aistudio.google.com/apikey) |

### Optional API Keys

| Key | Purpose | How to Get |
|-----|---------|------------|
| `YOUTUBE_API_KEY` | YouTube playlist features | [Google Cloud Console](https://console.cloud.google.com/) |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth | Google Cloud Console > OAuth 2.0 |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth | Google Cloud Console > OAuth 2.0 |

### Portfolio Settings

Configure in `.env` for the Market Dashboard:

```env
AMZN_SHARES=100
CASH_ASSETS_EUR=5000
XRP_QUANTITY=500
```

## Project Structure

```
Skye/
├── app.py                 # Main Flask application
├── blueprints/            # API route modules
│   ├── dashboard/         # Dashboard API endpoints
│   │   ├── stocks.py
│   │   ├── currency.py
│   │   ├── crypto.py
│   │   ├── gold.py
│   │   ├── portfolio.py
│   │   └── recommendations.py
│   ├── weather.py
│   ├── gemini.py
│   ├── youtube.py
│   ├── todo.py
│   └── ...
├── pages/                 # Auto-discovered page modules
│   ├── home/
│   ├── dashboard/
│   ├── weather/
│   └── ...
├── utils/                 # Shared utilities
│   ├── api_client.py      # External API client
│   ├── cache.py           # Flask-Caching setup
│   ├── circuit_breaker.py # Resilience patterns
│   ├── decorators.py      # Error handling decorators
│   └── logging_setup.py   # Logging configuration
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   └── index.html
├── config/
│   └── .env.example
└── docs/
    ├── API.md             # API reference
    └── DEVELOPMENT.md     # This file
```

## Adding a New Page

Pages are auto-discovered from the `pages/` directory.

### Option 1: Static HTML

```
pages/my-page/
├── config.py
└── content.html
```

**config.py:**
```python
PAGE_NAME = "My Page"
PAGE_DESCRIPTION = "What this page does"
PAGE_ICON = "fas fa-star"  # FontAwesome icon
ORDER = 10  # Optional: sort order (lower = first)
```

**content.html:**
```html
<div class="my-page">
    <h2>My Page</h2>
    <p>Content here...</p>
</div>
<style>
    .my-page { padding: 1rem; }
</style>
```

### Option 2: Dynamic Python

```
pages/my-page/
├── config.py
└── page.py
```

**page.py:**
```python
def get_content():
    # Generate content dynamically
    data = fetch_some_data()
    return {
        'html': f'''
        <div class="my-page">
            <h2>Dynamic Content</h2>
            <p>Data: {data}</p>
        </div>
        '''
    }
```

## Adding a New API Endpoint

1. Create or edit a blueprint in `blueprints/`
2. Use the error handling decorator:

```python
from flask import Blueprint, jsonify
from utils.decorators import handle_api_errors
from utils.cache import cache, CACHE_TIMEOUT_PRICE

my_bp = Blueprint('my_bp', __name__)

@my_bp.route('/api/my-endpoint')
@handle_api_errors
@cache.cached(timeout=CACHE_TIMEOUT_PRICE)
def my_endpoint():
    # Your logic here
    return jsonify({'data': 'value'})
```

3. Register the blueprint in `app.py`:

```python
from blueprints.my_module import my_bp
app.register_blueprint(my_bp)
```

## Caching

Response caching is handled via Flask-Caching. Use predefined timeouts:

```python
from utils.cache import cache, CACHE_TIMEOUT_PRICE, CACHE_TIMEOUT_CHART

@cache.cached(timeout=CACHE_TIMEOUT_PRICE)  # 60 seconds
def get_price(): ...

@cache.cached(timeout=CACHE_TIMEOUT_CHART)  # 300 seconds
def get_chart_data(): ...
```

Available timeouts:
- `CACHE_TIMEOUT_PRICE`: 60s - Real-time price data
- `CACHE_TIMEOUT_PORTFOLIO`: 120s - Portfolio calculations
- `CACHE_TIMEOUT_CHART`: 300s - Historical chart data
- `CACHE_TIMEOUT_RECOMMENDATION`: 600s - AI recommendations
- `CACHE_TIMEOUT_WEATHER`: 900s - Weather data
- `CACHE_TIMEOUT_SUN`: 3600s - Sunrise/sunset times

## Circuit Breaker

External APIs are protected by circuit breakers to prevent cascade failures:

```python
from utils.api_client import api_client
from utils.circuit_breaker import CircuitOpenError

try:
    data = api_client.fetch_with_retry(url, circuit_name='yahoo_finance')
except CircuitOpenError as e:
    # Service is temporarily unavailable
    # e.recovery_in tells you when to retry
    pass
```

Circuit states:
- **Closed**: Normal operation
- **Open**: Too many failures, requests fail immediately
- **Half-Open**: Testing if service recovered

## Dark Mode Support

When adding new components, include dark mode styles:

```css
.my-component {
    background: white;
    color: #333;
}

[data-theme="dark"] .my-component {
    background: var(--bg-card);
    color: var(--text-primary);
}
```

CSS variables available in dark mode:
- `--bg-primary`: Main background
- `--bg-secondary`: Secondary background
- `--bg-card`: Card/widget background
- `--text-primary`: Main text color
- `--text-secondary`: Muted text color
- `--border-color`: Border color

## Debugging

### View Logs
Visit the Logs page in the UI or:
```bash
curl http://localhost:5001/api/logs?level=error
```

### Health Check
```bash
curl http://localhost:5001/health
```

### Clear Cache
Restart the server to clear all cached data.

## Keyboard Shortcuts

During development, use these shortcuts:
- `1-9`: Switch tabs
- `D`: Toggle dark mode
- `R`: Refresh current page
- `?`: Show shortcut help
