def get_content():
    """Return the HTML content for the home page"""
    import os
    import json
    
    # Load config to get user name
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
    user_name = "Friend"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            user_name = config.get('user_name', 'Friend')
    except:
        pass
    
    html_content = f'''
    <div class="home-container">
        <div class="welcome-section">
            <h1>Hey {user_name}!</h1>
            <p>What would you like to do?</p>
        </div>
        
        <div class="quick-links">
            <div class="link-card" onclick="switchTab('todo')">
                <div class="card-icon">✅</div>
                <h3>Todo List</h3>
                <p>Manage your tasks and notes</p>
            </div>

            <div class="link-card" onclick="switchTab('weather')">
                <div class="card-icon">☀️</div>
                <h3>Weather</h3>
                <p>Live weather for Killiney, Dublin</p>
            </div>

            <div class="link-card" onclick="switchTab('dashboard')">
                <div class="card-icon">📈</div>
                <h3>Stock Market</h3>
                <p>View AMZN stock and currency data</p>
            </div>

            <div class="link-card" onclick="switchTab('q-portal')">
                <div class="card-icon">🧠</div>
                <h3>Gemini Portal</h3>
                <p>Chat with AI assistant</p>
            </div>

            <div class="link-card" onclick="switchTab('tools')">
                <div class="card-icon">🛠️</div>
                <h3>Tools</h3>
                <p>YouTube playlist copier and more</p>
            </div>

            <div class="link-card" onclick="switchTab('music-next')">
                <div class="card-icon">🎵</div>
                <h3>Music Next</h3>
                <p>Discover similar artists and music</p>
            </div>

            <div class="link-card" onclick="switchTab('logs')">
                <div class="card-icon">📋</div>
                <h3>Logs</h3>
                <p>View system logs and activity</p>
            </div>
        </div>
    </div>
    
    <style>
    .home-container {{
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }}
    
    .welcome-section {{
        text-align: center;
        margin-bottom: 3rem;
    }}
    
    .welcome-section h1 {{
        font-size: 3rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .welcome-section p {{
        font-size: 1.2rem;
        color: #666;
    }}
    
    .quick-links {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }}
    
    .link-card {{
        background: white;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e1e5e9;
    }}
    
    .link-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }}
    
    .card-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
    }}
    
    .link-card h3 {{
        margin: 0.5rem 0;
        color: #333;
        font-size: 1.3rem;
    }}
    
    .link-card p {{
        color: #666;
        margin: 0;
        font-size: 0.9rem;
    }}
    </style>
    '''
    
    return {
        'html': html_content
    }