class SkyeApp {
    constructor() {
        this.currentPage = null;
        this.tabStates = new Map(); // Store tab content and state
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        // Tab button clicks
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const pageId = e.currentTarget.dataset.page;
                this.loadPage(pageId);
            });
        });

        // Page card clicks
        document.querySelectorAll('.page-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const pageId = e.currentTarget.dataset.page;
                this.loadPage(pageId);
            });
        });

        // Restart button click
        const restartBtn = document.getElementById('restartBtn');
        if (restartBtn) {
            restartBtn.addEventListener('click', () => this.restartServer());
        }
    }

    async restartServer() {
        const btn = document.getElementById('restartBtn');
        const originalHTML = btn.innerHTML;
        
        try {
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            btn.disabled = true;
            
            await fetch('/api/restart', { method: 'POST' });
            
            // Wait a moment then reload the page
            setTimeout(() => {
                window.location.reload();
            }, 2000);
            
        } catch (error) {
            btn.innerHTML = originalHTML;
            btn.disabled = false;
            alert('Restart failed: ' + error.message);
        }
    }

    async loadPage(pageId) {
        if (this.currentPage === pageId) return;

        const content = document.getElementById('page-content');
        
        // Save current tab state before switching
        if (this.currentPage) {
            this.saveTabState(this.currentPage, content.innerHTML);
        }

        // Update active tab
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.page === pageId);
        });

        // Check if we have saved state for this tab
        if (this.tabStates.has(pageId)) {
            content.innerHTML = this.tabStates.get(pageId);
            this.currentPage = pageId;
            this.executeScripts(content);
            return;
        }

        // Show loading for new tab
        content.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';

        try {
            const response = await fetch(`/page/${pageId}`);
            const data = await response.json();

            if (response.ok) {
                const pageContent = data.html || '<p>No content available</p>';
                content.innerHTML = pageContent;
                this.currentPage = pageId;
                
                // Save initial state
                this.saveTabState(pageId, pageContent);
                
                // Execute any scripts in the loaded content
                this.executeScripts(content);
            } else {
                content.innerHTML = `<div class="error">Error: ${data.error}</div>`;
            }
        } catch (error) {
            content.innerHTML = `<div class="error">Failed to load page: ${error.message}</div>`;
        }
    }

    saveTabState(pageId, content) {
        this.tabStates.set(pageId, content);
    }

    executeScripts(container) {
        const scripts = container.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            if (script.src) {
                newScript.src = script.src;
            } else {
                newScript.textContent = script.textContent;
            }
            document.head.appendChild(newScript);
        });
    }
}

// Global function for switching tabs (used by home page)
function switchTab(pageId) {
    if (window.skyeApp) {
        window.skyeApp.loadPage(pageId);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.skyeApp = new SkyeApp();
    // Load home tab by default
    window.skyeApp.loadPage('home');
});