"""Dashboard API blueprint package

This module provides endpoints for:
- Stock market data (AMZN)
- Currency exchange rates (USD/EUR)
- Cryptocurrency prices (XRP)
- Gold prices
- Portfolio calculations
- Sell recommendations
"""
from .blueprint import dashboard_bp

# Import all route modules to register endpoints
from . import stocks
from . import currency
from . import crypto
from . import gold
from . import portfolio
from . import recommendations

__all__ = ['dashboard_bp']
