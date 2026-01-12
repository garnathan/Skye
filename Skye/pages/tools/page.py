def get_content():
    """Return the HTML content for the tools page"""
    import os
    
    # Read the modal HTML
    modal_path = os.path.join(os.path.dirname(__file__), 'playlist_copier.html')
    modal_html = ''
    if os.path.exists(modal_path):
        with open(modal_path, 'r') as f:
            modal_html = f.read()
    
    html_content = '''
        <div class="tools-page">
            <h2><i class="fas fa-tools"></i> Misc Tools</h2>
            
            <div class="tools-grid">
                <div class="tool-card">
                    <i class="fas fa-car"></i>
                    <h3>Ireland VRT Calculator</h3>
                    <p>Calculate Vehicle Registration Tax for importing cars to Ireland</p>
                    <a href="/vrt-calculator" target="_blank" class="tool-button">Open Tool</a>
                </div>
                
                <div class="tool-card">
                    <i class="fab fa-youtube"></i>
                    <h3>YouTube Playlist Copier</h3>
                    <p>Copy playlists between YouTube accounts</p>
                    <button class="tool-button" onclick="document.getElementById('playlistModal').style.display='block'">Open Tool</button>
                </div>
                
                <div class="tool-card">
                    <i class="fas fa-music"></i>
                    <h3>YouTube Music Downloader</h3>
                    <p>Download audio from YouTube videos as MP3 files</p>
                    <button class="tool-button" onclick="document.getElementById('musicDownloaderModal').style.display='block'">Open Tool</button>
                </div>
            </div>
            
            ''' + modal_html + '''
            
            <!-- YouTube Music Downloader Modal -->
            <div id="musicDownloaderModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3><i class="fas fa-music"></i> YouTube Music Downloader</h3>
                        <span class="close" onclick="document.getElementById('musicDownloaderModal').style.display='none'">&times;</span>
                    </div>
                    <div class="modal-body">
                        <div class="step">
                            <h4>Download Audio from YouTube</h4>
                            <label for="youtubeUrl">YouTube Video URL:</label>
                            <input type="text" id="youtubeUrl" placeholder="https://www.youtube.com/watch?v=..." />
                            
                            <label for="saveLocation">Save Location:</label>
                            <div style="display: flex; gap: 0.5rem; align-items: stretch;">
                                <input type="text" id="saveLocation" placeholder="Choose where to save the file..." readonly style="flex: 1; margin-bottom: 0;" />
                                <button onclick="chooseSaveLocation()" style="background: #28a745; margin: 0; padding: 0.5rem 1rem; white-space: nowrap;">Browse</button>
                            </div>
                            
                            <div style="margin-top: 1rem;">
                                <button onclick="downloadAudio()" id="downloadBtn" style="background: #667eea; font-size: 1rem; padding: 0.75rem 1.5rem;">Download MP3</button>
                            </div>
                            
                            <div id="downloadProgress" class="progress hidden">
                                <div class="progress-bar"></div>
                                <div id="progressText">Downloading...</div>
                            </div>
                            
                            <div id="downloadResult" class="hidden" style="margin-top: 1rem; padding: 1rem; border-radius: 4px;"></div>
                        </div>
                    </div>
                </div>
            </div>
            

        </div>
        
        <style>

        
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .tool-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.2s;
        }
        
        .tool-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .tool-card i {
            font-size: 2rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .tool-button {
            display: inline-block;
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 1rem;
            text-decoration: none;
            font-size: 14px;
            font-family: inherit;
        }
        
        .tool-button:hover {
            background: #5a6fd8;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            border-radius: 8px;
            width: 80%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            padding: 1rem;
            border-bottom: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .close {
            font-size: 1.5rem;
            cursor: pointer;
            color: #999;
        }
        
        .close:hover {
            color: #333;
        }
        
        .modal-body {
            padding: 1rem;
        }
        
        .step {
            margin-bottom: 2rem;
        }
        
        .step.hidden {
            display: none;
        }
        
        .step h4 {
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .step label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: bold;
        }
        
        .step input[type="text"] {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        
        .step button {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .step button:hover {
            background: #5a6fd8;
        }
        
        .playlist-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .back-btn {
            background: #6c757d !important;
            margin-right: auto;
        }
        
        .back-btn:hover {
            background: #5a6268 !important;
        }
        
        .selection-controls {
            display: flex;
            gap: 0.5rem;
        }
        
        .selection-controls button {
            background: #28a745;
        }
        
        .playlist-list {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .playlist-item {
            display: flex;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .playlist-item:last-child {
            border-bottom: none;
        }
        
        .playlist-item input[type="checkbox"] {
            margin-right: 0.5rem;
        }
        
        .playlist-info {
            flex: 1;
        }
        
        .playlist-title {
            font-weight: bold;
            margin-bottom: 0.25rem;
        }
        
        .playlist-meta {
            font-size: 0.8rem;
            color: #666;
        }
        
        .auth-section {
            margin-bottom: 1.5rem;
        }
        
        .auth-account {
            margin-bottom: 1rem;
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #f8f9fa;
        }
        
        .auth-account h5 {
            margin: 0 0 0.5rem 0;
            color: #333;
        }
        
        .copy-options {
            margin: 1rem 0;
        }
        
        .copy-options label {
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
            font-weight: normal;
        }
        
        .copy-options input[type="checkbox"] {
            margin-right: 0.5rem;
        }
        
        .next-btn, .copy-btn {
            background: #28a745 !important;
            font-size: 1rem;
            padding: 0.75rem 1.5rem;
        }
        
        .progress {
            margin-top: 1rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 4px;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }
        
        .progress-bar::after {
            content: '';
            display: block;
            height: 100%;
            background: #28a745;
            width: 0%;
            transition: width 0.3s;
            animation: progress 2s infinite;
        }
        
        @keyframes progress {
            0% { width: 0%; }
            50% { width: 50%; }
            100% { width: 100%; }
        }
        
        .loading, .hidden {
            display: none;
        }
        
        .loading {
            color: #667eea;
            font-style: italic;
            margin-top: 0.5rem;
        }
        
        .error-notice {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 0.75rem;
            margin-bottom: 1rem;
            color: #721c24;
        }
        

        </style>
        
        <script>
        let selectedPlaylists = [];
        
        async function loadPlaylists() {
            const sourceChannel = document.getElementById('sourceChannel').value.trim();
            if (!sourceChannel) {
                alert('Please enter a source channel name or handle');
                return;
            }
            
            document.getElementById('loadBtn').disabled = true;
            document.getElementById('loadingMsg').classList.remove('hidden');
            
            try {
                const response = await fetch('/api/youtube/playlists?channel=' + encodeURIComponent(sourceChannel));
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to load playlists');
                }
                
                const listContainer = document.getElementById('playlistList');
                listContainer.innerHTML = '';
                
                if (data.playlists.length === 0) {
                    listContainer.innerHTML = '<div class="error-notice">No public playlists found for "' + data.channelName + '". The channel may not have any public playlists or may not exist.</div>';
                } else {
                    data.playlists.forEach(playlist => {
                        const item = document.createElement('div');
                        item.className = 'playlist-item';
                        
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.id = 'playlist_' + playlist.id;
                        checkbox.value = playlist.id;
                        checkbox.onchange = function() {
                            selectedPlaylists = Array.from(document.querySelectorAll('#playlistList input[type="checkbox"]:checked')).map(cb => cb.value);
                        };
                        
                        const playlistInfo = document.createElement('div');
                        playlistInfo.className = 'playlist-info';
                        playlistInfo.innerHTML = '<div class="playlist-title">' + playlist.title + '</div><div class="playlist-meta">' + playlist.videoCount + ' videos • ' + playlist.privacy + ' • ' + (playlist.description || 'No description') + '</div>';
                        
                        item.appendChild(checkbox);
                        item.appendChild(playlistInfo);
                        listContainer.appendChild(item);
                    });
                }
                
                document.getElementById('step1').classList.add('hidden');
                document.getElementById('step2').classList.remove('hidden');
            } catch (error) {
                const listContainer = document.getElementById('playlistList');
                listContainer.innerHTML = '<div class="error-notice"><strong>Error:</strong> ' + error.message + '<br><br><strong>Note:</strong> This tool requires a YouTube Data API key to be configured.</div>';
                document.getElementById('step1').classList.add('hidden');
                document.getElementById('step2').classList.remove('hidden');
            } finally {
                document.getElementById('loadBtn').disabled = false;
                document.getElementById('loadingMsg').classList.add('hidden');
            }
        }
        
        function goBackToStep1() {
            document.getElementById('step2').classList.add('hidden');
            document.getElementById('step1').classList.remove('hidden');
        }
        
        function selectAll() {
            document.querySelectorAll('#playlistList input[type="checkbox"]').forEach(cb => {
                cb.checked = true;
            });
            selectedPlaylists = Array.from(document.querySelectorAll('#playlistList input[type="checkbox"]:checked')).map(cb => cb.value);
        }
        
        function selectNone() {
            document.querySelectorAll('#playlistList input[type="checkbox"]').forEach(cb => {
                cb.checked = false;
            });
            selectedPlaylists = [];
        }
        
        function showStep3() {
            if (selectedPlaylists.length === 0) {
                alert('Please select at least one playlist to copy');
                return;
            }
            document.getElementById('step2').classList.add('hidden');
            document.getElementById('step3').classList.remove('hidden');
        }
        
        async function authorizeYouTube(accountType) {
            alert('OAuth authentication coming soon. For now, this tool can only browse playlists.');
        }
        
        async function copyPlaylists() {
            alert('Playlist copying requires OAuth authentication which is not yet implemented. For now, you can browse and view playlists.');
        }
        
        let selectedSavePath = '';
        
        async function chooseSaveLocation() {
            try {
                // Use the File System Access API if available (Chrome/Edge)
                if ('showSaveFilePicker' in window) {
                    const fileHandle = await window.showSaveFilePicker({
                        suggestedName: 'audio.mp3',
                        types: [{
                            description: 'MP3 files',
                            accept: {
                                'audio/mpeg': ['.mp3']
                            }
                        }]
                    });
                    selectedSavePath = fileHandle.name;
                    document.getElementById('saveLocation').value = selectedSavePath;
                } else {
                    // Fallback for browsers that don't support File System Access API
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.webkitdirectory = false;
                    input.accept = '.mp3';
                    input.onchange = function(e) {
                        if (e.target.files.length > 0) {
                            selectedSavePath = e.target.files[0].name;
                            document.getElementById('saveLocation').value = selectedSavePath;
                        }
                    };
                    input.click();
                }
            } catch (error) {
                // User cancelled or error occurred
                console.log('File selection cancelled or failed:', error);
            }
        }
        
        async function downloadAudio() {
            const url = document.getElementById('youtubeUrl').value.trim();
            const savePath = document.getElementById('saveLocation').value.trim();
            
            if (!url) {
                alert('Please enter a YouTube URL');
                return;
            }
            
            if (!savePath) {
                alert('Please choose a save location');
                return;
            }
            
            // Validate YouTube URL
            const youtubeRegex = /^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
            if (!youtubeRegex.test(url)) {
                alert('Please enter a valid YouTube URL');
                return;
            }
            
            const downloadBtn = document.getElementById('downloadBtn');
            const progressDiv = document.getElementById('downloadProgress');
            const resultDiv = document.getElementById('downloadResult');
            
            downloadBtn.disabled = true;
            downloadBtn.textContent = 'Downloading...';
            progressDiv.classList.remove('hidden');
            resultDiv.classList.add('hidden');
            
            try {
                const response = await fetch('/api/youtube/download-audio', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url: url,
                        savePath: savePath
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.innerHTML = '<div style="background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 0.75rem; border-radius: 4px;"><strong>Success!</strong> Audio downloaded successfully as: ' + data.filename + '</div>';
                    resultDiv.classList.remove('hidden');
                    
                    // If we have the file data, trigger download
                    if (data.fileData) {
                        const blob = new Blob([Uint8Array.from(atob(data.fileData), c => c.charCodeAt(0))], { type: 'audio/mpeg' });
                        const downloadUrl = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = downloadUrl;
                        a.download = data.filename;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(downloadUrl);
                    }
                } else {
                    resultDiv.innerHTML = '<div style="background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 0.75rem; border-radius: 4px;"><strong>Error:</strong> ' + (data.error || 'Download failed') + '</div>';
                    resultDiv.classList.remove('hidden');
                }
            } catch (error) {
                resultDiv.innerHTML = '<div style="background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 0.75rem; border-radius: 4px;"><strong>Error:</strong> ' + error.message + '</div>';
                resultDiv.classList.remove('hidden');
            } finally {
                downloadBtn.disabled = false;
                downloadBtn.textContent = 'Download MP3';
                progressDiv.classList.add('hidden');
            }
        }
        
        window.onclick = function(event) {
            const playlistModal = document.getElementById('playlistModal');
            const musicModal = document.getElementById('musicDownloaderModal');
            if (event.target === playlistModal) {
                playlistModal.style.display = 'none';
            }
            if (event.target === musicModal) {
                musicModal.style.display = 'none';
            }
        }
        </script>
    '''
    
    return {'html': html_content}