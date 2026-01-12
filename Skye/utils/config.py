"""Configuration management with caching and environment variable support"""
import json
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def load_config():
    """Load configuration from config.json, set env vars, then allow env overrides"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    config = {}
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    env_mappings = {
        'GEMINI_API_KEY': 'gemini_api_key',
        'YOUTUBE_API_KEY': 'youtube_api_key',
        'YOUTUBE_CLIENT_ID': ('youtube_oauth', 'client_id'),
        'YOUTUBE_CLIENT_SECRET': ('youtube_oauth', 'client_secret'),
        'USER_NAME': 'user_name'
    }
    
    placeholders = ['your_api_key_here', 'your_key_here', 'your_gemini_api_key_here', 'your_youtube_api_key_here', 'your_client_id_here', 'your_client_secret_here']
    
    # First: Load config.json values into environment if not already set
    for env_var, config_key in env_mappings.items():
        if env_var not in os.environ or os.getenv(env_var) in placeholders:
            if isinstance(config_key, tuple):
                value = config.get(config_key[0], {}).get(config_key[1])
            else:
                value = config.get(config_key)
            
            if value and value not in placeholders:
                os.environ[env_var] = value
    
    # Second: Allow environment variables to override config.json
    for env_var, config_key in env_mappings.items():
        value = os.getenv(env_var)
        if value and value not in placeholders:
            if isinstance(config_key, tuple):
                if config_key[0] not in config:
                    config[config_key[0]] = {}
                config[config_key[0]][config_key[1]] = value
            else:
                config[config_key] = value
    
    return config

def get_config_value(key, default=None):
    """Get a specific config value"""
    config = load_config()
    return config.get(key, default)

def clear_config_cache():
    """Clear config cache (useful after config updates)"""
    load_config.cache_clear()
