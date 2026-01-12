# YouTube Music Downloader Tool

## Overview
The YouTube Music Downloader is a web-based tool integrated into the Skye Tools page that allows you to download audio from YouTube videos as high-quality MP3 files.

## Features
- Download audio from any YouTube video
- Automatic conversion to MP3 format (320kbps quality)
- File save dialog for choosing download location
- Clean, user-friendly interface
- Error handling and progress feedback

## How to Use

1. **Access the Tool**
   - Open Skye in your browser
   - Navigate to the Tools page
   - Click "Open Tool" on the YouTube Music Downloader card

2. **Download Audio**
   - Paste a YouTube video URL in the input field
   - Click "Browse" to choose where to save the file
   - Click "Download MP3" to start the download
   - The file will be automatically downloaded to your chosen location

## Technical Details

### Dependencies
- `yt-dlp`: Modern YouTube downloader library
- `ffmpeg`: Audio processing (installed via Homebrew)
- `Flask`: Web framework for the API

### API Endpoint
- **POST** `/api/youtube/download-audio`
- **Body**: `{"url": "youtube_url", "savePath": "filename.mp3"}`
- **Response**: Base64-encoded MP3 file data

### File Processing
1. URL validation ensures only YouTube URLs are accepted
2. `yt-dlp` downloads the best available audio quality
3. `ffmpeg` converts audio to MP3 format (320kbps)
4. File is encoded as base64 and sent to browser
5. Browser triggers automatic download

## Browser Compatibility
- **Chrome/Edge**: Full support with File System Access API
- **Firefox/Safari**: Basic support with file input fallback
- **Mobile**: Limited support due to file system restrictions

## Error Handling
- Invalid URLs are rejected with helpful error messages
- Network timeouts are handled gracefully (5-minute limit)
- Missing dependencies are detected and reported
- Download failures provide detailed error information

## Security
- Only YouTube URLs are accepted
- Temporary files are automatically cleaned up
- No persistent storage of downloaded content
- Rate limiting prevents abuse

## Troubleshooting

### Common Issues
1. **"Download failed: HTTP Error 403"**
   - YouTube has blocked the request
   - Try again later or use a different video

2. **"ffmpeg not found"**
   - Install ffmpeg: `brew install ffmpeg`

3. **"Timeout error"**
   - Video is too long or network is slow
   - Try a shorter video or check internet connection

### Supported Formats
- Input: Any YouTube video URL
- Output: MP3 audio files (320kbps, stereo)

## Legal Notice
This tool is for personal use only. Respect YouTube's Terms of Service and copyright laws. Only download content you have permission to use.