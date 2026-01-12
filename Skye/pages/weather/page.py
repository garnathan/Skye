def get_content():
    """Return the HTML content for the Weather page"""

    html_content = '''
    <div class="weather-container">
        <div class="weather-header">
            <h1><i class="fas fa-map-marker-alt"></i> Killiney, Dublin</h1>
            <p class="last-updated">Loading weather data...</p>
        </div>

        <div class="current-weather">
            <div class="weather-main">
                <div class="weather-icon-large" id="currentIcon">
                    <i class="fas fa-spinner fa-spin"></i>
                </div>
                <div class="weather-temp">
                    <div class="temp-value" id="currentTemp">--</div>
                    <div class="temp-unit">°C</div>
                </div>
                <div class="weather-wind">
                    <div class="wind-arrow" id="windArrow">
                        <i class="fas fa-arrow-up"></i>
                    </div>
                    <div class="wind-speed-value" id="windSpeedValue">--</div>
                    <div class="wind-unit">km/h</div>
                </div>
                <div class="feels-like" id="feelsLike">Feels like --°C</div>
                <div class="weather-description" id="weatherDescription">Loading...</div>
            </div>

            <div class="weather-details">
                <div class="detail-item">
                    <i class="fas fa-tint"></i>
                    <div class="detail-content">
                        <span class="detail-label">Humidity</span>
                        <span class="detail-value" id="humidity">--%</span>
                    </div>
                </div>
                <div class="detail-item">
                    <i class="fas fa-cloud"></i>
                    <div class="detail-content">
                        <span class="detail-label">Cloud Cover</span>
                        <span class="detail-value" id="cloudCover">--%</span>
                    </div>
                </div>
                <div class="detail-item">
                    <i class="fas fa-sun"></i>
                    <div class="detail-content">
                        <span class="detail-label">Sunset</span>
                        <span class="detail-value" id="sunset">--:--</span>
                    </div>
                </div>
                <div class="detail-item">
                    <i class="fas fa-lightbulb"></i>
                    <div class="detail-content">
                        <span class="detail-label">Usable Light</span>
                        <span class="detail-value" id="usableLight">--:--</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="hourly-forecast">
            <h2><i class="fas fa-clock"></i> Today's Hourly Forecast</h2>
            <div class="hourly-scroll" id="hourlyForecast">
                <div class="loading">Loading hourly forecast...</div>
            </div>
        </div>

        <div class="weekly-forecast">
            <h2><i class="fas fa-calendar-week"></i> Weekly Forecast</h2>
            <div class="weekly-grid" id="weeklyForecast">
                <div class="loading">Loading weekly forecast...</div>
            </div>
        </div>

        <div class="attribution">
            <p>Weather data provided by <strong>Met Éireann</strong> - Copyright Met Éireann</p>
        </div>
    </div>

    <style>
    .weather-container {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    .weather-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .weather-header h1 {
        font-size: 2.5rem;
        color: #333;
        margin-bottom: 0.5rem;
    }

    .last-updated {
        color: #666;
        font-size: 0.9rem;
    }

    .current-weather {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        color: white;
    }

    .weather-main {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }

    .weather-icon-large {
        font-size: 6rem;
    }

    .weather-temp,
    .weather-wind {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 180px;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }

    .temp-value,
    .wind-speed-value {
        font-size: 5rem;
        font-weight: bold;
        line-height: 1;
    }

    .temp-unit,
    .wind-unit {
        font-size: 1.5rem;
        margin-top: 0.5rem;
        opacity: 0.8;
    }

    .wind-arrow {
        font-size: 4rem;
        margin-bottom: 1rem;
        transition: transform 0.5s ease;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
    }

    .feels-like {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        text-align: center;
        width: 100%;
    }

    .weather-description {
        font-size: 1.5rem;
        text-transform: capitalize;
        text-align: center;
        width: 100%;
        margin-top: 0.5rem;
    }

    .weather-details {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }

    .detail-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }

    .detail-item i {
        font-size: 1.5rem;
        opacity: 0.9;
    }

    .detail-content {
        display: flex;
        flex-direction: column;
    }

    .detail-label {
        font-size: 0.85rem;
        opacity: 0.8;
    }

    .detail-value {
        font-size: 1.1rem;
        font-weight: bold;
    }

    .hourly-forecast {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }

    .hourly-forecast h2 {
        color: #333;
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
    }

    .hourly-scroll {
        display: flex;
        gap: 1rem;
        overflow-x: auto;
        padding-bottom: 1rem;
    }

    .hourly-scroll::-webkit-scrollbar {
        height: 8px;
    }

    .hourly-scroll::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }

    .hourly-scroll::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }

    .hourly-item {
        min-width: 120px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.5rem 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .hourly-time {
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }

    .hourly-icon {
        font-size: 2.5rem;
        margin: 0.5rem 0;
    }

    .hourly-temp {
        font-size: 1.3rem;
        font-weight: bold;
        color: #667eea;
        margin: 0.5rem 0;
    }

    .hourly-wind {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.5rem;
    }

    .hourly-rain {
        font-size: 0.85rem;
        color: #4a90e2;
        margin-top: 0.25rem;
    }

    .weekly-forecast {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }

    .weekly-forecast h2 {
        color: #333;
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
    }

    .weekly-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
    }

    .weekly-item {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.5rem 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .weekly-day {
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }

    .weekly-date {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.5rem;
    }

    .weekly-icon {
        font-size: 3rem;
        margin: 0.5rem 0;
    }

    .weekly-temp-range {
        font-size: 1.1rem;
        font-weight: bold;
        color: #667eea;
        margin: 0.5rem 0;
    }

    .weekly-temp-high {
        color: #e74c3c;
    }

    .weekly-temp-low {
        color: #3498db;
    }

    .weekly-description {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.5rem;
    }

    .attribution {
        text-align: center;
        padding: 1rem;
        color: #666;
        font-size: 0.85rem;
    }

    /* Weather icon colors */
    .fa-sun {
        color: #FFD700;
        filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.6));
    }

    .fa-moon {
        color: #F0E68C;
        filter: drop-shadow(0 0 8px rgba(240, 230, 140, 0.5));
    }

    .fa-cloud {
        color: #B0C4DE;
    }

    .fa-cloud-sun {
        color: #FFD700;
    }

    .fa-cloud-sun-rain {
        color: #4A90E2;
    }

    .fa-cloud-rain {
        color: #4A90E2;
    }

    .fa-cloud-showers-heavy {
        color: #1E90FF;
    }

    .fa-cloud-meatball {
        color: #87CEEB;
    }

    .fa-snowflake {
        color: #E0F7FF;
        filter: drop-shadow(0 0 3px rgba(224, 247, 255, 0.8));
    }

    .fa-smog {
        color: #D3D3D3;
    }

    .fa-bolt {
        color: #FFD700;
        filter: drop-shadow(0 0 5px rgba(255, 215, 0, 0.7));
    }

    .fa-wind {
        color: #B0C4DE;
    }

    .fa-tint {
        color: #4A90E2;
    }

    .loading {
        text-align: center;
        padding: 2rem;
        color: #666;
    }

    @media (max-width: 768px) {
        .weather-container {
            padding: 1rem;
        }

        .current-weather {
            padding: 2rem 1rem;
        }

        .weather-main {
            gap: 1rem;
        }

        .temp-value,
        .wind-speed-value {
            font-size: 3.5rem;
        }

        .weather-temp,
        .weather-wind {
            min-width: 140px;
            padding: 1rem;
        }

        .wind-arrow {
            font-size: 3rem;
        }

        .weather-icon-large {
            font-size: 4rem;
        }

        .weather-details {
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
    }
    </style>
    '''

    js_code = '''
    <script>
    // Killiney, Dublin coordinates
    const KILLINEY_LAT = 53.2631;
    const KILLINEY_LONG = -6.1083;

    let cachedSunsetTime = null;
    let cachedSunriseTime = null;

    async function fetchSunTimes() {
        try {
            const response = await fetch(`/api/sun-times?lat=${KILLINEY_LAT}&lng=${KILLINEY_LONG}`);
            const data = await response.json();
            if (data.sunset && data.sunrise) {
                cachedSunsetTime = data.sunset;
                cachedSunriseTime = data.sunrise;
                return data;
            }
        } catch (error) {
            console.error('Failed to fetch sun times:', error);
        }
        return null;
    }

    function calculateSunsetHour(sunsetTime) {
        // Convert sunset time string (HH:MM) to decimal hour
        if (!sunsetTime) return 18.5; // Fallback to average
        const [hours, minutes] = sunsetTime.split(':').map(Number);
        return hours + minutes / 60;
    }

    function isNighttime(timestamp) {
        // Check if it's nighttime based on sunset time
        if (!timestamp) {
            timestamp = new Date();
        }
        const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
        const hour = date.getHours();
        const minute = date.getMinutes();
        const currentTime = hour + minute / 60;

        // Use cached sunset/sunrise times
        const sunsetHour = calculateSunsetHour(cachedSunsetTime);
        const sunriseHour = cachedSunriseTime ? calculateSunsetHour(cachedSunriseTime) : 6;

        // Nighttime is after sunset or before sunrise
        return currentTime >= sunsetHour || currentTime < sunriseHour;
    }

    function getWeatherIcon(symbolCode, timestamp = null) {
        // Map Met Éireann weather symbols to Font Awesome icons
        const iconMap = {
            'Sun': isNighttime(timestamp) ? 'fa-moon' : 'fa-sun',
            'LightCloud': 'fa-cloud-sun',
            'PartlyCloud': 'fa-cloud-sun',
            'Cloud': 'fa-cloud',
            'LightRainSun': 'fa-cloud-sun-rain',
            'LightRain': 'fa-cloud-rain',
            'Rain': 'fa-cloud-showers-heavy',
            'HeavyRain': 'fa-cloud-showers-heavy',
            'Sleet': 'fa-cloud-meatball',
            'Snow': 'fa-snowflake',
            'Fog': 'fa-smog',
            'Thunder': 'fa-bolt'
        };

        for (const [key, icon] of Object.entries(iconMap)) {
            if (symbolCode && symbolCode.includes(key)) {
                return icon;
            }
        }
        return 'fa-cloud';
    }

    function getWindDirection(degrees) {
        const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
        const index = Math.round(degrees / 22.5) % 16;
        return directions[index];
    }

    async function fetchWeatherData() {
        try {
            // Fetch both weather and sun times in parallel
            const [weatherResponse, sunData] = await Promise.all([
                fetch(`/api/weather?lat=${KILLINEY_LAT}&long=${KILLINEY_LONG}`),
                fetchSunTimes()
            ]);

            const data = await weatherResponse.json();

            if (data.error) {
                console.error('Weather API error:', data.error);
                return;
            }

            updateCurrentWeather(data.current, sunData);
            updateHourlyForecast(data.hourly);
            updateWeeklyForecast(data.hourly);

            const lastUpdated = new Date().toLocaleString('en-IE', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            document.querySelector('.last-updated').textContent = `Last updated: ${lastUpdated}`;

        } catch (error) {
            console.error('Failed to fetch weather:', error);
            document.querySelector('.last-updated').textContent = 'Failed to load weather data';
        }
    }

    function calculateFeelsLike(temp, windSpeed, humidity) {
        // Simple feels-like calculation using wind chill and heat index
        const windKmh = windSpeed;

        if (temp < 10 && windKmh > 4.8) {
            // Wind chill formula
            const windChill = 13.12 + 0.6215 * temp - 11.37 * Math.pow(windKmh, 0.16) + 0.3965 * temp * Math.pow(windKmh, 0.16);
            return windChill;
        } else if (temp > 20) {
            // Heat index approximation
            const heatIndex = temp + 0.33 * (humidity / 100) * temp - 0.7 * windKmh - 4;
            return heatIndex;
        }

        return temp;
    }

    function updateCurrentWeather(current, sunData) {
        const iconClass = getWeatherIcon(current.symbol, current.time);
        document.getElementById('currentIcon').innerHTML = `<i class="fas ${iconClass}"></i>`;
        document.getElementById('currentTemp').textContent = Math.round(current.temperature);

        // Update wind display with rotation
        document.getElementById('windSpeedValue').textContent = Math.round(current.windSpeed);
        const windArrow = document.getElementById('windArrow');
        windArrow.style.transform = `rotate(${current.windDirection}deg)`;
        windArrow.title = `Wind from ${getWindDirection(current.windDirection)}`;

        // Calculate and display feels like temperature
        const feelsLike = calculateFeelsLike(current.temperature, current.windSpeed, current.humidity);
        document.getElementById('feelsLike').textContent = `Feels like ${Math.round(feelsLike)}°C`;

        document.getElementById('weatherDescription').textContent = current.description || 'Current conditions';
        document.getElementById('humidity').textContent = `${current.humidity}%`;
        document.getElementById('cloudCover').textContent = `${current.cloudCover}%`;

        // Display sunset time from API
        if (sunData && sunData.sunset) {
            document.getElementById('sunset').textContent = sunData.sunset;
        } else {
            document.getElementById('sunset').textContent = '--:--';
        }

        // Display usable light (civil twilight end) time from API
        if (sunData && sunData.civil_twilight_end) {
            document.getElementById('usableLight').textContent = sunData.civil_twilight_end;
        } else {
            document.getElementById('usableLight').textContent = '--:--';
        }
    }

    function updateHourlyForecast(hourly) {
        const container = document.getElementById('hourlyForecast');

        if (!hourly || hourly.length === 0) {
            container.innerHTML = '<div class="loading">No hourly forecast available</div>';
            return;
        }

        container.innerHTML = hourly.map(hour => {
            const time = new Date(hour.time);
            const timeStr = time.toLocaleTimeString('en-IE', { hour: '2-digit', minute: '2-digit' });
            const iconClass = getWeatherIcon(hour.symbol, hour.time);

            return `
                <div class="hourly-item">
                    <div class="hourly-time">${timeStr}</div>
                    <div class="hourly-icon"><i class="fas ${iconClass}"></i></div>
                    <div class="hourly-temp">${Math.round(hour.temperature)}°C</div>
                    <div class="hourly-wind"><i class="fas fa-wind"></i> ${Math.round(hour.windSpeed)} km/h</div>
                    ${hour.precipitation > 0 ? `<div class="hourly-rain"><i class="fas fa-tint"></i> ${hour.precipitation.toFixed(1)} mm</div>` : ''}
                </div>
            `;
        }).join('');
    }

    function updateWeeklyForecast(hourly) {
        const container = document.getElementById('weeklyForecast');

        if (!hourly || hourly.length === 0) {
            container.innerHTML = '<div class="loading">No weekly forecast available</div>';
            return;
        }

        // Group hourly data by day and calculate daily high/low
        const dailyData = {};

        hourly.forEach(hour => {
            const date = new Date(hour.time);
            const dateKey = date.toLocaleDateString('en-IE', { year: 'numeric', month: '2-digit', day: '2-digit' });

            if (!dailyData[dateKey]) {
                dailyData[dateKey] = {
                    date: date,
                    temps: [],
                    symbols: [],
                    precipitation: []
                };
            }

            dailyData[dateKey].temps.push(hour.temperature);
            dailyData[dateKey].symbols.push(hour.symbol);
            dailyData[dateKey].precipitation.push(hour.precipitation);
        });

        // Convert to array and take first 7 days
        const weeklyItems = Object.values(dailyData).slice(0, 7);

        container.innerHTML = weeklyItems.map(day => {
            const dayName = day.date.toLocaleDateString('en-IE', { weekday: 'short' });
            const dateStr = day.date.toLocaleDateString('en-IE', { month: 'short', day: 'numeric' });

            const highTemp = Math.round(Math.max(...day.temps));
            const lowTemp = Math.round(Math.min(...day.temps));

            // Use the most common symbol for the day (noon-ish)
            const middleIndex = Math.floor(day.symbols.length / 2);
            const daySymbol = day.symbols[middleIndex] || day.symbols[0];
            const iconClass = getWeatherIcon(daySymbol, day.date);

            const totalPrecip = day.precipitation.reduce((a, b) => a + b, 0);
            const precipText = totalPrecip > 0 ? `${totalPrecip.toFixed(1)}mm` : '';

            return `
                <div class="weekly-item">
                    <div class="weekly-day">${dayName}</div>
                    <div class="weekly-date">${dateStr}</div>
                    <div class="weekly-icon"><i class="fas ${iconClass}"></i></div>
                    <div class="weekly-temp-range">
                        <span class="weekly-temp-high">${highTemp}°</span> /
                        <span class="weekly-temp-low">${lowTemp}°</span>
                    </div>
                    ${precipText ? `<div class="weekly-description"><i class="fas fa-tint"></i> ${precipText}</div>` : ''}
                </div>
            `;
        }).join('');
    }

    // Load weather data on page load
    setTimeout(() => {
        fetchWeatherData();
        // Refresh every 10 minutes
        setInterval(fetchWeatherData, 600000);
    }, 100);
    </script>
    '''

    return {
        'html': html_content + js_code
    }
