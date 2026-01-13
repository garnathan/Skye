"""Cryptocurrency data endpoints (XRP)"""
from __future__ import annotations
from flask import jsonify, request, Response
import requests

from utils.api_client import api_client, PERIOD_MAP, YAHOO_FINANCE_URL, USER_AGENT
from utils.cache import cache, CACHE_TIMEOUT_PRICE, CACHE_TIMEOUT_CHART

from .blueprint import dashboard_bp


@dashboard_bp.route('/api/xrp-data')
@cache.cached(timeout=CACHE_TIMEOUT_CHART, query_string=True)
def get_xrp_data() -> Response | tuple[Response, int]:
    """Get XRP price data in EUR using Yahoo Finance"""
    try:
        period = request.args.get('period', '1y')
        range_param, interval_param = PERIOD_MAP.get(period, ('1y', '1wk'))

        url = f'{YAHOO_FINANCE_URL}/XRP-EUR?range={range_param}&interval={interval_param}'
        headers = {'User-Agent': USER_AGENT}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'timestamp' in result and 'indicators' in result:
                    timestamps = result['timestamp']
                    closes = result['indicators']['quote'][0]['close']

                    dates: list[str] = []
                    prices: list[float] = []

                    for ts, close in zip(timestamps, closes):
                        if close is not None:
                            dates.append(api_client.format_date(ts, period))
                            prices.append(round(close, 4))

                    if dates and prices:
                        return jsonify({
                            'dates': dates,
                            'prices': prices,
                            'symbol': 'XRP-EUR'
                        })

        return jsonify({'error': 'XRP chart data unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/xrp-price')
@cache.cached(timeout=CACHE_TIMEOUT_PRICE)
def get_xrp_price() -> Response | tuple[Response, int]:
    """Get current XRP price in EUR using Yahoo Finance"""
    try:
        url = f'{YAHOO_FINANCE_URL}/XRP-EUR'
        headers = {'User-Agent': USER_AGENT}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    price = result['meta']['regularMarketPrice']
                    return jsonify({'price': round(price, 4), 'symbol': 'XRP-EUR'})

        return jsonify({'error': 'XRP price unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500
