def get_content():
    """Return the HTML content for the Logs page"""

    html_content = '''
    <div class="logs-container">
        <h2><i class="fas fa-file-alt"></i> System Logs</h2>
        <p class="subtitle">View and filter Skye application logs</p>

        <div class="filters-section">
            <div class="filter-row">
                <div class="filter-group">
                    <label><i class="fas fa-clock"></i> Time Range:</label>
                    <select id="timeFilter" class="filter-select">
                        <option value="1">Last 1 minute</option>
                        <option value="5" selected>Last 5 minutes</option>
                        <option value="15">Last 15 minutes</option>
                        <option value="30">Last 30 minutes</option>
                        <option value="60">Last 1 hour</option>
                        <option value="180">Last 3 hours</option>
                        <option value="360">Last 6 hours</option>
                        <option value="1440">Last 24 hours</option>
                        <option value="all">All logs</option>
                    </select>
                </div>

                <div class="filter-group">
                    <label><i class="fas fa-exclamation-triangle"></i> Log Level:</label>
                    <select id="levelFilter" class="filter-select">
                        <option value="all" selected>All Levels</option>
                        <option value="ERROR">ERROR</option>
                        <option value="WARNING">WARNING</option>
                        <option value="INFO">INFO</option>
                        <option value="DEBUG">DEBUG</option>
                    </select>
                </div>

                <div class="filter-group search-group">
                    <label><i class="fas fa-search"></i> Search:</label>
                    <input type="text" id="searchFilter" class="search-input" placeholder="Search logs...">
                </div>

                <div class="filter-group">
                    <button id="refreshBtn" class="btn-refresh"><i class="fas fa-sync"></i> Refresh</button>
                    <button id="liveWatchBtn" class="btn-live-watch"><i class="fas fa-play"></i> Live Watch</button>
                    <button id="clearBtn" class="btn-clear"><i class="fas fa-trash"></i> Clear Logs</button>
                </div>
            </div>

            <div class="filter-stats">
                <span id="logCount">0 logs</span> |
                <span id="errorCount">0 errors</span> |
                <span id="warningCount">0 warnings</span>
            </div>
        </div>

        <div class="logs-display" id="logsDisplay">
            <div class="loading">Loading logs...</div>
        </div>
    </div>

    <style>
    .logs-container {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    .logs-container h2 {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: #333;
    }

    .subtitle {
        color: #666;
        margin-bottom: 2rem;
    }

    .filters-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }

    .filter-row {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .filter-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .filter-group label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #555;
    }

    .filter-select {
        padding: 0.5rem;
        border: 2px solid #dee2e6;
        border-radius: 6px;
        font-size: 0.95rem;
        background: white;
        cursor: pointer;
        min-width: 150px;
    }

    .filter-select:focus {
        outline: none;
        border-color: #667eea;
    }

    .search-group {
        flex: 1;
        min-width: 250px;
    }

    .search-input {
        padding: 0.5rem;
        border: 2px solid #dee2e6;
        border-radius: 6px;
        font-size: 0.95rem;
        width: 100%;
    }

    .search-input:focus {
        outline: none;
        border-color: #667eea;
    }

    .btn-refresh, .btn-live-watch, .btn-clear {
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 6px;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s;
        margin-top: 1.6rem;
    }

    .btn-refresh {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .btn-refresh:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .btn-live-watch {
        background: #27ae60;
        color: white;
    }

    .btn-live-watch:hover {
        background: #229954;
        transform: translateY(-2px);
    }

    .btn-live-watch.active {
        background: #e67e22;
    }

    .btn-live-watch.active:hover {
        background: #d35400;
    }

    .btn-clear {
        background: #e74c3c;
        color: white;
    }

    .btn-clear:hover {
        background: #c0392b;
        transform: translateY(-2px);
    }

    .filter-stats {
        padding-top: 1rem;
        border-top: 1px solid #dee2e6;
        color: #666;
        font-size: 0.95rem;
    }

    .filter-stats span {
        margin-right: 1rem;
    }

    .logs-display {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 0.75rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        max-height: 700px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        line-height: 1.3;
    }

    .log-entry {
        padding: 0.25rem 0.5rem;
        margin-bottom: 1px;
        border-radius: 2px;
        white-space: pre-wrap;
        word-wrap: break-word;
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
    }

    .log-entry:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    .log-timestamp {
        color: #888;
        flex-shrink: 0;
        font-size: 0.8rem;
    }

    .log-level {
        font-weight: bold;
        padding: 0.1rem 0.4rem;
        border-radius: 3px;
        display: inline-block;
        font-size: 0.75rem;
        min-width: 60px;
        text-align: center;
        flex-shrink: 0;
    }

    .log-level-ERROR {
        background: #e74c3c;
        color: white;
    }

    .log-level-WARNING {
        background: #f39c12;
        color: white;
    }

    .log-level-INFO {
        background: #3498db;
        color: white;
    }

    .log-level-DEBUG {
        background: #95a5a6;
        color: white;
    }

    .log-message {
        color: #e0e0e0;
        flex: 1;
        word-break: break-word;
    }

    .log-message-ERROR {
        color: #ff6b6b;
        font-weight: bold;
    }

    .log-message-WARNING {
        color: #ffd93d;
    }

    .loading {
        text-align: center;
        padding: 2rem;
        color: #888;
    }

    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #888;
    }

    .empty-state i {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    /* Scrollbar styling for logs display */
    .logs-display::-webkit-scrollbar {
        width: 10px;
    }

    .logs-display::-webkit-scrollbar-track {
        background: #2d2d2d;
        border-radius: 10px;
    }

    .logs-display::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }

    .logs-display::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }

    @media (max-width: 768px) {
        .filter-row {
            flex-direction: column;
        }

        .filter-group {
            width: 100%;
        }

        .logs-display {
            font-size: 0.8rem;
            max-height: 400px;
        }
    }
    </style>
    '''

    js_code = '''
    <script>
    let currentLogs = [];
    let autoRefreshInterval = null;
    let isLiveWatchActive = false;

    async function fetchLogs() {
        try {
            const timeFilter = document.getElementById('timeFilter').value;
            const levelFilter = document.getElementById('levelFilter').value;
            const searchFilter = document.getElementById('searchFilter').value;

            const params = new URLSearchParams({
                time: timeFilter,
                level: levelFilter,
                search: searchFilter
            });

            const response = await fetch(`/api/logs?${params}`);
            const data = await response.json();

            if (data.error) {
                console.error('Logs API error:', data.error);
                return;
            }

            currentLogs = data.logs || [];
            displayLogs(currentLogs);
            updateStats(data.stats || {});

        } catch (error) {
            console.error('Failed to fetch logs:', error);
            document.getElementById('logsDisplay').innerHTML =
                '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Failed to load logs</p></div>';
        }
    }

    function displayLogs(logs) {
        const container = document.getElementById('logsDisplay');

        if (!logs || logs.length === 0) {
            container.innerHTML =
                '<div class="empty-state"><i class="fas fa-inbox"></i><p>No logs found</p></div>';
            return;
        }

        // Remember current scroll position
        const wasAtTop = container.scrollTop === 0;

        const html = logs.map(log => {
            const level = log.level || 'INFO';
            const date = new Date(log.timestamp);
            // Compact timestamp format: HH:MM:SS
            const timestamp = date.toLocaleTimeString('en-IE', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            });

            return `
                <div class="log-entry">
                    <span class="log-timestamp">${timestamp}</span>
                    <span class="log-level log-level-${level}">${level}</span>
                    <span class="log-message log-message-${level}">${escapeHtml(log.message)}</span>
                </div>
            `;
        }).join('');

        container.innerHTML = html;

        // Keep at top if user was already at top, otherwise maintain scroll position
        if (wasAtTop) {
            container.scrollTop = 0;
        }
    }

    function updateStats(stats) {
        document.getElementById('logCount').textContent = `${stats.total || 0} logs`;
        document.getElementById('errorCount').textContent = `${stats.errors || 0} errors`;
        document.getElementById('warningCount').textContent = `${stats.warnings || 0} warnings`;
    }

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    async function clearLogs() {
        if (!confirm('Are you sure you want to clear all logs?')) {
            return;
        }

        try {
            const response = await fetch('/api/logs/clear', {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                currentLogs = [];
                displayLogs([]);
                updateStats({ total: 0, errors: 0, warnings: 0 });
            }

        } catch (error) {
            console.error('Failed to clear logs:', error);
            alert('Failed to clear logs');
        }
    }

    function toggleLiveWatch() {
        const btn = document.getElementById('liveWatchBtn');

        if (isLiveWatchActive) {
            // Stop live watch
            stopAutoRefresh();
            isLiveWatchActive = false;
            btn.classList.remove('active');
            btn.innerHTML = '<i class="fas fa-play"></i> Live Watch';
        } else {
            // Start live watch
            startAutoRefresh();
            isLiveWatchActive = true;
            btn.classList.add('active');
            btn.innerHTML = '<i class="fas fa-stop"></i> Stop Watch';
        }
    }

    function startAutoRefresh() {
        // Refresh every 5 seconds
        autoRefreshInterval = setInterval(fetchLogs, 5000);
    }

    function stopAutoRefresh() {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
    }

    // Event listeners
    document.getElementById('timeFilter').addEventListener('change', fetchLogs);
    document.getElementById('levelFilter').addEventListener('change', fetchLogs);
    document.getElementById('searchFilter').addEventListener('input', debounce(fetchLogs, 500));
    document.getElementById('refreshBtn').addEventListener('click', fetchLogs);
    document.getElementById('liveWatchBtn').addEventListener('click', toggleLiveWatch);
    document.getElementById('clearBtn').addEventListener('click', clearLogs);

    // Debounce function for search input
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Initial load only (user must click Live Watch to enable auto-refresh)
    setTimeout(() => {
        fetchLogs();
    }, 100);
    </script>
    '''

    return {
        'html': html_content + js_code
    }
