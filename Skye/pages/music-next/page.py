def get_content():
    """Return the HTML content for the Music Next page"""

    html_content = '''
    <div class="music-next-container">
        <h2><i class="fas fa-music"></i> Music Next</h2>
        <p class="subtitle">Discover similar artists based on your favorite bands</p>

        <div class="search-section">
            <div class="search-box">
                <input type="text" id="artistSearch" placeholder="Enter an artist or band name..." />
                <button id="searchBtn"><i class="fas fa-search"></i> Search</button>
            </div>
        </div>

        <div class="recommendation-section" id="recommendationSection" style="display: none;">
            <div class="current-artist">
                <h3>Based on: <span id="currentArtist"></span></h3>
            </div>

            <div class="recommendation-card">
                <div class="recommendation-header">
                    <h4>Try listening to:</h4>
                    <div class="recommendation-counter" id="recommendationCounter"></div>
                </div>
                <div class="artist-image-container" id="artistImageContainer">
                    <img id="artistImage" src="" alt="" style="display: none;">
                    <div class="image-placeholder" id="imagePlaceholder">
                        <i class="fas fa-music"></i>
                    </div>
                </div>
                <div class="artist-name" id="recommendedArtist">Loading...</div>
                <div class="action-buttons">
                    <button id="listenedBtn" class="btn-listened"><i class="fas fa-check"></i> Listened</button>
                    <button id="skipBtn" class="btn-skip"><i class="fas fa-forward"></i> Skip</button>
                    <button id="backBtn" class="btn-back"><i class="fas fa-backward"></i> Back</button>
                    <button id="newSearchBtn" class="btn-new-search"><i class="fas fa-sync"></i> New Search</button>
                    <button id="listenBtn" class="btn-listen"><i class="fas fa-play"></i> Listen</button>
                </div>
            </div>

            <div class="completion-message" id="completionMessage" style="display: none;">
                <i class="fas fa-check-circle"></i>
                <p>You've explored all recommendations for this artist!</p>
                <button id="refreshBtn" class="btn-refresh"><i class="fas fa-redo"></i> Check for Updates</button>
            </div>
        </div>

        <div class="history-section">
            <h3><i class="fas fa-history"></i> Search History</h3>
            <div id="searchHistory" class="search-history-list">
                <p class="empty-state">No searches yet</p>
            </div>
        </div>
    </div>

    <style>
    .music-next-container {
        padding: 2rem;
        max-width: 900px;
        margin: 0 auto;
    }

    .music-next-container h2 {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: #333;
    }

    .subtitle {
        color: #666;
        margin-bottom: 2rem;
    }

    .search-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }

    .search-box {
        display: flex;
        gap: 1rem;
    }

    #artistSearch {
        flex: 1;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        transition: border-color 0.3s;
    }

    #artistSearch:focus {
        outline: none;
        border-color: #667eea;
    }

    #searchBtn {
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: transform 0.2s;
    }

    #searchBtn:hover {
        transform: translateY(-2px);
    }

    .recommendation-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }

    .current-artist {
        margin-bottom: 1.5rem;
    }

    .current-artist h3 {
        color: #666;
        font-size: 1rem;
        font-weight: normal;
    }

    .current-artist span {
        color: #667eea;
        font-weight: bold;
        font-size: 1.1rem;
    }

    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }

    .recommendation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .recommendation-header h4 {
        margin: 0;
        font-size: 1rem;
        opacity: 0.9;
    }

    .recommendation-counter {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }

    .artist-image-container {
        width: 250px;
        height: 250px;
        margin: 1.5rem auto;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        position: relative;
    }

    #artistImage {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .image-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.1);
        font-size: 4rem;
        color: rgba(255, 255, 255, 0.5);
    }

    .artist-name {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 1.5rem 0;
        min-height: 3rem;
    }

    .action-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 2rem;
    }

    .action-buttons button {
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        border: 2px solid white;
        background: transparent;
        color: white;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
    }

    .action-buttons button:hover {
        background: white;
        color: #667eea;
    }

    .completion-message {
        text-align: center;
        padding: 2rem;
        background: #f8f9fa;
        border-radius: 12px;
    }

    .completion-message i {
        font-size: 3rem;
        color: #4CAF50;
        margin-bottom: 1rem;
    }

    .btn-refresh {
        margin-top: 1rem;
        padding: 0.75rem 1.5rem;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
    }

    .history-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .history-section h3 {
        margin-bottom: 1rem;
        color: #333;
    }

    .search-history-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .history-item {
        padding: 0.5rem 1rem;
        background: #f8f9fa;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s;
        border: 2px solid transparent;
    }

    .history-item:hover {
        background: #667eea;
        color: white;
    }

    .empty-state {
        color: #999;
        font-style: italic;
    }
    </style>
    '''

    js_code = '''
    <script>
    let currentState = null;

    async function searchArtist(artistName) {
        try {
            document.getElementById('artistSearch').disabled = true;
            document.getElementById('searchBtn').disabled = true;

            const response = await fetch(`/api/music-next/search?artist=${encodeURIComponent(artistName)}`);
            const data = await response.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            currentState = data;
            displayRecommendation();
            loadSearchHistory();

        } catch (error) {
            console.error('Search failed:', error);
            alert('Failed to search for artist');
        } finally {
            document.getElementById('artistSearch').disabled = false;
            document.getElementById('searchBtn').disabled = false;
        }
    }

    async function loadArtistImage(artistName) {
        const artistImage = document.getElementById('artistImage');
        const imagePlaceholder = document.getElementById('imagePlaceholder');

        try {
            const response = await fetch(`/api/music-next/artist-image?artist=${encodeURIComponent(artistName)}`);
            const data = await response.json();

            if (data.image_url) {
                artistImage.src = data.image_url;
                artistImage.alt = artistName;
                artistImage.style.display = 'block';
                imagePlaceholder.style.display = 'none';
            } else {
                artistImage.style.display = 'none';
                imagePlaceholder.style.display = 'flex';
            }
        } catch (error) {
            console.error('Failed to load artist image:', error);
            artistImage.style.display = 'none';
            imagePlaceholder.style.display = 'flex';
        }
    }

    function displayRecommendation() {
        const recSection = document.getElementById('recommendationSection');
        const completionMsg = document.getElementById('completionMessage');
        const recCard = document.querySelector('.recommendation-card');

        if (!currentState || !currentState.current_recommendation) {
            recSection.style.display = 'block';
            recCard.style.display = 'none';
            completionMsg.style.display = 'block';
            document.getElementById('currentArtist').textContent = currentState?.search_artist || '';
            return;
        }

        recSection.style.display = 'block';
        recCard.style.display = 'block';
        completionMsg.style.display = 'none';

        document.getElementById('currentArtist').textContent = currentState.search_artist;
        document.getElementById('recommendedArtist').textContent = currentState.current_recommendation;
        document.getElementById('recommendationCounter').textContent =
            `${currentState.listened_count + 1} / ${currentState.total_count}`;

        // Load artist image
        loadArtistImage(currentState.current_recommendation);

        // Enable/disable back button based on history position
        const backBtn = document.getElementById('backBtn');
        const currentIndex = currentState.current_index || 0;
        if (currentIndex > 0) {
            backBtn.disabled = false;
            backBtn.style.opacity = '1';
            backBtn.style.cursor = 'pointer';
        } else {
            backBtn.disabled = true;
            backBtn.style.opacity = '0.5';
            backBtn.style.cursor = 'not-allowed';
        }
    }

    async function markAsListened() {
        try {
            const response = await fetch('/api/music-next/listened', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    artist: currentState.search_artist,
                    recommended: currentState.current_recommendation
                })
            });

            const data = await response.json();
            currentState = data;
            displayRecommendation();

        } catch (error) {
            console.error('Failed to mark as listened:', error);
            alert('Failed to update recommendation');
        }
    }

    async function skipRecommendation() {
        try {
            const response = await fetch('/api/music-next/skip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    artist: currentState.search_artist,
                    recommended: currentState.current_recommendation
                })
            });

            const data = await response.json();
            currentState = data;
            displayRecommendation();

        } catch (error) {
            console.error('Failed to skip recommendation:', error);
            alert('Failed to skip recommendation');
        }
    }

    async function goBack() {
        try {
            const response = await fetch('/api/music-next/back', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    artist: currentState.search_artist
                })
            });

            const data = await response.json();
            if (data.error) {
                alert(data.error);
                return;
            }
            currentState = data;
            displayRecommendation();

        } catch (error) {
            console.error('Failed to go back:', error);
            alert('Failed to go back');
        }
    }

    async function refreshRecommendations() {
        await searchArtist(currentState.search_artist);
    }

    async function loadSearchHistory() {
        try {
            const response = await fetch('/api/music-next/history');
            const data = await response.json();

            const historyDiv = document.getElementById('searchHistory');

            if (data.history && data.history.length > 0) {
                historyDiv.innerHTML = data.history.map(artist =>
                    `<div class="history-item" onclick="searchArtist('${artist.replace(/'/g, "\\'")}')">
                        ${artist}
                    </div>`
                ).join('');
            } else {
                historyDiv.innerHTML = '<p class="empty-state">No searches yet</p>';
            }

        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }

    async function loadCurrentState() {
        try {
            const response = await fetch('/api/music-next/current');
            const data = await response.json();

            if (data.search_artist) {
                currentState = data;
                displayRecommendation();
            }

        } catch (error) {
            console.error('Failed to load current state:', error);
        }
    }

    document.getElementById('searchBtn').addEventListener('click', () => {
        const artist = document.getElementById('artistSearch').value.trim();
        if (artist) {
            searchArtist(artist);
        }
    });

    document.getElementById('artistSearch').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const artist = e.target.value.trim();
            if (artist) {
                searchArtist(artist);
            }
        }
    });

    document.getElementById('listenedBtn').addEventListener('click', markAsListened);
    document.getElementById('skipBtn').addEventListener('click', skipRecommendation);
    document.getElementById('backBtn').addEventListener('click', goBack);
    document.getElementById('newSearchBtn').addEventListener('click', () => {
        document.getElementById('recommendationSection').style.display = 'none';
        document.getElementById('artistSearch').value = '';
        document.getElementById('artistSearch').focus();
    });
    document.getElementById('listenBtn').addEventListener('click', () => {
        if (currentState && currentState.current_recommendation) {
            const searchQuery = encodeURIComponent(currentState.current_recommendation);
            window.open(`https://www.youtube.com/results?search_query=${searchQuery}`, '_blank');
        }
    });

    document.getElementById('refreshBtn').addEventListener('click', refreshRecommendations);

    setTimeout(() => {
        loadCurrentState();
        loadSearchHistory();
    }, 100);
    </script>
    '''

    return {
        'html': html_content + js_code
    }
