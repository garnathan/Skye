#!/usr/bin/env python3
# Standard library imports
import os
import sys
import json
import logging
import subprocess
import threading
import importlib.util
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from collections import deque
from urllib.parse import urlparse, parse_qs

# Third-party imports
import requests
import google.generativeai as genai

# Flask imports
from flask import Flask, render_template, jsonify, request, Response, session

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

app = Flask(__name__)

# ============================================================================
# LOG MANAGEMENT SYSTEM - Must be set up immediately after app creation
# ============================================================================

# Import logging system
from logging_setup import setup_logging, log_storage, log_storage_lock
setup_logging(app)

# Import utilities
from utils import load_config, get_config_value, handle_api_errors, require_config_key

# ============================================================================
# BLUEPRINTS
# ============================================================================

# Import and register blueprints
from blueprints.weather import weather_bp
from blueprints.logs import logs_bp
from blueprints.tools import tools_bp
from blueprints.pages import pages_bp
from blueprints.music_next import music_next_bp

app.register_blueprint(weather_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(tools_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(music_next_bp)

def discover_pages():
    """Automatically discover pages from the pages directory"""
    pages = []
    pages_dir = os.path.join(os.path.dirname(__file__), 'pages')
    
    if os.path.exists(pages_dir):
        for item in os.listdir(pages_dir):
            page_path = os.path.join(pages_dir, item)
            if os.path.isdir(page_path) and not item.startswith('_'):
                # Check if page has a config.py file
                config_file = os.path.join(page_path, 'config.py')
                if os.path.exists(config_file):
                    try:
                        spec = importlib.util.spec_from_file_location(f"{item}_config", config_file)
                        config = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(config)
                        
                        # Skip hidden pages
                        if getattr(config, 'HIDDEN', False):
                            continue
                        
                        pages.append({
                            'id': item,
                            'name': getattr(config, 'NAME', getattr(config, 'PAGE_NAME', item.title())),
                            'description': getattr(config, 'PAGE_DESCRIPTION', ''),
                            'icon': getattr(config, 'ICON', getattr(config, 'PAGE_ICON', 'fas fa-file'))
                        })
                    except Exception as e:
                        print(f"Error loading config for {item}: {e}")
                        pages.append({
                            'id': item,
                            'name': item.title(),
                            'description': '',
                            'icon': 'fas fa-file'
                        })
    
    # Sort pages with home first, then by ORDER if specified, then alphabetically
    def sort_key(page):
        if page['id'] == 'home':
            return '0'  # Home comes first
        # Check if page has ORDER attribute from config
        page_path = os.path.join(pages_dir, page['id'])
        config_file = os.path.join(page_path, 'config.py')
        if os.path.exists(config_file):
            try:
                spec = importlib.util.spec_from_file_location(f"{page['id']}_config", config_file)
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)
                order = getattr(config, 'ORDER', 999)
                return f"{order:03d}_{page['name']}"
            except:
                pass
        return f"999_{page['name']}"
    
    return sorted(pages, key=sort_key)

@app.route('/')
def index():
    app.logger.info(f"Home page accessed from {request.remote_addr}")
    pages = discover_pages()
    return render_template('index.html', pages=pages)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.svg')

# Pages routes moved to blueprints/pages.py

@app.route('/api/gemini/models', methods=['GET'])
def list_gemini_models():
    """List available Gemini models"""
    try:
        
        # Get API key from config file or environment
        config = load_config()
        api_key = config.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            return jsonify({'error': 'Gemini API key not configured'}), 500
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List models
        models = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                models.append({
                    'name': model.name,
                    'display_name': model.display_name or model.name
                })
        
        return jsonify({'models': models})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gemini/chat', methods=['POST'])
@require_config_key('gemini_api_key', 'Gemini API key not configured. Please set your API key in config.json')
@handle_api_errors
def gemini_chat():
    """Handle Gemini chat requests"""

    data = request.get_json()
    message = data.get('message', '').strip()
    model_name = data.get('model', 'models/gemini-pro')

    app.logger.info(f"Gemini chat request with model: {model_name}, message length: {len(message)}")

    if not message:
        app.logger.warning("Gemini chat request failed: No message provided")
        return jsonify({'error': 'No message provided'}), 400

    api_key = get_config_value('gemini_api_key') or os.environ.get('GEMINI_API_KEY')
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(message)

    if response.text:
        app.logger.info(f"Gemini chat response generated, length: {len(response.text)}")
        return jsonify({'response': response.text})

    app.logger.error("Gemini chat failed: No response generated")
    return jsonify({'error': 'No response generated'}), 500

@app.route('/api/pipeline-stats', methods=['GET'])
def run_pipeline_stats():
    """Run the critical pipeline stats script with streaming output"""
    import subprocess
    
    def generate():
        script_path = os.path.join(os.path.dirname(__file__), '../PipelineStats/critical_pipeline_stats.py')
        
        if not os.path.exists(script_path):
            yield f"data: {{\"output\": \"Script not found at: {script_path}\", \"status\": \"error\"}}\\n\\n"
            return
        
        try:
            yield f"data: {{\"output\": \"Starting pipeline analysis...\\n\", \"status\": \"running\"}}\\n\\n"
            
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=os.path.dirname(script_path)
            )
            
            # Read output line by line
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Escape quotes and newlines for JSON
                    escaped_line = output.strip().replace('\\', '\\\\').replace('"', '\\"')
                    yield f"data: {{\"output\": \"{escaped_line}\\n\", \"status\": \"running\"}}\\n\\n"
            
            # Check for any remaining output
            remaining_output = process.stdout.read()
            if remaining_output:
                escaped_output = remaining_output.strip().replace('\\', '\\\\').replace('"', '\\"')
                yield f"data: {{\"output\": \"{escaped_output}\\n\", \"status\": \"running\"}}\\n\\n"
            
            # Check for errors
            stderr_output = process.stderr.read()
            if stderr_output:
                escaped_error = stderr_output.strip().replace('\\', '\\\\').replace('"', '\\"')
                yield f"data: {{\"output\": \"Error: {escaped_error}\\n\", \"status\": \"error\"}}\\n\\n"
            
            return_code = process.poll()
            if return_code == 0:
                yield f"data: {{\"output\": \"\\nScript completed successfully.\", \"status\": \"success\"}}\\n\\n"
            else:
                yield f"data: {{\"output\": \"\\nScript failed with return code: {return_code}\", \"status\": \"error\"}}\\n\\n"
                
        except Exception as e:
            yield f"data: {{\"output\": \"Error: {str(e)}\", \"status\": \"error\"}}\\n\\n"
    
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control'
    })

@app.route('/api/youtube/playlists', methods=['GET'])
def get_youtube_playlists():
    """Get playlists for a YouTube channel"""
    try:
        
        channel_input = request.args.get('channel', '').strip()
        if not channel_input:
            return jsonify({'error': 'Channel handle required'}), 400
        
        # YouTube Data API v3 endpoint
        config = load_config()
        api_key = config.get('youtube_api_key') or os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            return jsonify({'error': 'YouTube API key not found in config.json or YOUTUBE_API_KEY environment variable'}), 500
        
        channel_id = None
        channel_name = None
        
        # Try different methods to get channel ID
        # Method 1: If it looks like a channel ID (starts with UC)
        if channel_input.startswith('UC') and len(channel_input) == 24:
            channel_id = channel_input
        else:
            # Method 2: Try channels endpoint with forHandle (for @handles)
            if channel_input.startswith('@'):
                handle = channel_input[1:]
                channels_url = 'https://www.googleapis.com/youtube/v3/channels'
                channels_params = {
                    'part': 'snippet',
                    'forHandle': handle,
                    'key': api_key
                }
                
                channels_response = requests.get(channels_url, params=channels_params, timeout=10)
                if channels_response.status_code == 200:
                    channels_data = channels_response.json()
                    if channels_data.get('items'):
                        channel_id = channels_data['items'][0]['id']
                        channel_name = channels_data['items'][0]['snippet']['title']
                elif channels_response.status_code == 403:
                    return jsonify({'error': f'YouTube API access denied. The API key may not have YouTube Data API v3 enabled. Please enable it in Google Cloud Console. Response: {channels_response.text}'}), 403
                elif channels_response.status_code == 400:
                    return jsonify({'error': f'YouTube API bad request. Response: {channels_response.text}'}), 400
            
            # Method 3: Search for channel by name
            if not channel_id:
                search_query = channel_input.replace('@', '')
                search_url = 'https://www.googleapis.com/youtube/v3/search'
                search_params = {
                    'part': 'snippet',
                    'q': search_query,
                    'type': 'channel',
                    'key': api_key,
                    'maxResults': 5
                }
                
                search_response = requests.get(search_url, params=search_params, timeout=10)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    if search_data.get('items'):
                        # Find exact match or closest match
                        for item in search_data['items']:
                            title = item['snippet']['title'].lower()
                            if search_query.lower() in title or title in search_query.lower():
                                channel_id = item['snippet']['channelId']
                                channel_name = item['snippet']['title']
                                break
                        
                        # If no exact match, use first result
                        if not channel_id:
                            channel_id = search_data['items'][0]['snippet']['channelId']
                            channel_name = search_data['items'][0]['snippet']['title']
                elif search_response.status_code == 403:
                    return jsonify({'error': f'YouTube API access denied. The API key may not have YouTube Data API v3 enabled. Please enable it in Google Cloud Console. Response: {search_response.text}'}), 403
                elif search_response.status_code == 400:
                    return jsonify({'error': f'YouTube API bad request. Response: {search_response.text}'}), 400
        
        if not channel_id:
            return jsonify({'error': f'Channel "{channel_input}" not found. Try using the exact channel handle (e.g., @username) or channel name.'}), 404
        
        # Get channel name if we don't have it
        if not channel_name:
            channels_url = 'https://www.googleapis.com/youtube/v3/channels'
            channels_params = {
                'part': 'snippet',
                'id': channel_id,
                'key': api_key
            }
            
            channels_response = requests.get(channels_url, params=channels_params, timeout=10)
            if channels_response.status_code == 200:
                channels_data = channels_response.json()
                if channels_data.get('items'):
                    channel_name = channels_data['items'][0]['snippet']['title']
        
        # Get playlists for the channel with pagination
        playlists = []
        next_page_token = None
        
        while True:
            playlists_url = 'https://www.googleapis.com/youtube/v3/playlists'
            playlists_params = {
                'part': 'snippet,contentDetails,status',
                'channelId': channel_id,
                'key': api_key,
                'maxResults': 50
            }
            
            if next_page_token:
                playlists_params['pageToken'] = next_page_token
            
            playlists_response = requests.get(playlists_url, params=playlists_params, timeout=10)
            if playlists_response.status_code != 200:
                return jsonify({'error': f'Failed to fetch playlists: {playlists_response.text}'}), 500
            
            playlists_data = playlists_response.json()
            
            for item in playlists_data.get('items', []):
                playlist = {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet'].get('description', ''),
                    'videoCount': item['contentDetails']['itemCount'],
                    'privacy': item['status']['privacyStatus'],
                    'thumbnail': item['snippet']['thumbnails'].get('default', {}).get('url', '')
                }
                playlists.append(playlist)
            
            next_page_token = playlists_data.get('nextPageToken')
            if not next_page_token:
                break
        
        return jsonify({
            'playlists': playlists,
            'channelName': channel_name or 'Unknown Channel',
            'channelId': channel_id
        })
        
    except Exception as e:
        return jsonify({'error': f'API error: {str(e)}'}), 500

@app.route('/api/youtube/playlist-videos', methods=['GET'])
def get_playlist_videos():
    """Get videos from a playlist"""
    try:
        
        playlist_id = request.args.get('playlistId', '').strip()
        if not playlist_id:
            return jsonify({'error': 'Playlist ID required'}), 400
        
        config = load_config()
        api_key = config.get('youtube_api_key') or os.environ.get('YOUTUBE_API_KEY')
        if not api_key or api_key in ['your_youtube_api_key_here', 'your_gemini_api_key_here']:
            return jsonify({'error': 'YouTube API key not configured'}), 500
        
        videos = []
        next_page_token = None
        
        while True:
            params = {
                'part': 'snippet',
                'playlistId': playlist_id,
                'key': api_key,
                'maxResults': 50
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            response = requests.get('https://www.googleapis.com/youtube/v3/playlistItems', params=params, timeout=10)
            if response.status_code != 200:
                return jsonify({'error': f'Failed to fetch playlist videos: {response.text}'}), 500
            
            data = response.json()
            
            for item in data.get('items', []):
                if item['snippet']['resourceId']['kind'] == 'youtube#video':
                    videos.append({
                        'videoId': item['snippet']['resourceId']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet'].get('description', ''),
                        'position': item['snippet']['position']
                    })
            
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
        
        return jsonify({'videos': videos})
        
    except Exception as e:
        return jsonify({'error': f'API error: {str(e)}'}), 500

@app.route('/oauth/youtube/authorize/<account_type>')
def youtube_oauth_authorize(account_type):
    """Start YouTube OAuth flow for source or destination account"""
    try:
        if account_type not in ['source', 'destination']:
            return jsonify({'error': 'Invalid account type'}), 400
            
        config = load_config()
        oauth_config = config.get('youtube_oauth', {})
        client_id = oauth_config.get('client_id')
        redirect_uri = oauth_config.get('redirect_uri')
        
        if not client_id or client_id == 'your_client_id.apps.googleusercontent.com':
            return jsonify({'error': 'YouTube OAuth not configured. Please set client_id in config.json'}), 500
        
        # YouTube OAuth scopes for playlist management
        scopes = 'https://www.googleapis.com/auth/youtube'
        
        auth_url = (
            f'https://accounts.google.com/o/oauth2/auth?'
            f'client_id={client_id}&'
            f'redirect_uri={redirect_uri}&'
            f'scope={scopes}&'
            f'response_type=code&'
            f'access_type=offline&'
            f'state={account_type}'
        )
        
        return jsonify({'auth_url': auth_url})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/oauth/youtube/callback')
def youtube_oauth_callback():
    """Handle YouTube OAuth callback"""
    try:
        
        code = request.args.get('code')
        state = request.args.get('state')  # source or destination
        
        if not code:
            return 'OAuth authorization failed', 400
            
        if state not in ['source', 'destination']:
            return 'Invalid state parameter', 400
        
        config = load_config()
        oauth_config = config.get('youtube_oauth', {})
        client_id = oauth_config.get('client_id')
        client_secret = oauth_config.get('client_secret')
        redirect_uri = oauth_config.get('redirect_uri')
        
        # Exchange code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code == 200:
            token_info = token_response.json()
            # Store tokens separately for source and destination
            session[f'youtube_{state}_access_token'] = token_info.get('access_token')
            session[f'youtube_{state}_refresh_token'] = token_info.get('refresh_token')
            
            return f'''
            <html>
            <body>
                <h2>YouTube Authorization Successful!</h2>
                <p>{state.title()} account authorized. You can now close this window.</p>
                <script>
                    window.opener.postMessage('oauth_success_{state}', '*');
                    window.close();
                </script>
            </body>
            </html>
            '''
        else:
            return f'Token exchange failed: {token_response.text}', 400
            
    except Exception as e:
        return f'OAuth callback error: {str(e)}', 500

@app.route('/api/youtube/copy-playlists', methods=['POST'])
def copy_playlists():
    """Copy playlists using OAuth authentication"""
    try:

        # Check if both accounts are authenticated
        source_token = session.get('youtube_source_access_token')
        dest_token = session.get('youtube_destination_access_token')

        if not source_token:
            app.logger.warning("YouTube playlist copy failed: Source account not authenticated")
            return jsonify({'error': 'Source account not authenticated. Please authorize source account first.', 'auth_required': 'source'}), 401

        if not dest_token:
            app.logger.warning("YouTube playlist copy failed: Destination account not authenticated")
            return jsonify({'error': 'Destination account not authenticated. Please authorize destination account first.', 'auth_required': 'destination'}), 401

        data = request.get_json()
        playlist_ids = data.get('playlistIds', [])
        copy_private = data.get('copyPrivate', True)
        copy_descriptions = data.get('copyDescriptions', True)

        app.logger.info(f"YouTube playlist copy requested: {len(playlist_ids)} playlists, private={copy_private}, descriptions={copy_descriptions}")

        if not playlist_ids:
            app.logger.warning("YouTube playlist copy failed: No playlists selected")
            return jsonify({'error': 'No playlists selected'}), 400
        
        config = load_config()
        api_key = config.get('youtube_api_key')
        
        copied_playlists = []
        
        for playlist_id in playlist_ids:
            try:
                # Get original playlist details
                playlist_url = f'https://www.googleapis.com/youtube/v3/playlists?part=snippet,status&id={playlist_id}&key={api_key}'
                playlist_response = requests.get(playlist_url, timeout=10)
                
                if playlist_response.status_code != 200:
                    continue
                
                playlist_data = playlist_response.json()
                if not playlist_data.get('items'):
                    continue
                
                original_playlist = playlist_data['items'][0]
                
                # Skip private playlists if not copying private
                if not copy_private and original_playlist['status']['privacyStatus'] == 'private':
                    continue
                
                # Create new playlist
                create_data = {
                    'snippet': {
                        'title': f"Copy of {original_playlist['snippet']['title']}",
                        'description': original_playlist['snippet']['description'] if copy_descriptions else ''
                    },
                    'status': {
                        'privacyStatus': 'private'  # Always create as private initially
                    }
                }
                
                create_headers = {
                    'Authorization': f'Bearer {dest_token}',
                    'Content-Type': 'application/json'
                }
                
                create_response = requests.post(
                    'https://www.googleapis.com/youtube/v3/playlists?part=snippet,status',
                    json=create_data,
                    headers=create_headers,
                    timeout=10
                )
                
                if create_response.status_code == 200:
                    new_playlist = create_response.json()
                    new_playlist_id = new_playlist['id']
                    
                    # Get videos from original playlist
                    videos_url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={api_key}'
                    videos_response = requests.get(videos_url, timeout=10)
                    
                    if videos_response.status_code == 200:
                        videos_data = videos_response.json()
                        
                        # Add videos to new playlist
                        for video in videos_data.get('items', []):
                            if video['snippet']['resourceId']['kind'] == 'youtube#video':
                                video_id = video['snippet']['resourceId']['videoId']
                                
                                add_video_data = {
                                    'snippet': {
                                        'playlistId': new_playlist_id,
                                        'resourceId': {
                                            'kind': 'youtube#video',
                                            'videoId': video_id
                                        }
                                    }
                                }
                                
                                requests.post(
                                    'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet',
                                    json=add_video_data,
                                    headers=create_headers,
                                    timeout=10
                                )
                    
                    copied_playlists.append({
                        'original_id': playlist_id,
                        'new_id': new_playlist_id,
                        'title': new_playlist['snippet']['title']
                    })
                    
            except Exception as e:
                print(f'Error copying playlist {playlist_id}: {e}')
                continue
        
        return jsonify({
            'success': True,
            'copied_playlists': copied_playlists,
            'message': f'Successfully copied {len(copied_playlists)} playlists'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/api/stock-data')
@handle_api_errors
def get_stock_data():
    """Get stock data using the same API as current price"""
    from utils import api_client

    symbol = request.args.get('symbol', 'AMZN')
    period = request.args.get('period', '1y')
    app.logger.info(f"Stock data requested for {symbol}, period: {period}")

    # Map period to Yahoo Finance parameters
    period_map = {
        '1d': ('1d', '5m'),
        '1wk': ('5d', '1h'),
        '1mo': ('1mo', '1d'),
        '1y': ('1y', '1wk')
    }

    range_param, interval_param = period_map.get(period, ('1y', '1wk'))

    data = api_client.get_yahoo_chart_data(symbol, range_param, interval_param)
    dates, prices = api_client.parse_yahoo_chart(data, period)

    if dates and prices:
        prices = [round(p, 2) for p in prices]
        app.logger.info(f"Stock data retrieved for {symbol}: {len(dates)} data points")
        return jsonify({'dates': dates, 'prices': prices, 'symbol': symbol})

    app.logger.error(f"Stock data unavailable for {symbol}")
    return jsonify({'error': 'Chart data unavailable'}), 503

@app.route('/api/currency-data')
def get_currency_data():
    """Get currency data using Yahoo Finance"""
    try:
        from datetime import datetime

        period = request.args.get('period', '1y')
        app.logger.info(f"Currency data (USD/EUR) requested, period: {period}")
        
        period = request.args.get('period', '1y')
        
        # Map period to Yahoo Finance parameters
        period_map = {
            '1d': ('1d', '5m'),
            '1wk': ('5d', '1h'), 
            '1mo': ('1mo', '1d'),
            '1y': ('1y', '1wk')
        }
        
        range_param, interval_param = period_map.get(period, ('1y', '1wk'))
        
        # Use Yahoo Finance v8 API for EUR/USD data
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?range={range_param}&interval={interval_param}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'timestamp' in result and 'indicators' in result:
                    timestamps = result['timestamp']
                    closes = result['indicators']['quote'][0]['close']
                    
                    dates = []
                    rates = []
                    
                    for ts, close in zip(timestamps, closes):
                        if close is not None:
                            date_obj = datetime.fromtimestamp(ts)
                            if period == '1d':
                                dates.append(date_obj.strftime('%H:%M'))
                            elif period == '1wk':
                                dates.append(date_obj.strftime('%a %H:%M'))
                            elif period == '1mo':
                                dates.append(date_obj.strftime('%b %d'))
                            else:
                                dates.append(date_obj.strftime('%b'))
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

@app.route('/api/current-price')
def get_current_price():
    """Get current price using the same API as chart data"""
    try:
        
        symbol = request.args.get('symbol', 'AMZN')
        
        # Use the same Yahoo Finance API that works for chart data
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    price = result['meta']['regularMarketPrice']
                    return jsonify({'price': round(price, 2), 'symbol': symbol})
        
        return jsonify({'error': 'Price unavailable'}), 503
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/currency-rate')
def get_currency_rate():
    """Get current USD to EUR rate using Yahoo Finance"""
    try:
        
        # Use Yahoo Finance v8 API like stock data
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
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

@app.route('/api/xrp-data')
def get_xrp_data():
    """Get XRP price data in EUR using Yahoo Finance"""
    try:
        from datetime import datetime
        
        period = request.args.get('period', '1y')
        
        # Map period to Yahoo Finance parameters
        period_map = {
            '1d': ('1d', '5m'),
            '1wk': ('5d', '1h'), 
            '1mo': ('1mo', '1d'),
            '1y': ('1y', '1wk')
        }
        
        range_param, interval_param = period_map.get(period, ('1y', '1wk'))
        
        # Use Yahoo Finance v8 API for XRP-EUR data
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/XRP-EUR?range={range_param}&interval={interval_param}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'timestamp' in result and 'indicators' in result:
                    timestamps = result['timestamp']
                    closes = result['indicators']['quote'][0]['close']
                    
                    dates = []
                    prices = []
                    
                    for i, (ts, close) in enumerate(zip(timestamps, closes)):
                        if close is not None:
                            date_obj = datetime.fromtimestamp(ts)
                            if period == '1d':
                                dates.append(date_obj.strftime('%H:%M'))
                            elif period == '1wk':
                                dates.append(date_obj.strftime('%a %H:%M'))
                            elif period == '1mo':
                                dates.append(date_obj.strftime('%b %d'))
                            else:
                                dates.append(date_obj.strftime('%b %d'))
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

@app.route('/api/xrp-price')
def get_xrp_price():
    """Get current XRP price in EUR using Yahoo Finance"""
    try:
        
        # Use Yahoo Finance API for XRP-EUR
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/XRP-EUR'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
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

@app.route('/api/gold-data')
def get_gold_data():
    """Get Gold price data in EUR using Yahoo Finance"""
    try:
        from datetime import datetime
        
        period = request.args.get('period', '1y')
        
        # Map period to Yahoo Finance parameters
        period_map = {
            '1d': ('1d', '5m'),
            '1wk': ('5d', '1h'), 
            '1mo': ('1mo', '1d'),
            '1y': ('1y', '1wk')
        }
        
        range_param, interval_param = period_map.get(period, ('1y', '1wk'))
        
        # Use Yahoo Finance v8 API for Gold data
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range={range_param}&interval={interval_param}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Get EUR/USD rate first with multiple fallbacks
        eur_usd_rate = 1.1  # Default fallback
        try:
            eur_response = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X', headers=headers, timeout=5)
            if eur_response.status_code == 200:
                eur_data = eur_response.json()
                if 'chart' in eur_data and eur_data['chart']['result']:
                    eur_result = eur_data['chart']['result'][0]
                    if 'meta' in eur_result and 'regularMarketPrice' in eur_result['meta']:
                        eur_usd_rate = eur_result['meta']['regularMarketPrice']
        except:
            # If EUR/USD fails, try alternative API
            try:
                alt_response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR', timeout=3)
                if alt_response.status_code == 200:
                    alt_data = alt_response.json()
                    if 'rates' in alt_data and 'USD' in alt_data['rates']:
                        eur_usd_rate = alt_data['rates']['USD']
            except:
                pass  # Use default fallback
        
        # Try gold API with retry logic
        response = None
        for attempt in range(3):
            try:
                timeout = 5 + (attempt * 2)  # 5s, 7s, 9s
                response = requests.get(url, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    # Validate response structure immediately
                    if ('chart' in data and data['chart']['result'] and 
                        len(data['chart']['result']) > 0):
                        result = data['chart']['result'][0]
                        if ('timestamp' in result and 'indicators' in result and 
                            result['indicators']['quote'] and 
                            len(result['indicators']['quote']) > 0):
                            break
            except requests.exceptions.RequestException:
                if attempt == 2:  # Last attempt
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
                    
                    # Ensure we have valid data
                    if timestamps and closes and len(timestamps) > 0 and len(closes) > 0:
                        dates = []
                        prices = []
                        
                        for i, (ts, close) in enumerate(zip(timestamps, closes)):
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
                                    # Convert USD to EUR (Gold is priced in USD per troy ounce)
                                    price_eur = close / eur_usd_rate
                                    prices.append(round(price_eur, 2))
                                except (ValueError, OSError):
                                    continue  # Skip invalid timestamps
                        
                        # Only return if we have meaningful data
                        if len(dates) >= 5 and len(prices) >= 5:  # At least 5 data points
                            return jsonify({
                                'dates': dates,
                                'prices': prices,
                                'symbol': 'Gold-EUR'
                            })
        
        return jsonify({'error': 'Gold chart data unavailable'}), 503
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gold-price')
def get_gold_price():
    """Get current Gold price in EUR using Yahoo Finance"""
    try:
        
        # Get EUR/USD rate first with multiple fallbacks
        eur_usd_rate = 1.1  # Default fallback
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            eur_response = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X', headers=headers, timeout=5)
            if eur_response.status_code == 200:
                eur_data = eur_response.json()
                if 'chart' in eur_data and eur_data['chart']['result']:
                    eur_result = eur_data['chart']['result'][0]
                    if 'meta' in eur_result and 'regularMarketPrice' in eur_result['meta']:
                        eur_usd_rate = eur_result['meta']['regularMarketPrice']
        except:
            # If EUR/USD fails, try alternative API
            try:
                alt_response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR', timeout=3)
                if alt_response.status_code == 200:
                    alt_data = alt_response.json()
                    if 'rates' in alt_data and 'USD' in alt_data['rates']:
                        eur_usd_rate = alt_data['rates']['USD']
            except:
                pass  # Use default fallback
        
        # Use Yahoo Finance API for Gold futures (GC=F) with retry logic
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GC=F'
        
        response = None
        for attempt in range(3):
            try:
                timeout = 5 + (attempt * 2)  # 5s, 7s, 9s
                response = requests.get(url, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                if attempt == 2:  # Last attempt
                    raise
                continue
        
        if response and response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']['result'] and len(data['chart']['result']) > 0:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    gold_usd = result['meta']['regularMarketPrice']
                    
                    # Convert USD to EUR
                    gold_eur = gold_usd / eur_usd_rate
                    return jsonify({'price': round(gold_eur, 2), 'symbol': 'Gold-EUR'})
        
        return jsonify({'error': 'Gold price unavailable'}), 503
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sell-recommendation')
def get_sell_recommendation():
    """Analyze AMZN stock and USD/EUR trends to recommend selling with percentage score"""
    try:
        from datetime import datetime, timedelta
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Get 12 months of AMZN data
        amzn_url = 'https://query1.finance.yahoo.com/v8/finance/chart/AMZN?range=1y&interval=1wk'
        amzn_response = requests.get(amzn_url, headers=headers, timeout=10)
        
        # Get 12 months of EUR/USD data
        eur_url = 'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?range=1y&interval=1wk'
        eur_response = requests.get(eur_url, headers=headers, timeout=10)
        
        stock_score = 50  # Base score
        currency_score = 50  # Base score
        stock_trend = "Unknown"
        currency_trend = "Unknown"
        
        # Analyze AMZN stock trend and calculate score
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
                        
                        # Calculate stock score (0-100)
                        if change_pct >= 30:
                            stock_score = 95
                            stock_trend = f"Exceptional growth (+{change_pct:.1f}%)"
                        elif change_pct >= 20:
                            stock_score = 85
                            stock_trend = f"Strong growth (+{change_pct:.1f}%)"
                        elif change_pct >= 10:
                            stock_score = 75
                            stock_trend = f"Good growth (+{change_pct:.1f}%)"
                        elif change_pct >= 5:
                            stock_score = 65
                            stock_trend = f"Moderate growth (+{change_pct:.1f}%)"
                        elif change_pct >= 0:
                            stock_score = 55
                            stock_trend = f"Slight growth (+{change_pct:.1f}%)"
                        elif change_pct >= -5:
                            stock_score = 45
                            stock_trend = f"Minor decline ({change_pct:.1f}%)"
                        elif change_pct >= -10:
                            stock_score = 35
                            stock_trend = f"Moderate decline ({change_pct:.1f}%)"
                        elif change_pct >= -20:
                            stock_score = 25
                            stock_trend = f"Significant decline ({change_pct:.1f}%)"
                        else:
                            stock_score = 10
                            stock_trend = f"Major decline ({change_pct:.1f}%)"
        
        # Analyze EUR/USD currency trend and calculate score
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
                        # Convert to USD/EUR for analysis
                        start_usd_eur = 1 / start_rate
                        end_usd_eur = 1 / end_rate
                        rate_change_pct = ((end_usd_eur - start_usd_eur) / start_usd_eur) * 100
                        
                        # Calculate currency score (0-100)
                        if rate_change_pct >= 5:
                            currency_score = 80
                            currency_trend = f"USD very strong (+{rate_change_pct:.1f}%)"
                        elif rate_change_pct >= 2:
                            currency_score = 70
                            currency_trend = f"USD strengthening (+{rate_change_pct:.1f}%)"
                        elif rate_change_pct >= -1:
                            currency_score = 60
                            currency_trend = f"USD stable ({rate_change_pct:.1f}%)"
                        elif rate_change_pct >= -3:
                            currency_score = 40
                            currency_trend = f"USD weakening ({rate_change_pct:.1f}%)"
                        else:
                            currency_score = 20
                            currency_trend = f"USD very weak ({rate_change_pct:.1f}%)"
        
        # Calculate overall recommendation score (weighted: 70% stock, 30% currency)
        overall_score = int((stock_score * 0.7) + (currency_score * 0.3))
        
        # Generate recommendation text based on score
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

@app.route('/api/portfolio-value')
def get_portfolio_value():
    """Get portfolio value of 287 AMZN shares in EUR over time"""
    try:
        from datetime import datetime

        period = request.args.get('period', '1y')

        # Map period to Yahoo Finance parameters
        period_map = {
            '1d': ('1d', '5m'),
            '1wk': ('5d', '1h'),
            '1mo': ('1mo', '1d'),
            '1y': ('1y', '1wk')
        }

        range_param, interval_param = period_map.get(period, ('1y', '1wk'))

        headers = {'User-Agent': 'Mozilla/5.0'}

        # Get AMZN data with selected period
        amzn_url = f'https://query1.finance.yahoo.com/v8/finance/chart/AMZN?range={range_param}&interval={interval_param}'
        amzn_response = requests.get(amzn_url, headers=headers, timeout=10)

        # Get current EUR/USD rate
        eur_url = 'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X'
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

                dates = []
                values = []

                for ts, close in zip(timestamps, closes):
                    if close is not None:
                        date_obj = datetime.fromtimestamp(ts)
                        if period == '1d':
                            dates.append(date_obj.strftime('%H:%M'))
                        elif period == '1wk':
                            dates.append(date_obj.strftime('%a %H:%M'))
                        elif period == '1mo':
                            dates.append(date_obj.strftime('%b %d'))
                        else:
                            dates.append(date_obj.strftime('%b %d'))
                        # Calculate portfolio value: 287 shares * price in USD * USD to EUR rate
                        portfolio_value_eur = 287 * close * usd_eur_rate
                        values.append(round(portfolio_value_eur, 2))

                if dates and values:
                    # Calculate current portfolio value and change
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
                        'shares': 287
                    })

        return jsonify({'error': 'Portfolio data unavailable'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cash-assets-value')
def get_cash_assets_value():
    """Get historical value of EUR cash assets (105,595.85 EUR today) converted to what they were worth over time"""
    try:
        from datetime import datetime

        period = request.args.get('period', '1y')

        # Map period to Yahoo Finance parameters
        period_map = {
            '1d': ('1d', '5m'),
            '1wk': ('5d', '1h'),
            '1mo': ('1mo', '1d'),
            '1y': ('1y', '1wk')
        }

        range_param, interval_param = period_map.get(period, ('1y', '1wk'))

        headers = {'User-Agent': 'Mozilla/5.0'}

        # Get EUR/USD data with selected period
        eur_url = f'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?range={range_param}&interval={interval_param}'
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
                eur_cash = 105595.85
                usd_cash = eur_cash * current_eur_usd_rate

                dates = []
                values = []

                for ts, eur_usd_rate in zip(timestamps, eur_usd_rates):
                    if eur_usd_rate is not None:
                        date_obj = datetime.fromtimestamp(ts)
                        if period == '1d':
                            dates.append(date_obj.strftime('%H:%M'))
                        elif period == '1wk':
                            dates.append(date_obj.strftime('%a %H:%M'))
                        elif period == '1mo':
                            dates.append(date_obj.strftime('%b %d'))
                        else:
                            dates.append(date_obj.strftime('%b %d'))
                        # Calculate USD amount, then convert back to EUR using historical rate
                        # This shows what the EUR value would have been at each point in time
                        usd_eur_rate = 1 / eur_usd_rate
                        cash_value_eur = usd_cash * usd_eur_rate
                        values.append(round(cash_value_eur, 2))

                if dates and values:
                    # Calculate current value and change
                    current_value = values[-1]
                    start_value = values[0]
                    change_amount = current_value - start_value
                    change_percent = ((current_value - start_value) / start_value) * 100

                    # Get current rate
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

@app.route('/api/recommendation-history')
def get_recommendation_history():
    """Get historical recommendation scores over 6 months"""
    try:
        from datetime import datetime

        headers = {'User-Agent': 'Mozilla/5.0'}

        # Get 12 months of AMZN data (weekly intervals)
        amzn_url = 'https://query1.finance.yahoo.com/v8/finance/chart/AMZN?range=1y&interval=1wk'
        amzn_response = requests.get(amzn_url, headers=headers, timeout=10)
        
        # Get 12 months of EUR/USD data (weekly intervals)
        eur_url = 'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?range=1y&interval=1wk'
        eur_response = requests.get(eur_url, headers=headers, timeout=10)
        
        dates = []
        scores = []
        
        if (amzn_response.status_code == 200 and eur_response.status_code == 200):
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
                    
                    # Calculate scores for each week
                    for i in range(len(amzn_timestamps)):
                        if (i < len(amzn_closes) and i < len(eur_closes) and
                            amzn_closes[i] is not None and eur_closes[i] is not None):
                            
                            # Calculate stock performance from start to current point
                            if i > 0:
                                start_price = next((price for price in amzn_closes[:i+1] if price is not None), amzn_closes[i])
                                current_price = amzn_closes[i]
                                stock_change = ((current_price - start_price) / start_price) * 100
                            else:
                                stock_change = 0
                            
                            # Calculate stock score
                            if stock_change >= 30:
                                stock_score = 95
                            elif stock_change >= 20:
                                stock_score = 85
                            elif stock_change >= 10:
                                stock_score = 75
                            elif stock_change >= 5:
                                stock_score = 65
                            elif stock_change >= 0:
                                stock_score = 55
                            elif stock_change >= -5:
                                stock_score = 45
                            elif stock_change >= -10:
                                stock_score = 35
                            elif stock_change >= -20:
                                stock_score = 25
                            else:
                                stock_score = 10
                            
                            # Calculate currency score
                            if i > 0:
                                start_rate = next((rate for rate in eur_closes[:i+1] if rate is not None), eur_closes[i])
                                current_rate = eur_closes[i]
                                start_usd_eur = 1 / start_rate
                                current_usd_eur = 1 / current_rate
                                currency_change = ((current_usd_eur - start_usd_eur) / start_usd_eur) * 100
                            else:
                                currency_change = 0
                            
                            if currency_change >= 5:
                                currency_score = 80
                            elif currency_change >= 2:
                                currency_score = 70
                            elif currency_change >= -1:
                                currency_score = 60
                            elif currency_change >= -3:
                                currency_score = 40
                            else:
                                currency_score = 20
                            
                            # Calculate overall score (70% stock, 30% currency)
                            overall_score = int((stock_score * 0.7) + (currency_score * 0.3))
                            
                            # Format date
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

# VRT calculator route moved to blueprints/tools.py

@app.route('/api/youtube/download-audio', methods=['POST'])
def download_youtube_audio():
    """Download audio from YouTube video as MP3"""
    try:
        import subprocess
        import tempfile
        import base64
        
        data = request.get_json()
        url = data.get('url', '').strip()
        save_path = data.get('savePath', 'audio.mp3')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Validate YouTube URL
        parsed_url = urlparse(url)
        if not (parsed_url.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be'] or 'youtube.com' in parsed_url.netloc):
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Create a temporary directory for the download
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use the existing youtube_audio_downloader.py script
            script_path = os.path.join(os.path.dirname(__file__), 'youtube_audio_downloader.py')
            
            if not os.path.exists(script_path):
                return jsonify({'error': 'YouTube downloader script not found'}), 500
            
            # Run the download script in the temp directory
            try:
                result = subprocess.run(
                    ['python3', script_path, url],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    # Check if it's actually an error or just warnings
                    stderr_lower = result.stderr.lower() if result.stderr else ''
                    if 'error:' in stderr_lower and 'unable to download' in stderr_lower:
                        return jsonify({'error': f'Download failed: {result.stderr}'}), 500
                    # If returncode != 0 but no critical error, continue to check for MP3 file
                
                # Find the downloaded MP3 file
                mp3_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3')]
                if not mp3_files:
                    return jsonify({'error': 'No MP3 file was created'}), 500
                
                mp3_file = mp3_files[0]
                mp3_path = os.path.join(temp_dir, mp3_file)
                
                # Read the file and encode it as base64 for download
                with open(mp3_path, 'rb') as f:
                    file_data = base64.b64encode(f.read()).decode('utf-8')
                
                # Clean up the filename for the user
                clean_filename = save_path if save_path.endswith('.mp3') else f"{save_path}.mp3"
                
                return jsonify({
                    'success': True,
                    'filename': clean_filename,
                    'fileData': file_data,
                    'originalFilename': mp3_file
                })
                
            except subprocess.TimeoutExpired:
                return jsonify({'error': 'Download timeout - the video may be too long or unavailable'}), 408
            except Exception as e:
                return jsonify({'error': f'Download error: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Music Next routes moved to blueprints/music_next.py

@app.route('/api/restart', methods=['POST'])
def restart_server():
    """Restart the Skye server"""
    try:
        import os
        import signal

        app.logger.warning("Server restart requested by user")
        # Send restart signal to keep_alive.py
        os.system('touch /tmp/skye_restart')
        return jsonify({'status': 'restarting'})
    except Exception as e:
        app.logger.error(f"Server restart failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/vrt-calculator')
def vrt_calculator_standalone():
    """Standalone VRT Calculator page"""
    pages_dir = os.path.join(os.path.dirname(__file__), 'pages', '_vrt-calculator')
    page_file = os.path.join(pages_dir, 'page.py')
    
    if os.path.exists(page_file):
        try:
            spec = importlib.util.spec_from_file_location("vrt_page", page_file)
            page_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(page_module)
            
            if hasattr(page_module, 'get_content'):
                content = page_module.get_content()
                return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VRT Calculator - Skye</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
    </style>
</head>
<body>
    {content['html']}
</body>
</html>
                '''
        except Exception as e:
            return f'<h1>Error loading VRT Calculator: {str(e)}</h1>', 500
    
    return '<h1>VRT Calculator not found</h1>', 404

# Page content route moved to blueprints/pages.py

# Logs routes moved to blueprints/logs.py

# Log application startup
app.logger.info("Skye application started")

# Configure session for OAuth
app.secret_key = 'your-secret-key-change-this-in-production'

if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=True, reloader_type='stat')