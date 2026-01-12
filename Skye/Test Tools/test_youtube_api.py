#!/usr/bin/env python3
import requests
import json
import sys

API_KEY = "AIzaSyAD7TZNnC7fvpIqeUtxYShJ9kt67z6cjtg"

def get_channel_playlists(channel_input):
    """Get all playlists for a YouTube channel"""
    print(f"Searching for channel: {channel_input}")
    
    channel_id = None
    channel_name = None
    
    # Try different methods to get channel ID
    if channel_input.startswith('UC') and len(channel_input) == 24:
        channel_id = channel_input
    else:
        # Try @handle lookup
        if channel_input.startswith('@'):
            handle = channel_input[1:]
            url = 'https://www.googleapis.com/youtube/v3/channels'
            params = {'part': 'snippet', 'forHandle': handle, 'key': API_KEY}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    channel_id = data['items'][0]['id']
                    channel_name = data['items'][0]['snippet']['title']
        
        # Try search if no channel found
        if not channel_id:
            search_query = channel_input.replace('@', '')
            url = 'https://www.googleapis.com/youtube/v3/search'
            params = {'part': 'snippet', 'q': search_query, 'type': 'channel', 'key': API_KEY, 'maxResults': 5}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    channel_id = data['items'][0]['snippet']['channelId']
                    channel_name = data['items'][0]['snippet']['title']
    
    if not channel_id:
        print(f"Channel '{channel_input}' not found")
        return
    
    print(f"Found channel: {channel_name} (ID: {channel_id})")
    
    # Get playlists with pagination
    playlists = []
    next_page_token = None
    page_count = 0
    
    while True:
        page_count += 1
        print(f"Fetching page {page_count}...")
        
        url = 'https://www.googleapis.com/youtube/v3/playlists'
        params = {
            'part': 'snippet,contentDetails,status',
            'channelId': channel_id,
            'key': API_KEY,
            'maxResults': 50,
            'privacyStatus': 'any'
        }
        
        if next_page_token:
            params['pageToken'] = next_page_token
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"Error fetching playlists: {response.text}")
            return
        
        data = response.json()
        page_playlists = data.get('items', [])
        print(f"Found {len(page_playlists)} playlists on page {page_count}")
        
        for item in page_playlists:
            playlist = {
                'id': item['id'],
                'title': item['snippet']['title'],
                'videoCount': item['contentDetails']['itemCount'],
                'privacy': item['status']['privacyStatus']
            }
            playlists.append(playlist)
        
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
    
    print(f"\nTotal playlists found: {len(playlists)}")
    print("-" * 50)
    
    for i, playlist in enumerate(playlists, 1):
        print(f"{i:2d}. {playlist['title']}")
        print(f"    Videos: {playlist['videoCount']} | Privacy: {playlist['privacy']}")
        print(f"    ID: {playlist['id']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_youtube_api.py '@channel_handle_or_name'")
        print("Example: python test_youtube_api.py '@mkbhd'")
        sys.exit(1)
    
    channel = sys.argv[1]
    get_channel_playlists(channel)