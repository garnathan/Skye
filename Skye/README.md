# Skye

A modular web application that automatically discovers and displays pages based on directory structure.

## Quick Start

### Option 1: Simple Start
```bash
python3 app.py
```

### Option 2: Always Running (Recommended)
```bash
./scripts/launch_skye.sh
```

### Option 3: Manual Control
```bash
./scripts/start_skye.sh start    # Start Skye
./scripts/start_skye.sh status   # Check status
./scripts/start_skye.sh stop     # Stop Skye
./scripts/start_skye.sh restart  # Restart Skye
```

### Option 4: Full Installation
```bash
python3 scripts/install.py
```

Visit http://localhost:5001

## Keep-Alive Features

- **Auto-restart**: Automatically restarts if Skye crashes
- **Health monitoring**: Checks every 30 seconds if Skye is responding
- **Process management**: Tracks PID and handles clean shutdowns
- **Logging**: Logs output to `skye.log`

## Adding New Pages

To add a new page/tab, simply create a new directory in the `pages/` folder:

### Method 1: Static HTML Content

1. Create directory: `pages/my-new-page/`
2. Add `config.py`:
```python
PAGE_NAME = "My New Page"
PAGE_DESCRIPTION = "Description of what this page does"
PAGE_ICON = "fas fa-star"  # FontAwesome icon class
```
3. Add `content.html` with your HTML content

### Method 2: Dynamic Python Content

1. Create directory: `pages/my-dynamic-page/`
2. Add `config.py` (same as above)
3. Add `page.py`:
```python
def get_content():
    return {
        'html': '''
        <h2>Dynamic Content</h2>
        <p>Generated at runtime</p>
        '''
    }
```

## Page Structure

```
pages/
├── dashboard/
│   ├── config.py      # Page configuration
│   └── page.py        # Dynamic content generator
├── tools/
│   ├── config.py      # Page configuration
│   └── content.html   # Static HTML content
├── reports/
│   ├── config.py      # Page configuration
│   └── page.py        # Dynamic content generator
└── q-portal/
    ├── config.py      # Page configuration
    └── content.html   # Q chat interface
```

## Features

- **Automatic Discovery**: Pages are automatically detected and added to tabs
- **Two Content Types**: Static HTML or dynamic Python-generated content
- **Responsive Design**: Works on desktop and mobile
- **Easy Styling**: Each page can include its own CSS and JavaScript
- **Icon Support**: FontAwesome icons for tabs and pages
- **Q Integration**: Real Amazon Q chat interface
- **Always Running**: Keep-alive monitoring ensures uptime

## Configuration Options

In `config.py`:
- `PAGE_NAME`: Display name in tab
- `PAGE_DESCRIPTION`: Description shown on welcome screen
- `PAGE_ICON`: FontAwesome icon class

## Content Methods

### Static HTML (`content.html`)
- Simple HTML file
- Can include `<style>` and `<script>` tags
- Good for simple, static content

### Dynamic Python (`page.py`)
- Must have `get_content()` function
- Returns dictionary with `html` key
- Can generate content dynamically
- Access to full Python ecosystem

## Examples

See the included example pages:
- `dashboard/` - Dynamic Python content with metrics
- `tools/` - Static HTML with interactive elements
- `reports/` - Dynamic Python content with data processing
- `q-portal/` - Real Amazon Q chat interface