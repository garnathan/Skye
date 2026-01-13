"""
Cache configuration for Skye application
Uses Flask-Caching for response caching with TTL support
"""
from flask_caching import Cache

# Cache instance - initialized with app in init_cache()
cache = Cache()

# Cache timeout constants (in seconds)
CACHE_TIMEOUT_PRICE = 60        # Current prices - near real-time
CACHE_TIMEOUT_CHART = 300       # Chart data - 5 minutes
CACHE_TIMEOUT_PORTFOLIO = 120   # Portfolio calculations - 2 minutes
CACHE_TIMEOUT_RECOMMENDATION = 600  # Recommendations - 10 minutes
CACHE_TIMEOUT_WEATHER = 900     # Weather data - 15 minutes
CACHE_TIMEOUT_SUN = 3600        # Sun times - 1 hour


def init_cache(app):
    """Initialize cache with Flask app"""
    cache.init_app(app, config={
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 300
    })
    return cache
