"""Sell recommendation analysis endpoints"""
from __future__ import annotations
from datetime import datetime
from flask import jsonify, Response
import requests

from utils.api_client import api_client, YAHOO_FINANCE_URL, USER_AGENT
from utils.cache import cache, CACHE_TIMEOUT_RECOMMENDATION

from .blueprint import dashboard_bp


@dashboard_bp.route('/api/sell-recommendation')
@cache.cached(timeout=CACHE_TIMEOUT_RECOMMENDATION)
def get_sell_recommendation() -> Response | tuple[Response, int]:
    """Analyze AMZN stock and USD/EUR trends to recommend selling with percentage score"""
    try:
        headers = {'User-Agent': USER_AGENT}

        # Get 12 months of AMZN data
        amzn_url = f'{YAHOO_FINANCE_URL}/AMZN?range=1y&interval=1wk'
        amzn_response = requests.get(amzn_url, headers=headers, timeout=10)

        # Get 12 months of EUR/USD data
        eur_url = f'{YAHOO_FINANCE_URL}/EURUSD=X?range=1y&interval=1wk'
        eur_response = requests.get(eur_url, headers=headers, timeout=10)

        stock_score = 50
        currency_score = 50
        stock_trend = "Unknown"
        currency_trend = "Unknown"

        # Analyze AMZN stock trend
        if amzn_response.status_code == 200:
            amzn_data = amzn_response.json()
            if 'chart' in amzn_data and amzn_data['chart']['result']:
                result = amzn_data['chart']['result'][0]
                if 'indicators' in result:
                    closes = result['indicators']['quote'][0]['close']
                    valid_closes = [c for c in closes if c is not None]

                    if len(valid_closes) >= 2:
                        start_price = valid_closes[0]
                        end_price = valid_closes[-1]
                        change_pct = ((end_price - start_price) / start_price) * 100
                        stock_score, stock_trend = api_client.calculate_stock_score(change_pct)

        # Analyze EUR/USD currency trend
        if eur_response.status_code == 200:
            eur_data = eur_response.json()
            if 'chart' in eur_data and eur_data['chart']['result']:
                result = eur_data['chart']['result'][0]
                if 'indicators' in result:
                    closes = result['indicators']['quote'][0]['close']
                    valid_closes = [c for c in closes if c is not None]

                    if len(valid_closes) >= 2:
                        start_rate = valid_closes[0]
                        end_rate = valid_closes[-1]
                        start_usd_eur = 1 / start_rate
                        end_usd_eur = 1 / end_rate
                        rate_change_pct = ((end_usd_eur - start_usd_eur) / start_usd_eur) * 100
                        currency_score, currency_trend = api_client.calculate_currency_score(rate_change_pct)

        # Calculate overall score (weighted: 70% stock, 30% currency)
        overall_score = int((stock_score * 0.7) + (currency_score * 0.3))

        # Generate recommendation text
        if overall_score >= 80:
            recommendation = "EXCELLENT"
            reasoning = "Outstanding conditions for selling - strong stock performance and favorable currency trends."
        elif overall_score >= 65:
            recommendation = "GOOD"
            reasoning = "Favorable conditions for selling - positive market indicators."
        elif overall_score >= 50:
            recommendation = "FAIR"
            reasoning = "Neutral conditions - consider your personal financial goals."
        elif overall_score >= 35:
            recommendation = "POOR"
            reasoning = "Unfavorable conditions - consider waiting for better market timing."
        else:
            recommendation = "VERY POOR"
            reasoning = "Poor conditions for selling - significant headwinds present."

        return jsonify({
            'recommendation': recommendation,
            'score': overall_score,
            'stockScore': stock_score,
            'currencyScore': currency_score,
            'stockTrend': stock_trend,
            'currencyTrend': currency_trend,
            'reasoning': reasoning
        })

    except Exception as e:
        return jsonify({
            'recommendation': 'UNKNOWN',
            'score': 0,
            'stockScore': 0,
            'currencyScore': 0,
            'stockTrend': 'Analysis failed',
            'currencyTrend': 'Analysis failed',
            'reasoning': f'Error: {str(e)}'
        }), 500


@dashboard_bp.route('/api/recommendation-history')
@cache.cached(timeout=CACHE_TIMEOUT_RECOMMENDATION)
def get_recommendation_history() -> Response | tuple[Response, int]:
    """Get historical recommendation scores over 12 months"""
    try:
        headers = {'User-Agent': USER_AGENT}

        # Get 12 months of AMZN data (weekly intervals)
        amzn_url = f'{YAHOO_FINANCE_URL}/AMZN?range=1y&interval=1wk'
        amzn_response = requests.get(amzn_url, headers=headers, timeout=10)

        # Get 12 months of EUR/USD data (weekly intervals)
        eur_url = f'{YAHOO_FINANCE_URL}/EURUSD=X?range=1y&interval=1wk'
        eur_response = requests.get(eur_url, headers=headers, timeout=10)

        dates: list[str] = []
        scores: list[int] = []

        if amzn_response.status_code == 200 and eur_response.status_code == 200:
            amzn_data = amzn_response.json()
            eur_data = eur_response.json()

            if ('chart' in amzn_data and amzn_data['chart']['result'] and
                    'chart' in eur_data and eur_data['chart']['result']):

                amzn_result = amzn_data['chart']['result'][0]
                eur_result = eur_data['chart']['result'][0]

                if ('timestamp' in amzn_result and 'indicators' in amzn_result and
                        'timestamp' in eur_result and 'indicators' in eur_result):

                    amzn_timestamps = amzn_result['timestamp']
                    amzn_closes = amzn_result['indicators']['quote'][0]['close']
                    eur_closes = eur_result['indicators']['quote'][0]['close']

                    for i in range(len(amzn_timestamps)):
                        if (i < len(amzn_closes) and i < len(eur_closes) and
                                amzn_closes[i] is not None and eur_closes[i] is not None):

                            # Calculate stock performance from start to current point
                            if i > 0:
                                start_price = next(
                                    (p for p in amzn_closes[:i+1] if p is not None),
                                    amzn_closes[i]
                                )
                                stock_change = ((amzn_closes[i] - start_price) / start_price) * 100
                            else:
                                stock_change = 0

                            stock_score, _ = api_client.calculate_stock_score(stock_change)

                            # Calculate currency change
                            if i > 0:
                                start_rate = next(
                                    (r for r in eur_closes[:i+1] if r is not None),
                                    eur_closes[i]
                                )
                                start_usd_eur = 1 / start_rate
                                current_usd_eur = 1 / eur_closes[i]
                                currency_change = ((current_usd_eur - start_usd_eur) / start_usd_eur) * 100
                            else:
                                currency_change = 0

                            currency_score, _ = api_client.calculate_currency_score(currency_change)

                            # Calculate overall score (70% stock, 30% currency)
                            overall_score = int((stock_score * 0.7) + (currency_score * 0.3))

                            date_obj = datetime.fromtimestamp(amzn_timestamps[i])
                            dates.append(date_obj.strftime('%b %d'))
                            scores.append(overall_score)

        if dates and scores:
            return jsonify({
                'dates': dates,
                'scores': scores
            })
        else:
            return jsonify({'error': 'Historical data unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500
