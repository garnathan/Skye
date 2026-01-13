"""
YouTube API blueprint
Handles YouTube playlists, OAuth, and audio downloads
"""
import os
import tempfile
import base64
from urllib.parse import urlparse
from flask import Blueprint, jsonify, request, current_app, session
import requests
import yt_dlp
from utils import load_config

youtube_bp = Blueprint('youtube', __name__)


@youtube_bp.route('/api/youtube/playlists', methods=['GET'])
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
            return jsonify({
                'error': 'YouTube API key not found in config.json or '
                'YOUTUBE_API_KEY environment variable'
            }), 500

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

                channels_response = requests.get(
                    channels_url, params=channels_params, timeout=10
                )
                if channels_response.status_code == 200:
                    channels_data = channels_response.json()
                    if channels_data.get('items'):
                        channel_id = channels_data['items'][0]['id']
                        channel_name = channels_data['items'][0]['snippet']['title']
                elif channels_response.status_code == 403:
                    return jsonify({
                        'error': 'YouTube API access denied. The API key may not '
                        'have YouTube Data API v3 enabled. Please enable it in '
                        f'Google Cloud Console. Response: {channels_response.text}'
                    }), 403
                elif channels_response.status_code == 400:
                    return jsonify({
                        'error': f'YouTube API bad request. '
                        f'Response: {channels_response.text}'
                    }), 400

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

                search_response = requests.get(
                    search_url, params=search_params, timeout=10
                )
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    if search_data.get('items'):
                        # Find exact match or closest match
                        for item in search_data['items']:
                            title = item['snippet']['title'].lower()
                            if (search_query.lower() in title or
                                    title in search_query.lower()):
                                channel_id = item['snippet']['channelId']
                                channel_name = item['snippet']['title']
                                break

                        # If no exact match, use first result
                        if not channel_id:
                            channel_id = search_data['items'][0]['snippet']['channelId']
                            channel_name = search_data['items'][0]['snippet']['title']
                elif search_response.status_code == 403:
                    return jsonify({
                        'error': 'YouTube API access denied. The API key may not '
                        'have YouTube Data API v3 enabled. Please enable it in '
                        f'Google Cloud Console. Response: {search_response.text}'
                    }), 403
                elif search_response.status_code == 400:
                    return jsonify({
                        'error': f'YouTube API bad request. '
                        f'Response: {search_response.text}'
                    }), 400

        if not channel_id:
            return jsonify({
                'error': f'Channel "{channel_input}" not found. Try using the '
                'exact channel handle (e.g., @username) or channel name.'
            }), 404

        # Get channel name if we don't have it
        if not channel_name:
            channels_url = 'https://www.googleapis.com/youtube/v3/channels'
            channels_params = {
                'part': 'snippet',
                'id': channel_id,
                'key': api_key
            }

            channels_response = requests.get(
                channels_url, params=channels_params, timeout=10
            )
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

            playlists_response = requests.get(
                playlists_url, params=playlists_params, timeout=10
            )
            if playlists_response.status_code != 200:
                return jsonify({
                    'error': f'Failed to fetch playlists: {playlists_response.text}'
                }), 500

            playlists_data = playlists_response.json()

            for item in playlists_data.get('items', []):
                playlist = {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet'].get('description', ''),
                    'videoCount': item['contentDetails']['itemCount'],
                    'privacy': item['status']['privacyStatus'],
                    'thumbnail': item['snippet']['thumbnails'].get(
                        'default', {}
                    ).get('url', '')
                }
                playlists.append(playlist)

            next_page_token = playlists_data.get('nextPageToken')
            if not next_page_token:
                break

        current_app.logger.info(
            f"Retrieved {len(playlists)} playlists for channel: {channel_name}"
        )

        return jsonify({
            'playlists': playlists,
            'channelName': channel_name or 'Unknown Channel',
            'channelId': channel_id
        })

    except Exception as e:
        current_app.logger.error(f"YouTube playlists error: {str(e)}")
        return jsonify({'error': f'API error: {str(e)}'}), 500


@youtube_bp.route('/api/youtube/playlist-videos', methods=['GET'])
def get_playlist_videos():
    """Get videos from a playlist"""
    try:
        playlist_id = request.args.get('playlistId', '').strip()
        if not playlist_id:
            return jsonify({'error': 'Playlist ID required'}), 400

        config = load_config()
        api_key = config.get('youtube_api_key') or os.environ.get('YOUTUBE_API_KEY')
        if not api_key or api_key in [
            'your_youtube_api_key_here', 'your_gemini_api_key_here'
        ]:
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

            response = requests.get(
                'https://www.googleapis.com/youtube/v3/playlistItems',
                params=params,
                timeout=10
            )
            if response.status_code != 200:
                return jsonify({
                    'error': f'Failed to fetch playlist videos: {response.text}'
                }), 500

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

        current_app.logger.info(
            f"Retrieved {len(videos)} videos from playlist: {playlist_id}"
        )
        return jsonify({'videos': videos})

    except Exception as e:
        current_app.logger.error(f"YouTube playlist videos error: {str(e)}")
        return jsonify({'error': f'API error: {str(e)}'}), 500


@youtube_bp.route('/oauth/youtube/authorize/<account_type>')
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
            return jsonify({
                'error': 'YouTube OAuth not configured. Please set client_id '
                'in config.json'
            }), 500

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

        current_app.logger.info(f"YouTube OAuth initiated for {account_type} account")
        return jsonify({'auth_url': auth_url})

    except Exception as e:
        current_app.logger.error(f"YouTube OAuth authorize error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@youtube_bp.route('/oauth/youtube/callback')
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

            current_app.logger.info(
                f"YouTube OAuth successful for {state} account"
            )

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
            current_app.logger.error(
                f"YouTube OAuth token exchange failed: {token_response.text}"
            )
            return f'Token exchange failed: {token_response.text}', 400

    except Exception as e:
        current_app.logger.error(f"YouTube OAuth callback error: {str(e)}")
        return f'OAuth callback error: {str(e)}', 500


@youtube_bp.route('/api/youtube/copy-playlists', methods=['POST'])
def copy_playlists():
    """Copy playlists using OAuth authentication"""
    try:
        # Check if both accounts are authenticated
        source_token = session.get('youtube_source_access_token')
        dest_token = session.get('youtube_destination_access_token')

        if not source_token:
            current_app.logger.warning(
                "YouTube playlist copy failed: Source account not authenticated"
            )
            return jsonify({
                'error': 'Source account not authenticated. '
                'Please authorize source account first.',
                'auth_required': 'source'
            }), 401

        if not dest_token:
            current_app.logger.warning(
                "YouTube playlist copy failed: Destination account not authenticated"
            )
            return jsonify({
                'error': 'Destination account not authenticated. '
                'Please authorize destination account first.',
                'auth_required': 'destination'
            }), 401

        data = request.get_json()
        playlist_ids = data.get('playlistIds', [])
        copy_private = data.get('copyPrivate', True)
        copy_descriptions = data.get('copyDescriptions', True)

        current_app.logger.info(
            f"YouTube playlist copy requested: {len(playlist_ids)} playlists, "
            f"private={copy_private}, descriptions={copy_descriptions}"
        )

        if not playlist_ids:
            current_app.logger.warning(
                "YouTube playlist copy failed: No playlists selected"
            )
            return jsonify({'error': 'No playlists selected'}), 400

        config = load_config()
        api_key = config.get('youtube_api_key')

        copied_playlists = []

        for playlist_id in playlist_ids:
            try:
                # Get original playlist details
                playlist_url = (
                    f'https://www.googleapis.com/youtube/v3/playlists?'
                    f'part=snippet,status&id={playlist_id}&key={api_key}'
                )
                playlist_response = requests.get(playlist_url, timeout=10)

                if playlist_response.status_code != 200:
                    continue

                playlist_data = playlist_response.json()
                if not playlist_data.get('items'):
                    continue

                original_playlist = playlist_data['items'][0]

                # Skip private playlists if not copying private
                if (not copy_private and
                        original_playlist['status']['privacyStatus'] == 'private'):
                    continue

                # Create new playlist
                create_data = {
                    'snippet': {
                        'title': f"Copy of {original_playlist['snippet']['title']}",
                        'description': (
                            original_playlist['snippet']['description']
                            if copy_descriptions else ''
                        )
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
                    'https://www.googleapis.com/youtube/v3/playlists?'
                    'part=snippet,status',
                    json=create_data,
                    headers=create_headers,
                    timeout=10
                )

                if create_response.status_code == 200:
                    new_playlist = create_response.json()
                    new_playlist_id = new_playlist['id']

                    # Get videos from original playlist
                    videos_url = (
                        f'https://www.googleapis.com/youtube/v3/playlistItems?'
                        f'part=snippet&playlistId={playlist_id}&maxResults=50'
                        f'&key={api_key}'
                    )
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
                                    'https://www.googleapis.com/youtube/v3/'
                                    'playlistItems?part=snippet',
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
                current_app.logger.error(
                    f'Error copying playlist {playlist_id}: {e}'
                )
                continue

        current_app.logger.info(
            f"Successfully copied {len(copied_playlists)} playlists"
        )

        return jsonify({
            'success': True,
            'copied_playlists': copied_playlists,
            'message': f'Successfully copied {len(copied_playlists)} playlists'
        })

    except Exception as e:
        current_app.logger.error(f"YouTube copy playlists error: {str(e)}")
        return jsonify({'error': f'Error: {str(e)}'}), 500


@youtube_bp.route('/api/youtube/download-audio', methods=['POST'])
def download_youtube_audio():
    """Download audio from YouTube video as MP3"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        save_path = data.get('savePath', 'audio.mp3')

        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # Validate YouTube URL
        parsed_url = urlparse(url)
        if not (parsed_url.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be'] or
                'youtube.com' in parsed_url.netloc):
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        current_app.logger.info(f"YouTube audio download requested: {url}")

        # Create a temporary directory for the download
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Configure yt-dlp options
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/91.0.4472.124 Safari/537.36'
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web']
                        }
                    },
                    'quiet': True,
                    'no_warnings': True,
                }

                # Download using yt-dlp library directly
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

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
                clean_filename = (
                    save_path if save_path.endswith('.mp3')
                    else f"{save_path}.mp3"
                )

                current_app.logger.info(
                    f"YouTube audio download successful: {mp3_file}"
                )

                return jsonify({
                    'success': True,
                    'filename': clean_filename,
                    'fileData': file_data,
                    'originalFilename': mp3_file
                })

            except yt_dlp.utils.DownloadError as e:
                current_app.logger.error(f"YouTube download error: {str(e)}")
                return jsonify({
                    'error': f'Download failed: {str(e)}'
                }), 500
            except Exception as e:
                current_app.logger.error(f"YouTube download error: {str(e)}")
                return jsonify({'error': f'Download error: {str(e)}'}), 500

    except Exception as e:
        current_app.logger.error(f"YouTube audio download error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
