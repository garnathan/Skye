"""Shared API client utilities for external API calls"""
import requests
from functools import lru_cache
from datetime import datetime

class APIClient:
    """Centralized API client with retry logic and caching"""
    
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.timeout = 10
    
    def fetch_with_retry(self, url, retries=3):
        """Fetch URL with retry logic"""
        for attempt in range(retries):
            try:
                timeout = self.timeout + (attempt * 2)
                response = requests.get(url, headers=self.headers, timeout=timeout)
                if response.status_code == 200:
                    return response.json()
            except requests.exceptions.RequestException:
                if attempt == retries - 1:
                    raise
        return None
    
    def get_yahoo_chart_data(self, symbol, range_param='1y', interval_param='1wk'):
        """Get chart data from Yahoo Finance"""
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_param}&interval={interval_param}'
        return self.fetch_with_retry(url)
    
    def get_yahoo_current_price(self, symbol):
        """Get current price from Yahoo Finance"""
        data = self.get_yahoo_chart_data(symbol, '1d', '5m')
        if data and 'chart' in data and data['chart']['result']:
            result = data['chart']['result'][0]
            if 'meta' in result and 'regularMarketPrice' in result['meta']:
                return result['meta']['regularMarketPrice']
        return None
    
    def parse_yahoo_chart(self, data, period='1y'):
        """Parse Yahoo Finance chart data into dates and values"""
        if not data or 'chart' not in data or not data['chart']['result']:
            return None, None
        
        result = data['chart']['result'][0]
        if 'timestamp' not in result or 'indicators' not in result:
            return None, None
        
        timestamps = result['timestamp']
        closes = result['indicators']['quote'][0]['close']
        
        dates = []
        values = []
        
        for ts, close in zip(timestamps, closes):
            if close is not None and ts is not None:
                try:
                    date_obj = datetime.fromtimestamp(ts)
                    if period == '1d':
                        dates.append(date_obj.strftime('%H:%M'))
                    elif period == '1wk':
                        dates.append(date_obj.strftime('%a %H:%M'))
                    elif period == '1mo':
                        dates.append(date_obj.strftime('%b %d'))
                    else:
                        dates.append(date_obj.strftime('%b %d'))
                    values.append(close)
                except (ValueError, OSError):
                    continue
        
        return dates, values
    
    @lru_cache(maxsize=32)
    def get_eur_usd_rate(self):
        """Get EUR/USD exchange rate with caching"""
        try:
            data = self.get_yahoo_chart_data('EURUSD=X', '1d', '5m')
            if data and 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    return result['meta']['regularMarketPrice']
        except:
            pass
        
        # Fallback to alternative API
        try:
            response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR', timeout=3)
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and 'USD' in data['rates']:
                    return data['rates']['USD']
        except:
            pass
        
        return 1.1  # Default fallback

# Global instance
api_client = APIClient()
