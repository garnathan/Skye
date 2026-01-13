"""Shared API client utilities for external API calls"""
from __future__ import annotations
import requests
from functools import lru_cache
from datetime import datetime
from typing import Any, Callable
import time

from utils.circuit_breaker import circuit_registry, CircuitOpenError

# =============================================================================
# CONSTANTS
# =============================================================================

# Circuit breaker names
CIRCUIT_YAHOO = 'yahoo_finance'
CIRCUIT_EXCHANGE = 'exchange_rate'

# Timeout configurations (seconds)
TIMEOUT_SHORT = 5      # Quick lookups
TIMEOUT_DEFAULT = 10   # Standard API calls
TIMEOUT_LONG = 30      # Heavy operations (downloads, large data)

# Period mapping for Yahoo Finance API
PERIOD_MAP: dict[str, tuple[str, str]] = {
    '1d': ('1d', '5m'),
    '1wk': ('5d', '1h'),
    '1mo': ('1mo', '1d'),
    '1y': ('1y', '1wk')
}

# Stock score thresholds: (min_change_pct, score)
STOCK_SCORE_THRESHOLDS: list[tuple[float, int, str]] = [
    (30, 95, "Exceptional growth"),
    (20, 85, "Strong growth"),
    (10, 75, "Good growth"),
    (5, 65, "Moderate growth"),
    (0, 55, "Slight growth"),
    (-5, 45, "Minor decline"),
    (-10, 35, "Moderate decline"),
    (-20, 25, "Significant decline"),
    (-999, 10, "Major decline")
]

# Currency score thresholds: (min_change_pct, score, description)
CURRENCY_SCORE_THRESHOLDS: list[tuple[float, int, str]] = [
    (5, 80, "USD very strong"),
    (2, 70, "USD strengthening"),
    (-1, 60, "USD stable"),
    (-3, 40, "USD weakening"),
    (-999, 20, "USD very weak")
]

# API defaults
DEFAULT_EUR_USD_RATE: float = 1.1
REQUEST_TIMEOUT: int = 10
USER_AGENT: str = 'Mozilla/5.0'

# Yahoo Finance base URL
YAHOO_FINANCE_URL: str = 'https://query1.finance.yahoo.com/v8/finance/chart'


class APIClient:
    """Centralized API client with retry logic and caching"""

    def __init__(self) -> None:
        self.headers: dict[str, str] = {'User-Agent': USER_AGENT}
        self.timeout: int = REQUEST_TIMEOUT

    def fetch_with_retry(
        self,
        url: str,
        retries: int = 3,
        circuit_name: str = CIRCUIT_YAHOO
    ) -> dict[str, Any] | None:
        """Fetch URL with retry logic and circuit breaker protection"""
        circuit = circuit_registry.get(circuit_name)

        # Check if circuit is open - fail fast with clear error
        circuit.check_state()

        for attempt in range(retries):
            try:
                timeout = self.timeout + (attempt * 2)
                response = requests.get(url, headers=self.headers, timeout=timeout)
                if response.status_code == 200:
                    circuit.record_success()
                    return response.json()
            except requests.exceptions.RequestException:
                if attempt == retries - 1:
                    circuit.record_failure()
                    raise

        circuit.record_failure()
        return None

    def get_yahoo_chart_data(
        self,
        symbol: str,
        range_param: str = '1y',
        interval_param: str = '1wk'
    ) -> dict[str, Any] | None:
        """Get chart data from Yahoo Finance"""
        url = f'{YAHOO_FINANCE_URL}/{symbol}?range={range_param}&interval={interval_param}'
        return self.fetch_with_retry(url)

    def get_yahoo_current_price(self, symbol: str) -> float | None:
        """Get current price from Yahoo Finance"""
        data = self.get_yahoo_chart_data(symbol, '1d', '5m')
        if data and 'chart' in data and data['chart']['result']:
            result = data['chart']['result'][0]
            if 'meta' in result and 'regularMarketPrice' in result['meta']:
                return result['meta']['regularMarketPrice']
        return None

    def format_date(self, timestamp: int, period: str) -> str:
        """Format timestamp based on period for chart display"""
        date_obj = datetime.fromtimestamp(timestamp)
        if period == '1d':
            return date_obj.strftime('%H:%M')
        elif period == '1wk':
            return date_obj.strftime('%a %H:%M')
        elif period == '1mo':
            return date_obj.strftime('%b %d')
        else:
            return date_obj.strftime('%b %d')

    def parse_yahoo_chart(
        self,
        data: dict[str, Any] | None,
        period: str = '1y'
    ) -> tuple[list[str], list[float]] | tuple[None, None]:
        """Parse Yahoo Finance chart data into dates and values"""
        if not data or 'chart' not in data or not data['chart']['result']:
            return None, None

        result = data['chart']['result'][0]
        if 'timestamp' not in result or 'indicators' not in result:
            return None, None

        timestamps = result['timestamp']
        closes = result['indicators']['quote'][0]['close']

        dates: list[str] = []
        values: list[float] = []

        for ts, close in zip(timestamps, closes):
            if close is not None and ts is not None:
                try:
                    dates.append(self.format_date(ts, period))
                    values.append(close)
                except (ValueError, OSError):
                    continue

        return dates, values

    def calculate_stock_score(self, change_pct: float) -> tuple[int, str]:
        """Calculate stock score and trend description from percentage change"""
        for threshold, score, description in STOCK_SCORE_THRESHOLDS:
            if change_pct >= threshold:
                sign = '+' if change_pct >= 0 else ''
                return score, f"{description} ({sign}{change_pct:.1f}%)"
        return 10, f"Major decline ({change_pct:.1f}%)"

    def calculate_currency_score(self, change_pct: float) -> tuple[int, str]:
        """Calculate currency score and trend description from percentage change"""
        for threshold, score, description in CURRENCY_SCORE_THRESHOLDS:
            if change_pct >= threshold:
                sign = '+' if change_pct >= 0 else ''
                return score, f"{description} ({sign}{change_pct:.1f}%)"
        return 20, f"USD very weak ({change_pct:.1f}%)"

    @lru_cache(maxsize=32)
    def get_eur_usd_rate(self) -> float:
        """Get EUR/USD exchange rate with caching"""
        try:
            data = self.get_yahoo_chart_data('EURUSD=X', '1d', '5m')
            if data and 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    return result['meta']['regularMarketPrice']
        except (requests.RequestException, KeyError, ValueError):
            pass

        # Fallback to alternative API
        try:
            response = requests.get(
                'https://api.exchangerate-api.com/v4/latest/EUR',
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and 'USD' in data['rates']:
                    return data['rates']['USD']
        except (requests.RequestException, KeyError, ValueError):
            pass

        return DEFAULT_EUR_USD_RATE

    def get_eur_usd_rate_with_fallback(self) -> float:
        """Get EUR/USD rate with multiple fallback attempts (uncached)"""
        # Try Yahoo Finance first
        try:
            response = requests.get(
                f'{YAHOO_FINANCE_URL}/EURUSD=X',
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and data['chart']['result']:
                    result = data['chart']['result'][0]
                    if 'meta' in result and 'regularMarketPrice' in result['meta']:
                        return result['meta']['regularMarketPrice']
        except (requests.RequestException, KeyError, ValueError):
            pass

        # Fallback to alternative API
        try:
            response = requests.get(
                'https://api.exchangerate-api.com/v4/latest/EUR',
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and 'USD' in data['rates']:
                    return data['rates']['USD']
        except (requests.RequestException, KeyError, ValueError):
            pass

        return DEFAULT_EUR_USD_RATE


# =============================================================================
# FETCH WITH TIMEOUT HELPER
# =============================================================================

def fetch_with_timeout(
    url: str,
    timeout: int = TIMEOUT_DEFAULT,
    headers: dict[str, str] | None = None,
    method: str = 'GET',
    **kwargs
) -> requests.Response:
    """
    Make HTTP request with consistent timeout handling.
    Raises requests.Timeout if request exceeds timeout.
    """
    default_headers = {'User-Agent': USER_AGENT}
    if headers:
        default_headers.update(headers)

    return requests.request(
        method,
        url,
        headers=default_headers,
        timeout=timeout,
        **kwargs
    )


def retry_with_backoff(
    fn: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0
) -> Any:
    """
    Retry a function with exponential backoff.
    Returns the result or raises the last exception.
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return fn()
        except (requests.RequestException, TimeoutError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                time.sleep(delay)

    raise last_exception


# Global instance
api_client = APIClient()
