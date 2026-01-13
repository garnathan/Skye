import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.config import get_config_value

def get_content():
    """Return the HTML content for the dashboard page"""

    # Load portfolio values from config
    portfolio = get_config_value('portfolio', {})
    amzn_shares = int(portfolio.get('amzn_shares', 0))
    cash_assets_eur = int(portfolio.get('cash_assets_eur', 0))
    xrp_quantity = int(portfolio.get('xrp_quantity', 0))

    # Format values for display
    cash_assets_formatted = "{:,}".format(cash_assets_eur)

    html_content = '''
        <div class="dashboard-page">
            <h2><i class="fas fa-chart-line"></i> Market Dashboard</h2>

            <div class="charts-container">
                <div class="chart-section">
                    <div class="widget-header">
                        <h3><i class="fas fa-building"></i> Amazon Stock (AMZN)</h3>
                        <select id="amznPeriodSelect" class="period-selector">
                            <option value="1d">1 Day</option>
                            <option value="1wk">1 Week</option>
                            <option value="1mo">1 Month</option>
                            <option value="1y" selected>1 Year</option>
                        </select>
                    </div>
                    <div class="current-price" id="amznPrice">Loading current price...</div>
                    <div id="amznChart" class="chart-container">
                        <div class="loading">Loading AMZN data...</div>
                    </div>
                </div>

                <div class="chart-section">
                    <div class="widget-header">
                        <h3><i class="fas fa-wallet"></i> Portfolio Value (''' + str(amzn_shares) + ''' AMZN Shares)</h3>
                        <select id="portfolioPeriodSelect" class="period-selector">
                            <option value="1d">1 Day</option>
                            <option value="1wk">1 Week</option>
                            <option value="1mo">1 Month</option>
                            <option value="1y" selected>1 Year</option>
                        </select>
                    </div>
                    <div class="current-price" id="portfolioValue">Loading portfolio value...</div>
                    <div id="portfolioChart" class="chart-container">
                        <div class="loading">Loading portfolio data...</div>
                    </div>
                </div>
                
                <div class="chart-section">
                    <div class="widget-header">
                        <h3><i class="fas fa-exchange-alt"></i> USD to EUR</h3>
                        <select id="eurPeriodSelect" class="period-selector">
                            <option value="1d">1 Day</option>
                            <option value="1wk">1 Week</option>
                            <option value="1mo">1 Month</option>
                            <option value="1y" selected>1 Year</option>
                        </select>
                    </div>
                    <div class="current-price" id="eurRate">Loading current rate...</div>
                    <div id="usdeurChart" class="chart-container">
                        <div class="loading">Loading USD/EUR data...</div>
                    </div>
                </div>

                <div class="chart-section">
                    <div class="widget-header">
                        <h3><i class="fas fa-money-bill-wave"></i> Cash Assets (€''' + cash_assets_formatted + ''')</h3>
                        <select id="cashPeriodSelect" class="period-selector">
                            <option value="1d">1 Day</option>
                            <option value="1wk">1 Week</option>
                            <option value="1mo">1 Month</option>
                            <option value="1y" selected>1 Year</option>
                        </select>
                    </div>
                    <div class="current-price" id="cashValue">Loading cash value...</div>
                    <div id="cashChart" class="chart-container">
                        <div class="loading">Loading cash data...</div>
                    </div>
                </div>

                <div class="chart-section">
                    <h3><i class="fas fa-chart-area"></i> AMZN Sell Recommendation History - Past 12 Months</h3>
                    <div id="recommendationChart" class="chart-container">
                        <div class="loading">Loading recommendation history...</div>
                    </div>
                </div>

                <div class="chart-section recommendation-section">
                    <h3><i class="fas fa-chart-line"></i> AMZN Current Sell Recommendation</h3>
                    <div class="recommendation" id="sellRecommendation">
                        <div class="loading">Analyzing market trends...</div>
                    </div>
                    <div class="recommendation-details" id="recommendationDetails">
                        <div class="loading">Loading analysis...</div>
                    </div>
                </div>
                
                <div class="chart-section">
                    <div class="widget-header">
                        <h3><i class="fas fa-building"></i> Oracle Stock (ORCL)</h3>
                        <select id="orclPeriodSelect" class="period-selector">
                            <option value="1d">1 Day</option>
                            <option value="1wk">1 Week</option>
                            <option value="1mo">1 Month</option>
                            <option value="1y" selected>1 Year</option>
                        </select>
                    </div>
                    <div class="current-price" id="orclPrice">Loading current price...</div>
                    <div id="orclChart" class="chart-container">
                        <div class="loading">Loading ORCL data...</div>
                    </div>
                </div>

                <div class="chart-section">
                    <div class="widget-header">
                        <h3><i class="fas fa-coins"></i> XRP (''' + str(xrp_quantity) + ''' Coins)</h3>
                        <select id="xrpPeriodSelect" class="period-selector">
                            <option value="1d">1 Day</option>
                            <option value="1wk">1 Week</option>
                            <option value="1mo">1 Month</option>
                            <option value="1y" selected>1 Year</option>
                        </select>
                    </div>
                    <div class="current-price" id="xrpPrice">Loading current price...</div>
                    <div id="xrpChart" class="chart-container">
                        <div class="loading">Loading XRP data...</div>
                    </div>
                </div>
                
                <div class="chart-section">
                    <div class="widget-header">
                        <h3><i class="fas fa-coins"></i> Gold Price</h3>
                        <select id="goldPeriodSelect" class="period-selector">
                            <option value="1d">1 Day</option>
                            <option value="1wk">1 Week</option>
                            <option value="1mo">1 Month</option>
                            <option value="1y" selected>1 Year</option>
                        </select>
                    </div>
                    <div class="current-price" id="goldPrice">Loading current price...</div>
                    <div id="goldChart" class="chart-container">
                        <div class="loading">Loading Gold data...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        .charts-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .chart-section {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            border: 2px solid #dee2e6;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .chart-section h3 {
            margin-bottom: 1rem;
            color: #333;
            font-size: 1.1rem;
        }
        
        .widget-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .period-selector {
            padding: 0.3rem 0.5rem;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background: white;
            color: #495057;
            font-size: 0.9rem;
        }
        
        .chart-container {
            height: 300px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #6c757d;
            font-style: italic;
        }
        
        .current-price {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            text-align: center;
            margin-bottom: 1rem;
            padding: 0.5rem;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .recommendation-section {
            display: flex;
            flex-direction: column;
        }
        
        .recommendation {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            position: relative;
        }
        
        .recommendation.excellent {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
        }
        
        .recommendation.good {
            background: linear-gradient(135deg, #8BC34A, #689F38);
            color: white;
        }
        
        .recommendation.fair {
            background: linear-gradient(135deg, #FF9800, #F57C00);
            color: white;
        }
        
        .recommendation.poor {
            background: linear-gradient(135deg, #FF5722, #D84315);
            color: white;
        }
        
        .recommendation.very.poor {
            background: linear-gradient(135deg, #f44336, #da190b);
            color: white;
        }
        
        .score-display {
            font-size: 1.2rem;
            margin-top: 0.5rem;
            opacity: 0.9;
        }
        
        .score-breakdown {
            display: flex;
            justify-content: space-between;
            margin-top: 0.5rem;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .recommendation-details {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid #dee2e6;
            font-size: 0.9rem;
            line-height: 1.4;
            color: #333;
        }

        @media (max-width: 768px) {
            .charts-container {
                grid-template-columns: 1fr;
            }
        }
        </style>
    '''
    
    js_code = '''
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
        (function() {
        // Portfolio configuration from config file
        const PORTFOLIO_CONFIG = {
            amznShares: ''' + str(amzn_shares) + ''',
            cashAssetsEur: ''' + str(cash_assets_eur) + ''',
            xrpQuantity: ''' + str(xrp_quantity) + '''
        };
        async function fetchWithRetry(url, retries = 3) {
            for (let i = 0; i < retries; i++) {
                try {
                    console.log(`Attempt ${i + 1} for ${url}`);
                    const response = await fetch(url, { timeout: 10000 });
                    if (response.ok) return await response.json();
                    console.warn(`Attempt ${i + 1} failed with status ${response.status}`);
                } catch (error) {
                    console.warn(`Attempt ${i + 1} failed:`, error.message);
                    if (i === retries - 1) throw error;
                    await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                }
            }
        }
        
        function createChart(chartId, labels, data, config) {
            const ctx = document.getElementById(chartId);
            if (!ctx) return;

            ctx.innerHTML = '<canvas></canvas>';
            const canvas = ctx.querySelector('canvas');

            const datasets = [{
                label: config.label,
                data: data,
                borderColor: config.color,
                backgroundColor: config.bgColor,
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }];

            if (config.referenceLine) {
                datasets.push({
                    label: config.referenceLine.label,
                    data: new Array(data.length).fill(config.referenceLine.value),
                    borderColor: config.referenceLine.color,
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    tension: 0
                });
            }

            new Chart(canvas, {
                type: 'line',
                data: { labels, datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: false, grid: { color: config.gridColor } },
                        x: { grid: { color: config.gridColor } }
                    }
                }
            });
        }
        
        async function fetchChartData(url, chartId, dataKey, config) {
            try {
                console.log(`Fetching ${config.name} data...`);
                const data = await fetchWithRetry(url);
                if (data.dates && data[dataKey]) {
                    console.log(`${config.name} data received:`, data.dates.length, 'data points');
                    createChart(chartId, data.dates, data[dataKey], config);
                    return;
                }
                console.warn(`${config.name} data invalid:`, data);
            } catch (error) {
                console.error(`${config.name} fetch failed:`, error);
            }
            document.getElementById(chartId).innerHTML = `<div class="loading">${config.name} data unavailable</div>`;
        }
        
        function setupPeriodSelector(selectorId, fetchFn) {
            const selector = document.getElementById(selectorId);
            if (selector) selector.addEventListener('change', (e) => fetchFn(e.target.value));
        }
        
        const chartConfigs = {
            amzn: { name: 'AMZN', label: 'AMZN Price ($)', color: '#667eea', bgColor: 'rgba(102, 126, 234, 0.1)', gridColor: 'rgba(102, 126, 234, 0.1)' },
            eur: { name: 'USD/EUR', label: 'USD/EUR Rate', color: '#764ba2', bgColor: 'rgba(118, 75, 162, 0.1)', gridColor: 'rgba(118, 75, 162, 0.1)' },
            orcl: { name: 'ORCL', label: 'ORCL Price ($)', color: '#dc2626', bgColor: 'rgba(220, 38, 38, 0.1)', gridColor: 'rgba(220, 38, 38, 0.1)' },
            xrp: { name: 'XRP', label: 'XRP Price (€)', color: '#ff6b35', bgColor: 'rgba(255, 107, 53, 0.1)', gridColor: 'rgba(255, 107, 53, 0.1)', referenceLine: { value: 0.25, label: '€0.25 Reference', color: '#00ff00' } },
            gold: { name: 'Gold', label: 'Gold Price (€)', color: '#ffd700', bgColor: 'rgba(255, 215, 0, 0.1)', gridColor: 'rgba(255, 215, 0, 0.1)', referenceLine: { value: 3321, label: '€3,321 Reference', color: '#ff0000' } }
        };

        const fetchStockData = (period = '1y') => fetchChartData(`/api/stock-data?symbol=AMZN&period=${period}`, 'amznChart', 'prices', chartConfigs.amzn);
        const fetchCurrencyData = (period = '1y') => fetchChartData(`/api/currency-data?period=${period}`, 'usdeurChart', 'rates', chartConfigs.eur);
        const fetchOrclData = (period = '1y') => fetchChartData(`/api/stock-data?symbol=ORCL&period=${period}`, 'orclChart', 'prices', chartConfigs.orcl);
        const fetchGoldData = (period = '1y') => fetchChartData(`/api/gold-data?period=${period}`, 'goldChart', 'prices', chartConfigs.gold);

        async function fetchXrpData(period = '1y') {
            try {
                console.log('Fetching XRP data...');
                const data = await fetchWithRetry(`/api/xrp-data?period=${period}`);
                if (data.dates && data.prices) {
                    console.log('XRP data received:', data.dates.length, 'data points');

                    // Calculate investment value using config
                    const investmentValues = data.prices.map(price => price * PORTFOLIO_CONFIG.xrpQuantity);

                    // Update current price display with both values
                    const currentPrice = data.prices[data.prices.length - 1];
                    const currentInvestment = investmentValues[investmentValues.length - 1];
                    document.getElementById('xrpPrice').innerHTML =
                        `€${currentPrice.toFixed(2)} | Investment: €${Math.round(currentInvestment).toLocaleString('en-US')}`;

                    // Create chart with dual datasets
                    const ctx = document.getElementById('xrpChart');
                    if (!ctx) return;

                    ctx.innerHTML = '<canvas></canvas>';
                    const canvas = ctx.querySelector('canvas');

                    new Chart(canvas, {
                        type: 'line',
                        data: {
                            labels: data.dates,
                            datasets: [
                                {
                                    label: 'XRP Price (€)',
                                    data: data.prices,
                                    borderColor: '#ff6b35',
                                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                                    borderWidth: 3,
                                    fill: true,
                                    tension: 0.4,
                                    yAxisID: 'y'
                                },
                                {
                                    label: `${PORTFOLIO_CONFIG.xrpQuantity} XRP Investment (€)`,
                                    data: investmentValues,
                                    borderColor: '#10b981',
                                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                    borderWidth: 3,
                                    fill: true,
                                    tension: 0.4,
                                    yAxisID: 'y1'
                                },
                                {
                                    label: '€0.25 Reference',
                                    data: new Array(data.prices.length).fill(0.25),
                                    borderColor: '#00ff00',
                                    borderWidth: 2,
                                    borderDash: [5, 5],
                                    fill: false,
                                    pointRadius: 0,
                                    tension: 0,
                                    yAxisID: 'y'
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top'
                                }
                            },
                            scales: {
                                y: {
                                    type: 'linear',
                                    display: true,
                                    position: 'left',
                                    beginAtZero: false,
                                    grid: { color: 'rgba(255, 107, 53, 0.1)' },
                                    title: {
                                        display: true,
                                        text: 'XRP Price (€)'
                                    }
                                },
                                y1: {
                                    type: 'linear',
                                    display: true,
                                    position: 'right',
                                    beginAtZero: false,
                                    grid: { drawOnChartArea: false },
                                    title: {
                                        display: true,
                                        text: 'Investment Value (€)'
                                    }
                                },
                                x: { grid: { color: 'rgba(255, 107, 53, 0.1)' } }
                            }
                        }
                    });
                    return;
                }
                console.warn('XRP data invalid:', data);
            } catch (error) {
                console.error('XRP fetch failed:', error);
            }
            document.getElementById('xrpChart').innerHTML = '<div class="loading">XRP data unavailable</div>';
        }

        async function fetchPortfolioData(period = '1y') {
            try {
                console.log('Fetching portfolio data...');
                const data = await fetchWithRetry(`/api/portfolio-value?period=${period}`);
                if (data.dates && data.values) {
                    console.log('Portfolio data received:', data.dates.length, 'data points');

                    // Update current value display
                    const valueElement = document.getElementById('portfolioValue');
                    const changeSymbol = data.changeAmount >= 0 ? '+' : '';
                    valueElement.innerHTML = `€${Math.round(data.currentValue).toLocaleString('en-US')}`;

                    // Create chart
                    createChart('portfolioChart', data.dates, data.values, {
                        label: 'Portfolio Value (€)',
                        color: '#667eea',
                        bgColor: 'rgba(102, 126, 234, 0.1)',
                        gridColor: 'rgba(102, 126, 234, 0.1)'
                    });
                    return;
                }
                console.warn('Portfolio data invalid:', data);
            } catch (error) {
                console.error('Portfolio fetch failed:', error);
            }
            document.getElementById('portfolioChart').innerHTML = '<div class="loading">Portfolio data unavailable</div>';
            document.getElementById('portfolioValue').textContent = 'Value unavailable';
        }

        async function fetchCashAssetsData(period = '1y') {
            try {
                console.log('Fetching cash assets data...');
                const data = await fetchWithRetry(`/api/cash-assets-value?period=${period}`);
                if (data.dates && data.values) {
                    console.log('Cash assets data received:', data.dates.length, 'data points');

                    // Update current value display
                    const valueElement = document.getElementById('cashValue');
                    valueElement.innerHTML = `€${Math.round(data.currentValue).toLocaleString('en-US')}`;

                    // Create chart
                    createChart('cashChart', data.dates, data.values, {
                        label: 'Cash Value (€)',
                        color: '#10b981',
                        bgColor: 'rgba(16, 185, 129, 0.1)',
                        gridColor: 'rgba(16, 185, 129, 0.1)'
                    });
                    return;
                }
                console.warn('Cash assets data invalid:', data);
            } catch (error) {
                console.error('Cash assets fetch failed:', error);
            }
            document.getElementById('cashChart').innerHTML = '<div class="loading">Cash data unavailable</div>';
            document.getElementById('cashValue').textContent = 'Value unavailable';
        }
        
        async function fetchPrice(url, elementId, formatter, name) {
            try {
                const data = await fetchWithRetry(url);
                const value = data.price || data.rate;
                document.getElementById(elementId).textContent = formatter(value);
                console.log(`${name} updated:`, value);
            } catch (error) {
                console.error(`${name} fetch failed:`, error);
                document.getElementById(elementId).textContent = 'Price unavailable';
            }
        }
        
        async function fetchCurrentPrices() {
            console.log('Fetching current prices...');
            await Promise.all([
                fetchPrice('/api/current-price?symbol=AMZN', 'amznPrice', v => `$${Math.round(v)}`, 'AMZN price'),
                fetchPrice('/api/currency-rate', 'eurRate', v => `${v.toFixed(2)} EUR`, 'USD/EUR rate'),
                fetchPrice('/api/current-price?symbol=ORCL', 'orclPrice', v => `$${Math.round(v)}`, 'ORCL price'),
                fetchPrice('/api/xrp-price', 'xrpPrice', v => `€${v.toFixed(2)}`, 'XRP price'),
                fetchPrice('/api/gold-price', 'goldPrice', v => `€${Math.round(v)}`, 'Gold price')
            ]);
        }
        
        async function fetchRecommendationHistory() {
            try {
                console.log('Fetching recommendation history...');
                const data = await fetchWithRetry('/api/recommendation-history');
                if (data.dates && data.scores) {
                    console.log('Recommendation history received:', data.dates.length, 'data points');
                    const ctx = document.getElementById('recommendationChart');
                    if (ctx) {
                        ctx.innerHTML = '<canvas></canvas>';
                        new Chart(ctx.querySelector('canvas'), {
                            type: 'line',
                            data: {
                                labels: data.dates,
                                datasets: [{
                                    label: 'Sell Recommendation Score',
                                    data: data.scores,
                                    borderColor: '#f093fb',
                                    backgroundColor: 'rgba(240, 147, 251, 0.1)',
                                    borderWidth: 3,
                                    fill: true,
                                    tension: 0.4
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: { legend: { display: false } },
                                scales: {
                                    y: { beginAtZero: true, max: 100, grid: { color: 'rgba(240, 147, 251, 0.1)' }, ticks: { callback: v => v + '%' } },
                                    x: { grid: { color: 'rgba(240, 147, 251, 0.1)' } }
                                }
                            }
                        });
                    }
                    return;
                }
                console.warn('Recommendation history invalid:', data);
            } catch (error) {
                console.error('Recommendation history fetch failed:', error);
            }
            document.getElementById('recommendationChart').innerHTML = '<div class="loading">Recommendation history unavailable</div>';
        }
        
        async function fetchRecommendation() {
            try {
                console.log('Fetching sell recommendation...');
                const data = await fetchWithRetry('/api/sell-recommendation');
                
                const recElement = document.getElementById('sellRecommendation');
                const detailsElement = document.getElementById('recommendationDetails');
                
                recElement.innerHTML = `
                    <div>${data.recommendation}</div>
                    <div class="score-display">${data.score}% Confidence</div>
                    <div class="score-breakdown">
                        <span>Stock: ${data.stockScore}%</span>
                        <span>Currency: ${data.currencyScore}%</span>
                    </div>
                `;
                recElement.className = `recommendation ${data.recommendation.toLowerCase().replace(' ', '.')}`;
                
                detailsElement.innerHTML = `
                    <strong>Market Analysis:</strong><br>
                    • Stock Performance: ${data.stockTrend}<br>
                    • Currency Trend: ${data.currencyTrend}<br><br>
                    <strong>Recommendation:</strong> ${data.reasoning}
                `;
                console.log('Sell recommendation updated:', data.recommendation, data.score + '%');
            } catch (error) {
                console.error('Sell recommendation fetch failed:', error);
                document.getElementById('sellRecommendation').textContent = 'Analysis unavailable';
                document.getElementById('recommendationDetails').textContent = 'Error loading recommendation';
            }
        }
        

        // Auto-refresh interval (60 seconds for prices)
        const AUTO_REFRESH_INTERVAL = 60000;

        // Wait for Chart.js to be available before initializing
        function initDashboard() {
            fetchCurrentPrices();
            fetchStockData('1y');
            fetchPortfolioData('1y');
            fetchCurrencyData('1y');
            fetchCashAssetsData('1y');
            fetchOrclData('1y');
            fetchXrpData('1y');
            fetchGoldData('1y');
            fetchRecommendationHistory();
            fetchRecommendation();
            setupPeriodSelector('amznPeriodSelect', fetchStockData);
            setupPeriodSelector('portfolioPeriodSelect', fetchPortfolioData);
            setupPeriodSelector('eurPeriodSelect', fetchCurrencyData);
            setupPeriodSelector('cashPeriodSelect', fetchCashAssetsData);
            setupPeriodSelector('orclPeriodSelect', fetchOrclData);
            setupPeriodSelector('xrpPeriodSelect', fetchXrpData);
            setupPeriodSelector('goldPeriodSelect', fetchGoldData);

            // Register auto-refresh for prices (updates every 60 seconds)
            if (window.autoRefresh) {
                window.autoRefresh.register('dashboard-prices', () => {
                    console.log('Auto-refreshing dashboard prices...');
                    fetchCurrentPrices();
                }, AUTO_REFRESH_INTERVAL);
            }
        }

        // Check if Chart.js is loaded, retry until available
        function waitForChartJs(callback, maxAttempts = 50) {
            let attempts = 0;
            const check = () => {
                attempts++;
                if (typeof Chart !== 'undefined') {
                    console.log('Chart.js ready, initializing dashboard...');
                    callback();
                } else if (attempts < maxAttempts) {
                    setTimeout(check, 100);
                } else {
                    console.error('Chart.js failed to load');
                }
            };
            check();
        }

        waitForChartJs(initDashboard);
        })();
        </script>
    '''
    
    return {
        'html': html_content + js_code
    }