# Skye API Reference

Base URL: `http://localhost:5001`

## System Endpoints

### Health Check
```
GET /health
```
Returns service health status and circuit breaker states.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-13T12:00:00.000000Z",
  "services": {
    "yahoo_finance": {
      "name": "yahoo_finance",
      "state": "closed",
      "healthy": true,
      "failure_count": 0,
      "failure_threshold": 5
    }
  }
}
```

| Status Code | Meaning |
|-------------|---------|
| 200 | All services healthy |
| 503 | One or more services degraded |

### Restart Server
```
POST /api/restart
```
Triggers a server restart via the keep-alive system.

**Response:**
```json
{"status": "restarting"}
```

---

## Dashboard APIs

### Stock Data
```
GET /api/stock-data?symbol=AMZN&period=1y
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| symbol | string | AMZN | Stock ticker symbol |
| period | string | 1y | Time period: `1d`, `1wk`, `1mo`, `1y` |

**Response:**
```json
{
  "dates": ["Jan 01", "Jan 08", ...],
  "values": [150.25, 152.30, ...],
  "symbol": "AMZN"
}
```

### Current Price
```
GET /api/current-price?symbol=AMZN
```

**Response:**
```json
{
  "price": 185.50,
  "symbol": "AMZN"
}
```

### Portfolio Value
```
GET /api/portfolio-value?period=1y
```
Returns portfolio value over time based on configured AMZN shares.

**Response:**
```json
{
  "dates": ["Jan 01", "Jan 08", ...],
  "values": [43125.75, 43710.10, ...],
  "current_value": 53218.50,
  "shares": 287
}
```

### Cash Assets Value
```
GET /api/cash-assets-value?period=1y
```
Returns EUR cash assets converted to USD over time.

**Response:**
```json
{
  "dates": ["Jan 01", "Jan 08", ...],
  "values": [11000.00, 11050.25, ...],
  "current_value": 11200.00,
  "eur_amount": 10000
}
```

### Currency Data (EUR/USD)
```
GET /api/currency-data?period=1y
```

**Response:**
```json
{
  "dates": ["Jan 01", "Jan 08", ...],
  "values": [1.08, 1.09, ...],
  "score": 65,
  "trend": "USD stable (+0.5%)"
}
```

### Currency Rate
```
GET /api/currency-rate
```

**Response:**
```json
{
  "rate": 1.0850,
  "pair": "EUR/USD"
}
```

### XRP Data
```
GET /api/xrp-data?period=1y
```

**Response:**
```json
{
  "dates": ["Jan 01", "Jan 08", ...],
  "values": [0.55, 0.58, ...],
  "current_price": 0.62,
  "portfolio_value": 620.00,
  "quantity": 1000
}
```

### XRP Price
```
GET /api/xrp-price
```

**Response:**
```json
{
  "price": 0.62,
  "symbol": "XRP-USD"
}
```

### Gold Data
```
GET /api/gold-data?period=1y
```

**Response:**
```json
{
  "dates": ["Jan 01", "Jan 08", ...],
  "values": [1950.00, 1975.50, ...],
  "current_price": 2050.00
}
```

### Gold Price
```
GET /api/gold-price
```

**Response:**
```json
{
  "price": 2050.00,
  "symbol": "GC=F"
}
```

### Sell Recommendation
```
GET /api/sell-recommendation
```
AI-powered recommendation based on portfolio analysis.

**Response:**
```json
{
  "recommendation": "HOLD",
  "score": 72,
  "details": "Market conditions are stable...",
  "factors": {
    "stock_trend": 75,
    "currency_impact": 65,
    "overall_portfolio": 72
  }
}
```

### Recommendation History
```
GET /api/recommendation-history
```

**Response:**
```json
{
  "history": [
    {
      "timestamp": "2024-01-13T12:00:00Z",
      "recommendation": "HOLD",
      "score": 72
    }
  ]
}
```

---

## Weather APIs

### Current Weather
```
GET /api/weather?lat=51.05&lon=3.72
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| lat | float | 51.05 | Latitude (default: Ghent) |
| lon | float | 3.72 | Longitude (default: Ghent) |

**Response:**
```json
{
  "temperature": 15.5,
  "feels_like": 14.2,
  "humidity": 75,
  "description": "Partly cloudy",
  "icon": "02d",
  "wind_speed": 12.5,
  "location": "Ghent"
}
```

### Sun Times
```
GET /api/sun-times?lat=51.05&lon=3.72
```

**Response:**
```json
{
  "sunrise": "07:45",
  "sunset": "17:30",
  "day_length": "9h 45m"
}
```

---

## Gemini AI APIs

### List Models
```
GET /api/gemini/models
```

**Response:**
```json
{
  "models": [
    {"id": "gemini-pro", "name": "Gemini Pro"},
    {"id": "gemini-pro-vision", "name": "Gemini Pro Vision"}
  ]
}
```

### Chat
```
POST /api/gemini/chat
Content-Type: application/json
```

**Request:**
```json
{
  "message": "Hello, how are you?",
  "model": "gemini-pro",
  "history": []
}
```

**Response:**
```json
{
  "response": "I'm doing well, thank you for asking!",
  "model": "gemini-pro"
}
```

---

## YouTube APIs

### Get Playlists
```
GET /api/youtube/playlists?account=source
```

| Parameter | Type | Description |
|-----------|------|-------------|
| account | string | `source` or `destination` |

**Response:**
```json
{
  "playlists": [
    {
      "id": "PLxxxxxxx",
      "title": "My Playlist",
      "itemCount": 42,
      "thumbnail": "https://..."
    }
  ]
}
```

### Get Playlist Videos
```
GET /api/youtube/playlist-videos?playlist_id=PLxxxxxxx&account=source
```

**Response:**
```json
{
  "videos": [
    {
      "id": "dQw4w9WgXcQ",
      "title": "Video Title",
      "thumbnail": "https://...",
      "duration": "3:45"
    }
  ]
}
```

### Copy Playlists
```
POST /api/youtube/copy-playlists
Content-Type: application/json
```

**Request:**
```json
{
  "playlist_ids": ["PLxxxxxxx", "PLyyyyyyy"]
}
```

### Download Audio
```
POST /api/youtube/download-audio
Content-Type: application/json
```

**Request:**
```json
{
  "video_url": "https://youtube.com/watch?v=xxxxx"
}
```

### OAuth Authorize
```
GET /oauth/youtube/authorize/<account_type>
```
Initiates OAuth flow. `account_type` is `source` or `destination`.

### OAuth Callback
```
GET /oauth/youtube/callback
```
Handles OAuth callback from Google.

---

## Todo APIs

### Get Todos
```
GET /api/todos
```

**Response:**
```json
{
  "todos": [
    {
      "id": 1,
      "text": "Buy groceries",
      "completed": false,
      "created_at": "2024-01-13T12:00:00Z"
    }
  ]
}
```

### Add Todo
```
POST /api/todos
Content-Type: application/json
```

**Request:**
```json
{
  "text": "New todo item"
}
```

---

## Music Next APIs

### Search
```
GET /api/music-next/search?q=artist+name
```

### Mark Listened
```
POST /api/music-next/listened
Content-Type: application/json
```

**Request:**
```json
{
  "track_id": "spotify:track:xxxxx"
}
```

### Skip Track
```
POST /api/music-next/skip
```

### Go Back
```
POST /api/music-next/back
```

### Get Current
```
GET /api/music-next/current
```

### Get History
```
GET /api/music-next/history
```

### Get Artist Image
```
GET /api/music-next/artist-image?artist=Artist+Name
```

---

## Logs APIs

### Get Logs
```
GET /api/logs?level=all&limit=100
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| level | string | all | Filter: `all`, `error`, `warning`, `info` |
| limit | int | 100 | Max number of logs to return |

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-13 12:00:00",
      "level": "INFO",
      "message": "Server started"
    }
  ]
}
```

### Clear Logs
```
POST /api/logs/clear
```

---

## Tools APIs

### VRT Calculator
```
POST /api/vrt-calculate
Content-Type: application/json
```

**Request:**
```json
{
  "vehicle_type": "car",
  "co2_emissions": 120,
  "fuel_type": "petrol",
  "age_months": 24
}
```

---

## Pages API

### List Pages
```
GET /api/pages
```

**Response:**
```json
{
  "pages": [
    {
      "id": "dashboard",
      "name": "Stock Market",
      "description": "Track your portfolio",
      "icon": "fas fa-chart-line"
    }
  ]
}
```

### Get Page Content
```
GET /page/<page_id>
```

**Response:**
```json
{
  "html": "<div>Page content...</div>"
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `SERVICE_UNAVAILABLE` | 503 | Circuit breaker open, service temporarily unavailable |
| `EXTERNAL_API_ERROR` | 503 | External API (Yahoo, etc.) failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `CONFIG_MISSING` | 500 | Required configuration not set |
