"""Currency/forex data endpoints"""
from __future__ import annotations
from datetime import datetime
from flask import jsonify, request, Response
import requests

from utils.api_client import (
    api_client, PERIOD_MAP, YAHOO_FINANCE_URL, USER_AGENT
)
from utils.cache import cache, CACHE_TIMEOUT_CHART

from .blueprint import dashboard_bp


@dashboard_bp.route('/api/currency-data')
@cache.cached(timeout=CACHE_TIMEOUT_CHART, query_string=True)
def get_currency_data() -> Response | tuple[Response, int]:
    """Get EUR/USD currency data using Yahoo Finance"""
    try:
        period = request.args.get('period', '1y')
        range_param, interval_param = PERIOD_MAP.get(period, ('1y', '1wk'))

        url = f'{YAHOO_FINANCE_URL}/EURUSD=X?range={range_param}&interval={interval_param}'
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
                    rates: list[float] = []

                    for ts, close in zip(timestamps, closes):
                        if close is not None:
                            dates.append(api_client.format_date(ts, period))
                            # Convert EUR/USD to USD/EUR
                            usd_eur_rate = 1 / close
                            rates.append(round(usd_eur_rate, 4))

                    if dates and rates:
                        return jsonify({
                            'dates': dates,
                            'rates': rates,
                            'pair': 'USD/EUR'
                        })

        return jsonify({'error': 'Currency data unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/currency-rate')
@cache.cached(timeout=CACHE_TIMEOUT_CHART)
def get_currency_rate() -> Response | tuple[Response, int]:
    """Get current USD to EUR rate using Yahoo Finance"""
    try:
        url = f'{YAHOO_FINANCE_URL}/EURUSD=X'
        headers = {'User-Agent': USER_AGENT}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    eur_usd_rate = result['meta']['regularMarketPrice']
                    if eur_usd_rate > 0:
                        usd_eur_rate = 1 / eur_usd_rate
                        return jsonify({'rate': round(usd_eur_rate, 4), 'pair': 'USD/EUR'})

        return jsonify({'error': 'Rate unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500
