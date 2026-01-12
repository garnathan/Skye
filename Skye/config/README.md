# Configuration Directory

This directory contains all configuration files for the Skye application.

## Files

- **config.json** - Main application configuration (API keys, settings)
- **music_recommendations.json** - Music Next recommendation history
- **.env.example** - Example environment variables template
- **.env** - Environment variables (not committed to git)

## Setup

1. Copy `.env.example` to `.env` in the project root
2. Create `config.json` based on your needs:

```json
{
  "gemini_api_key": "your_gemini_api_key_here",
  "youtube_api_key": "your_youtube_api_key_here",
  "youtube_oauth": {
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here"
  },
  "user_name": "Your Name"
}
```

3. The application will automatically create `music_recommendations.json` when you use Music Next

## Note

All files in this directory except `.env.example` and this README are ignored by git to protect sensitive information.
