#!/usr/bin/env python3

import requests
import json
import sys

def test_music_downloader_api():
    """Test the YouTube Music Downloader API endpoint"""
    
    # Test URL - a short video
    test_url = "https://www.youtube.com/watch?v=56WBK4ZK_cw"
    
    # API endpoint
    api_url = "http://localhost:5001/api/youtube/download-audio"
    
    # Test data
    test_data = {
        "url": test_url,
        "savePath": "test_audio.mp3"
    }
    
    print(f"Testing YouTube Music Downloader API...")
    print(f"URL: {test_url}")
    print(f"API Endpoint: {api_url}")
    
    try:
        response = requests.post(api_url, json=test_data, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Test Successful!")
            print(f"Filename: {data.get('filename', 'N/A')}")
            print(f"Original Filename: {data.get('originalFilename', 'N/A')}")
            print(f"File Data Length: {len(data.get('fileData', '')) if data.get('fileData') else 0} bytes")
        else:
            print(f"❌ API Test Failed!")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Skye server is running on port 5001")
        print("Run: python3 app.py")
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")

if __name__ == "__main__":
    test_music_downloader_api()