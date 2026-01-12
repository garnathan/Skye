"""
Weather API blueprint
Handles weather forecast from Met Éireann
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
import requests

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/api/weather', methods=['GET'])
def get_weather():
    """Get weather forecast from Met Éireann API"""
    try:
        lat = request.args.get('lat', '53.2631')  # Default to Killiney
        long = request.args.get('long', '-6.1083')
        current_app.logger.info(f"Weather data requested for coordinates: lat={lat}, long={long}")

        # Fetch from Met Éireann API
        url = f'http://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat={lat};long={long}'
        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            current_app.logger.error(f"Met Éireann API returned status {response.status_code}")
            return jsonify({'error': 'Failed to fetch weather data'}), 500

        current_app.logger.info("Successfully fetched weather data from Met Éireann")

        # Parse XML response
        root = ET.fromstring(response.content)

        # Extract current weather (first time point)
        current_time = None
        current_weather = {}
        hourly_forecast = []

        # Find all time elements (no namespace)
        for time_elem in root.findall('.//time'):
            from_time = time_elem.get('from')
            to_time = time_elem.get('to')

            # Skip if no 'from' time or from != to (we want point forecasts)
            if not from_time or from_time != to_time:
                continue

            time_dt = datetime.fromisoformat(from_time.replace('Z', '+00:00'))

            # Get location data
            location = time_elem.find('.//location')
            if location is None:
                continue

            # Extract weather parameters
            temp_elem = location.find('.//temperature')
            wind_speed_elem = location.find('.//windSpeed')
            wind_dir_elem = location.find('.//windDirection')
            humidity_elem = location.find('.//humidity')
            pressure_elem = location.find('.//pressure')
            cloud_elem = location.find('.//cloudiness')

            # For symbol and precipitation, check the interval forecast
            symbol_elem = None
            precip_value = 0
            for interval_time in root.findall('.//time'):
                interval_from = interval_time.get('from')
                interval_to = interval_time.get('to')
                if interval_from and interval_to and interval_from != interval_to:
                    # This is an interval forecast
                    if interval_from == from_time or (interval_from < from_time < interval_to):
                        interval_loc = interval_time.find('.//location')
                        if interval_loc is not None:
                            if symbol_elem is None:
                                symbol_elem = interval_loc.find('.//symbol')
                            precip_elem = interval_loc.find('.//precipitation')
                            if precip_elem is not None:
                                precip_value = float(precip_elem.get('value', 0))

            weather_data = {
                'time': from_time,
                'temperature': float(temp_elem.get('value')) if temp_elem is not None else 0,
                'windSpeed': float(wind_speed_elem.get('mps', 0)) * 3.6 if wind_speed_elem is not None else 0,  # Convert m/s to km/h
                'windDirection': float(wind_dir_elem.get('deg', 0)) if wind_dir_elem is not None else 0,
                'humidity': float(humidity_elem.get('value', 0)) if humidity_elem is not None else 0,
                'pressure': float(pressure_elem.get('value', 0)) if pressure_elem is not None else 0,
                'cloudCover': float(cloud_elem.get('percent', 0)) if cloud_elem is not None else 0,
                'precipitation': precip_value,
                'symbol': symbol_elem.get('id', 'Cloud') if symbol_elem is not None else 'Cloud',
                'visibility': 10000  # Default visibility
            }

            # Set current weather (first valid entry)
            if current_time is None:
                current_time = time_dt
                current_weather = weather_data.copy()
                current_weather['description'] = symbol_elem.get('id', 'Cloud').replace('_', ' ') if symbol_elem is not None else 'Cloudy'

            # Collect hourly forecast for today (next 24 hours)
            if len(hourly_forecast) < 24:
                hourly_forecast.append(weather_data)

        return jsonify({
            'current': current_weather,
            'hourly': hourly_forecast
        })

    except Exception as e:
        current_app.logger.error(f"Weather API error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@weather_bp.route('/api/sun-times', methods=['GET'])
def get_sun_times():
    """Get sunrise and sunset times from sunrise-sunset.org API"""
    try:
        lat = request.args.get('lat', '53.2631')  # Default to Killiney
        lng = request.args.get('lng', '-6.1083')
        current_app.logger.info(
            f"Sun times requested for coordinates: lat={lat}, lng={lng}"
        )

        # Fetch from sunrise-sunset.org API (free, no API key required)
        url = f'https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&formatted=0'
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            current_app.logger.error(
                f"Sunrise-sunset API returned status {response.status_code}"
            )
            return jsonify({'error': 'Failed to fetch sun times'}), 500

        data = response.json()

        if data.get('status') != 'OK':
            current_app.logger.error(
                f"Sunrise-sunset API error: {data.get('status')}"
            )
            return jsonify({'error': 'Invalid response from sun times API'}), 500

        results = data.get('results', {})

        # Parse ISO timestamps and convert to local time
        sunrise_utc = datetime.fromisoformat(
            results['sunrise'].replace('Z', '+00:00')
        )
        sunset_utc = datetime.fromisoformat(
            results['sunset'].replace('Z', '+00:00')
        )
        civil_twilight_end_utc = datetime.fromisoformat(
            results['civil_twilight_end'].replace('Z', '+00:00')
        )

        # Convert to local timezone (Ireland is UTC+0 in winter, UTC+1 in summer)
        # For simplicity, we'll return both UTC and formatted local times
        sunrise_local = sunrise_utc.strftime('%H:%M')
        sunset_local = sunset_utc.strftime('%H:%M')
        civil_twilight_end_local = civil_twilight_end_utc.strftime('%H:%M')

        current_app.logger.info(
            f"Sun times retrieved: sunrise={sunrise_local}, "
            f"sunset={sunset_local}, "
            f"civil_twilight_end={civil_twilight_end_local}"
        )

        return jsonify({
            'sunrise': sunrise_local,
            'sunset': sunset_local,
            'civil_twilight_end': civil_twilight_end_local,
            'sunrise_iso': results['sunrise'],
            'sunset_iso': results['sunset'],
            'civil_twilight_end_iso': results['civil_twilight_end'],
            'day_length': results.get('day_length', 0)
        })

    except Exception as e:
        current_app.logger.error(f"Sun times API error: {str(e)}")
        return jsonify({'error': str(e)}), 500
