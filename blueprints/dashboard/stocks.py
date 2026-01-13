"""Stock market data endpoints"""
from __future__ import annotations
from flask import jsonify, request, current_app, Response

from utils.api_client import api_client, PERIOD_MAP
from utils.cache import cache, CACHE_TIMEOUT_PRICE, CACHE_TIMEOUT_CHART
from utils import handle_api_errors

from .blueprint import dashboard_bp


@dashboard_bp.route('/api/stock-data')
@cache.cached(timeout=CACHE_TIMEOUT_CHART, query_string=True)
@handle_api_errors
def get_stock_data() -> Response | tuple[Response, int]:
    """Get stock data using Yahoo Finance API"""
    symbol = request.args.get('symbol', 'AMZN')
    period = request.args.get('period', '1y')
    current_app.logger.info(f"Stock data requested for {symbol}, period: {period}")

    range_param, interval_param = PERIOD_MAP.get(period, ('1y', '1wk'))

    data = api_client.get_yahoo_chart_data(symbol, range_param, interval_param)
    dates, prices = api_client.parse_yahoo_chart(data, period)

    if dates and prices:
        prices = [round(p, 2) for p in prices]
        current_app.logger.info(f"Stock data retrieved for {symbol}: {len(dates)} data points")
        return jsonify({'dates': dates, 'prices': prices, 'symbol': symbol})

    current_app.logger.error(f"Stock data unavailable for {symbol}")
    return jsonify({'error': 'Chart data unavailable'}), 503


@dashboard_bp.route('/api/current-price')
@cache.cached(timeout=CACHE_TIMEOUT_PRICE, query_string=True)
def get_current_price() -> Response | tuple[Response, int]:
    """Get current stock price using Yahoo Finance API"""
    try:
        symbol = request.args.get('symbol', 'AMZN')
        price = api_client.get_yahoo_current_price(symbol)

        if price is not None:
            return jsonify({'price': round(price, 2), 'symbol': symbol})

        return jsonify({'error': 'Price unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500
