"""Gold price data endpoints"""
from __future__ import annotations
from flask import jsonify, request, Response
import requests

from utils.api_client import (
    api_client, PERIOD_MAP, YAHOO_FINANCE_URL, USER_AGENT, DEFAULT_EUR_USD_RATE
)
from utils.cache import cache, CACHE_TIMEOUT_PRICE, CACHE_TIMEOUT_CHART

from .blueprint import dashboard_bp


def _get_eur_usd_rate() -> float:
    """Get EUR/USD rate with fallback"""
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(
            f'{YAHOO_FINANCE_URL}/EURUSD=X',
            headers=headers,
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


@dashboard_bp.route('/api/gold-data')
@cache.cached(timeout=CACHE_TIMEOUT_CHART, query_string=True)
def get_gold_data() -> Response | tuple[Response, int]:
    """Get Gold price data in EUR using Yahoo Finance"""
    try:
        period = request.args.get('period', '1y')
        range_param, interval_param = PERIOD_MAP.get(period, ('1y', '1wk'))

        headers = {'User-Agent': USER_AGENT}
        eur_usd_rate = _get_eur_usd_rate()

        # Try gold API with retry logic
        url = f'{YAHOO_FINANCE_URL}/GC=F?range={range_param}&interval={interval_param}'
        response = None

        for attempt in range(3):
            try:
                timeout = 5 + (attempt * 2)
                response = requests.get(url, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    if ('chart' in data and data['chart']['result'] and
                            len(data['chart']['result']) > 0):
                        result = data['chart']['result'][0]
                        if ('timestamp' in result and 'indicators' in result and
                                result['indicators']['quote'] and
                                len(result['indicators']['quote']) > 0):
                            break
            except requests.exceptions.RequestException:
                if attempt == 2:
                    raise
                continue

        if response and response.status_code == 200:
            data = response.json()
            if ('chart' in data and data['chart']['result'] and
                    len(data['chart']['result']) > 0):
                result = data['chart']['result'][0]
                if ('timestamp' in result and 'indicators' in result and
                        result['indicators']['quote'] and
                        len(result['indicators']['quote']) > 0):
                    timestamps = result['timestamp']
                    closes = result['indicators']['quote'][0]['close']

                    if timestamps and closes:
                        dates: list[str] = []
                        prices: list[float] = []

                        for ts, close in zip(timestamps, closes):
                            if close is not None and ts is not None:
                                try:
                                    dates.append(api_client.format_date(ts, period))
                                    price_eur = close / eur_usd_rate
                                    prices.append(round(price_eur, 2))
                                except (ValueError, OSError):
                                    continue

                        if len(dates) >= 5 and len(prices) >= 5:
                            return jsonify({
                                'dates': dates,
                                'prices': prices,
                                'symbol': 'Gold-EUR'
                            })

        return jsonify({'error': 'Gold chart data unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/gold-price')
@cache.cached(timeout=CACHE_TIMEOUT_PRICE)
def get_gold_price() -> Response | tuple[Response, int]:
    """Get current Gold price in EUR using Yahoo Finance"""
    try:
        headers = {'User-Agent': USER_AGENT}
        eur_usd_rate = _get_eur_usd_rate()

        # Try gold API with retry logic
        url = f'{YAHOO_FINANCE_URL}/GC=F'
        response = None

        for attempt in range(3):
            try:
                timeout = 5 + (attempt * 2)
                response = requests.get(url, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                if attempt == 2:
                    raise
                continue

        if response and response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']['result'] and len(data['chart']['result']) > 0:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    gold_usd = result['meta']['regularMarketPrice']
                    gold_eur = gold_usd / eur_usd_rate
                    return jsonify({'price': round(gold_eur, 2), 'symbol': 'Gold-EUR'})

        return jsonify({'error': 'Gold price unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500
