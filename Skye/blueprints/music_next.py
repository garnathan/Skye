"""
Music Next API blueprint
Handles artist search, recommendations, and navigation for music discovery
"""
import os
import re
import json
import urllib.parse
import urllib.request
from flask import Blueprint, jsonify, request, current_app
import requests

music_next_bp = Blueprint('music_next', __name__)

MUSIC_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'music_recommendations.json')
DEFAULT_MUSIC_CONFIG = {'artists': {}, 'current_search': None}


def get_config_path():
    """Get the path to music_recommendations.json"""
    return MUSIC_CONFIG_PATH


def ensure_music_config_exists():
    """Create music_recommendations.json if it doesn't exist"""
    if not os.path.exists(MUSIC_CONFIG_PATH):
        os.makedirs(os.path.dirname(MUSIC_CONFIG_PATH), exist_ok=True)
        with open(MUSIC_CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_MUSIC_CONFIG, f, indent=2)


@music_next_bp.route('/api/music-next/search', methods=['GET'])
def music_next_search():
    """Search for similar artists on music-map.com"""
    try:
        artist = request.args.get('artist', '').strip()
        current_app.logger.info(f"Music Next search requested for artist: {artist}")

        if not artist:
            current_app.logger.warning(
                "Music Next search failed: No artist name provided"
            )
            return jsonify({'error': 'Artist name required'}), 400

        # Fetch from music-map.com
        artist_slug = artist.lower().replace(' ', '+')
        url = f'https://www.music-map.com/{artist_slug}'
        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            current_app.logger.error(
                f"Music-map.com returned status {response.status_code} "
                f"for artist: {artist}"
            )
            return jsonify({'error': 'Failed to fetch artist data'}), 500

        # Parse HTML to extract similar artists
        html = response.text
        similar_artists = []

        # Extract artist links from the HTML
        pattern = r'<a href="([^"]+)" class=S id=s\d+>([^<]+)</a>'
        matches = re.findall(pattern, html)

        for match in matches:
            artist_name = match[1]
            # Skip the search artist itself
            if artist_name.lower() != artist.lower():
                similar_artists.append(artist_name)

        if not similar_artists:
            current_app.logger.warning(f"No similar artists found for: {artist}")
            return jsonify({'error': 'No similar artists found'}), 404

        current_app.logger.info(
            f"Found {len(similar_artists)} similar artists for: {artist}"
        )

        # Load or create music recommendations state
        config_path = get_config_path()
        ensure_music_config_exists()

        with open(config_path, 'r') as f:
            music_config = json.load(f)

        # Check if this is a re-search
        artist_key = artist.lower()
        if artist_key in music_config['artists']:
            existing_artists = set(
                music_config['artists'][artist_key].get('all_recommendations', [])
            )
            new_artists = [
                a for a in similar_artists if a not in existing_artists
            ]

            # If re-searching, add new artists to the pending list
            if new_artists:
                music_config['artists'][artist_key]['all_recommendations'].extend(
                    new_artists
                )
                music_config['artists'][artist_key]['pending'].extend(new_artists)
        else:
            # New search
            music_config['artists'][artist_key] = {
                'search_artist': artist,
                'all_recommendations': similar_artists.copy(),
                'pending': similar_artists.copy(),
                'listened': [],
                # Track navigation history
                'history': [similar_artists[0]] if similar_artists else [],
                'current_index': 0  # Current position in history
            }

        # Set as current search
        music_config['current_search'] = artist_key

        # Save config
        with open(config_path, 'w') as f:
            json.dump(music_config, f, indent=2)

        # Return current state
        artist_data = music_config['artists'][artist_key]
        current_rec = artist_data['pending'][0] if artist_data['pending'] else None

        return jsonify({
            'search_artist': artist,
            'current_recommendation': current_rec,
            'total_count': len(artist_data['all_recommendations']),
            'listened_count': len(artist_data['listened']),
            'current_index': artist_data.get('current_index', 0)
        })

    except Exception as e:
        current_app.logger.error(
            f"Music Next search error for artist {artist}: {str(e)}"
        )
        return jsonify({'error': str(e)}), 500


@music_next_bp.route('/api/music-next/listened', methods=['POST'])
def music_next_listened():
    """Mark a recommendation as listened"""
    try:
        current_app.logger.info("Music Next: Marking recommendation as listened")
        data = request.get_json()
        artist = data.get('artist', '').strip()
        recommended = data.get('recommended', '').strip()

        if not artist or not recommended:
            return jsonify({'error': 'Invalid request'}), 400

        config_path = get_config_path()
        ensure_music_config_exists()

        with open(config_path, 'r') as f:
            music_config = json.load(f)

        artist_key = artist.lower()
        if artist_key not in music_config.get('artists', {}):
            return jsonify({'error': 'Artist not found'}), 404

        artist_data = music_config['artists'][artist_key]

        # Initialize history and current_index if not present
        if 'history' not in artist_data:
            artist_data['history'] = []
        if 'current_index' not in artist_data:
            artist_data['current_index'] = 0

        # Move from pending to listened
        if recommended in artist_data['pending']:
            artist_data['pending'].remove(recommended)
            if recommended not in artist_data['listened']:
                artist_data['listened'].append(recommended)

        # Move forward in navigation
        if artist_data['current_index'] < len(artist_data['history']) - 1:
            # Navigate to next item in history
            artist_data['current_index'] += 1
            next_rec = artist_data['history'][artist_data['current_index']]
        else:
            # At the end of history, get next from pending and add to history
            next_rec = artist_data['pending'][0] if artist_data['pending'] else None
            if next_rec:
                artist_data['history'].append(next_rec)
                artist_data['current_index'] += 1

        # Save config
        with open(config_path, 'w') as f:
            json.dump(music_config, f, indent=2)

        return jsonify({
            'search_artist': artist,
            'current_recommendation': next_rec,
            'total_count': len(artist_data['all_recommendations']),
            'listened_count': len(artist_data['listened']),
            'current_index': artist_data.get('current_index', 0)
        })

    except Exception as e:
        current_app.logger.error(f"Music Next listened error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@music_next_bp.route('/api/music-next/skip', methods=['POST'])
def music_next_skip():
    """Skip a recommendation (moves it to the end of the queue)"""
    try:
        data = request.get_json()
        artist = data.get('artist', '').strip()
        recommended = data.get('recommended', '').strip()

        if not artist or not recommended:
            return jsonify({'error': 'Invalid request'}), 400

        config_path = get_config_path()
        ensure_music_config_exists()

        with open(config_path, 'r') as f:
            music_config = json.load(f)

        artist_key = artist.lower()
        if artist_key not in music_config.get('artists', {}):
            return jsonify({'error': 'Artist not found'}), 404

        artist_data = music_config['artists'][artist_key]

        # Initialize history and current_index if not present
        if 'history' not in artist_data:
            artist_data['history'] = []
        if 'current_index' not in artist_data:
            artist_data['current_index'] = 0

        # Move from front to back of pending queue
        if recommended in artist_data['pending']:
            artist_data['pending'].remove(recommended)
            artist_data['pending'].append(recommended)

        # Move forward in navigation
        if artist_data['current_index'] < len(artist_data['history']) - 1:
            # Navigate to next item in history
            artist_data['current_index'] += 1
            next_rec = artist_data['history'][artist_data['current_index']]
        else:
            # At the end of history, get next from pending and add to history
            next_rec = artist_data['pending'][0] if artist_data['pending'] else None
            if next_rec:
                artist_data['history'].append(next_rec)
                artist_data['current_index'] += 1

        # Save config
        with open(config_path, 'w') as f:
            json.dump(music_config, f, indent=2)

        return jsonify({
            'search_artist': artist,
            'current_recommendation': next_rec,
            'total_count': len(artist_data['all_recommendations']),
            'listened_count': len(artist_data['listened']),
            'current_index': artist_data.get('current_index', 0)
        })

    except Exception as e:
        current_app.logger.error(f"Music Next skip error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@music_next_bp.route('/api/music-next/back', methods=['POST'])
def music_next_back():
    """Go back to the previous recommendation"""
    try:
        data = request.get_json()
        artist = data.get('artist', '').strip()

        if not artist:
            return jsonify({'error': 'Invalid request'}), 400

        config_path = get_config_path()
        ensure_music_config_exists()

        with open(config_path, 'r') as f:
            music_config = json.load(f)

        artist_key = artist.lower()
        if artist_key not in music_config.get('artists', {}):
            return jsonify({'error': 'Artist not found'}), 404

        artist_data = music_config['artists'][artist_key]

        # Initialize history and current_index if not present
        if 'history' not in artist_data:
            artist_data['history'] = []
        if 'current_index' not in artist_data:
            artist_data['current_index'] = 0

        # Check if we can go back in history
        if artist_data['current_index'] <= 0:
            return jsonify({
                'error': 'No previous recommendations to go back to'
            }), 400

        # Move back one step in history
        artist_data['current_index'] -= 1
        previous_rec = artist_data['history'][artist_data['current_index']]

        # Save config
        with open(config_path, 'w') as f:
            json.dump(music_config, f, indent=2)

        return jsonify({
            'search_artist': artist,
            'current_recommendation': previous_rec,
            'total_count': len(artist_data['all_recommendations']),
            'listened_count': len(artist_data['listened']),
            'current_index': artist_data['current_index']
        })

    except Exception as e:
        current_app.logger.error(f"Music Next back error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@music_next_bp.route('/api/music-next/current', methods=['GET'])
def music_next_current():
    """Get current recommendation state"""
    try:
        config_path = get_config_path()
        ensure_music_config_exists()

        with open(config_path, 'r') as f:
            music_config = json.load(f)

        current_search = music_config.get('current_search')
        if not current_search or current_search not in music_config['artists']:
            return jsonify({})

        artist_data = music_config['artists'][current_search]

        # Initialize history and current_index if not present
        if 'history' not in artist_data:
            artist_data['history'] = []
        if 'current_index' not in artist_data:
            artist_data['current_index'] = 0

        # Get current recommendation
        current_rec = artist_data['pending'][0] if artist_data['pending'] else None

        # If history is empty but we have a current recommendation,
        # initialize history
        if not artist_data['history'] and current_rec:
            artist_data['history'] = [current_rec]
            artist_data['current_index'] = 0
            # Save the initialized state
            with open(config_path, 'w') as f:
                json.dump(music_config, f, indent=2)
        # Get from history if we have history
        elif (artist_data['history'] and
              artist_data['current_index'] < len(artist_data['history'])):
            current_rec = artist_data['history'][artist_data['current_index']]

        return jsonify({
            'search_artist': artist_data['search_artist'],
            'current_recommendation': current_rec,
            'total_count': len(artist_data['all_recommendations']),
            'listened_count': len(artist_data['listened']),
            'current_index': artist_data.get('current_index', 0)
        })

    except Exception as e:
        current_app.logger.error(f"Music Next current error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@music_next_bp.route('/api/music-next/history', methods=['GET'])
def music_next_history():
    """Get search history"""
    try:
        config_path = get_config_path()
        ensure_music_config_exists()

        with open(config_path, 'r') as f:
            music_config = json.load(f)

        history = [
            data['search_artist']
            for data in music_config.get('artists', {}).values()
        ]

        return jsonify({'history': history})

    except Exception as e:
        current_app.logger.error(f"Music Next history error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@music_next_bp.route('/api/music-next/artist-image', methods=['GET'])
def music_next_artist_image():
    """Get artist image from Wikipedia"""
    try:
        artist = request.args.get('artist', '').strip()
        if not artist:
            return jsonify({'error': 'Artist name required'}), 400

        # Use urllib instead of requests to avoid SSL issues
        # Try Wikipedia API for artist image
        encoded_artist = urllib.parse.quote(artist)
        wiki_search_url = (
            f'https://en.wikipedia.org/w/api.php?action=query&format=json'
            f'&prop=pageimages&piprop=original&titles={encoded_artist}'
        )

        req = urllib.request.Request(
            wiki_search_url, headers={'User-Agent': 'Skye/1.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            wiki_data = json.loads(response.read().decode('utf-8'))
            pages = wiki_data.get('query', {}).get('pages', {})

            for page_id, page in pages.items():
                if 'original' in page:
                    return jsonify({'image_url': page['original']['source']})

        # If Wikipedia didn't work, try searching for the artist page first
        search_url = (
            f'https://en.wikipedia.org/w/api.php?action=opensearch'
            f'&format=json&search={encoded_artist}&limit=1'
        )
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Skye/1.0'})

        with urllib.request.urlopen(req, timeout=5) as response:
            search_data = json.loads(response.read().decode('utf-8'))

            if len(search_data) > 1 and len(search_data[1]) > 0:
                # Get the first search result title
                page_title = search_data[1][0]
                encoded_title = urllib.parse.quote(page_title)

                # Now get the image for this page
                image_url = (
                    f'https://en.wikipedia.org/w/api.php?action=query'
                    f'&format=json&prop=pageimages&piprop=original'
                    f'&titles={encoded_title}'
                )
                req = urllib.request.Request(
                    image_url, headers={'User-Agent': 'Skye/1.0'}
                )

                with urllib.request.urlopen(req, timeout=5) as img_response:
                    img_data = json.loads(img_response.read().decode('utf-8'))
                    pages = img_data.get('query', {}).get('pages', {})

                    for page_id, page in pages.items():
                        if 'original' in page:
                            return jsonify({'image_url': page['original']['source']})

        # No image found
        return jsonify({'image_url': None})

    except Exception as e:
        current_app.logger.error(f"Music Next artist image error: {str(e)}")
        return jsonify({'error': str(e)}), 500
