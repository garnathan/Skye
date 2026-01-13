"""Portfolio value calculation endpoints"""
from __future__ import annotations
from flask import jsonify, request, Response
import requests

from utils.api_client import api_client, PERIOD_MAP, YAHOO_FINANCE_URL, USER_AGENT
from utils.config import get_config_value
from utils.cache import cache, CACHE_TIMEOUT_PORTFOLIO, CACHE_TIMEOUT_CHART

from .blueprint import dashboard_bp


@dashboard_bp.route('/api/portfolio-value')
@cache.cached(timeout=CACHE_TIMEOUT_PORTFOLIO, query_string=True)
def get_portfolio_value() -> Response | tuple[Response, int]:
    """Get portfolio value of AMZN shares in EUR over time"""
    try:
        portfolio = get_config_value('portfolio', {})
        amzn_shares = int(portfolio.get('amzn_shares', 0))

        period = request.args.get('period', '1y')
        range_param, interval_param = PERIOD_MAP.get(period, ('1y', '1wk'))

        headers = {'User-Agent': USER_AGENT}

        # Get AMZN data with selected period
        amzn_url = f'{YAHOO_FINANCE_URL}/AMZN?range={range_param}&interval={interval_param}'
        amzn_response = requests.get(amzn_url, headers=headers, timeout=10)

        # Get current EUR/USD rate
        eur_url = f'{YAHOO_FINANCE_URL}/EURUSD=X'
        eur_response = requests.get(eur_url, headers=headers, timeout=10)

        if amzn_response.status_code != 200 or eur_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data'}), 500

        # Get current EUR/USD rate
        eur_usd_rate = 1.1  # Default fallback
        eur_data = eur_response.json()
        if 'chart' in eur_data and eur_data['chart']['result']:
            eur_result = eur_data['chart']['result'][0]
            if 'meta' in eur_result and 'regularMarketPrice' in eur_result['meta']:
                eur_usd_rate = eur_result['meta']['regularMarketPrice']

        # Convert EUR/USD to USD/EUR
        usd_eur_rate = 1 / eur_usd_rate

        amzn_data = amzn_response.json()
        if 'chart' in amzn_data and amzn_data['chart']['result']:
            result = amzn_data['chart']['result'][0]
            if 'timestamp' in result and 'indicators' in result:
                timestamps = result['timestamp']
                closes = result['indicators']['quote'][0]['close']

                dates: list[str] = []
                values: list[float] = []

                for ts, close in zip(timestamps, closes):
                    if close is not None:
                        dates.append(api_client.format_date(ts, period))
                        portfolio_value_eur = amzn_shares * close * usd_eur_rate
                        values.append(round(portfolio_value_eur, 2))

                if dates and values:
                    current_value = values[-1]
                    start_value = values[0]
                    change_amount = current_value - start_value
                    change_percent = ((current_value - start_value) / start_value) * 100

                    return jsonify({
                        'dates': dates,
                        'values': values,
                        'currentValue': round(current_value, 2),
                        'changeAmount': round(change_amount, 2),
                        'changePercent': round(change_percent, 2),
                        'usdEurRate': round(usd_eur_rate, 4),
                        'shares': amzn_shares
                    })

        return jsonify({'error': 'Portfolio data unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/cash-assets-value')
@cache.cached(timeout=CACHE_TIMEOUT_CHART, query_string=True)
def get_cash_assets_value() -> Response | tuple[Response, int]:
    """Get historical value of EUR cash assets converted to what they were worth over time"""
    try:
        portfolio = get_config_value('portfolio', {})
        eur_cash = int(portfolio.get('cash_assets_eur', 0))

        period = request.args.get('period', '1y')
        range_param, interval_param = PERIOD_MAP.get(period, ('1y', '1wk'))

        headers = {'User-Agent': USER_AGENT}

        # Get EUR/USD data with selected period
        eur_url = f'{YAHOO_FINANCE_URL}/EURUSD=X?range={range_param}&interval={interval_param}'
        eur_response = requests.get(eur_url, headers=headers, timeout=10)

        if eur_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch exchange rate data'}), 500

        eur_data = eur_response.json()
        if 'chart' in eur_data and eur_data['chart']['result']:
            result = eur_data['chart']['result'][0]
            if 'timestamp' in result and 'indicators' in result:
                timestamps = result['timestamp']
                eur_usd_rates = result['indicators']['quote'][0]['close']

                # Get current rate to calculate the USD equivalent
                current_eur_usd_rate = eur_usd_rates[-1] if eur_usd_rates[-1] else 1.17
                usd_cash = eur_cash * current_eur_usd_rate

                dates: list[str] = []
                values: list[float] = []

                for ts, eur_usd_rate in zip(timestamps, eur_usd_rates):
                    if eur_usd_rate is not None:
                        dates.append(api_client.format_date(ts, period))
                        usd_eur_rate = 1 / eur_usd_rate
                        cash_value_eur = usd_cash * usd_eur_rate
                        values.append(round(cash_value_eur, 2))

                if dates and values:
                    current_value = values[-1]
                    start_value = values[0]
                    change_amount = current_value - start_value
                    change_percent = ((current_value - start_value) / start_value) * 100
                    current_usd_eur_rate = 1 / current_eur_usd_rate

                    return jsonify({
                        'dates': dates,
                        'values': values,
                        'eurAmount': eur_cash,
                        'currentValue': round(current_value, 2),
                        'changeAmount': round(change_amount, 2),
                        'changePercent': round(change_percent, 2),
                        'usdEurRate': round(current_usd_eur_rate, 4)
                    })

        return jsonify({'error': 'Cash assets data unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500
