// =============================================================================
// PROGRESS BAR
// =============================================================================

class ProgressBar {
    constructor() {
        this.container = null;
        this.bar = null;
        this.init();
    }

    init() {
        this.container = document.createElement('div');
        this.container.className = 'progress-bar-container';
        this.bar = document.createElement('div');
        this.bar.className = 'progress-bar';
        this.container.appendChild(this.bar);
        document.body.appendChild(this.container);
    }

    start() {
        this.bar.style.width = '0%';
        this.bar.classList.add('indeterminate');
    }

    set(percent) {
        this.bar.classList.remove('indeterminate');
        this.bar.style.width = `${Math.min(100, percent)}%`;
    }

    done() {
        this.bar.classList.remove('indeterminate');
        this.bar.style.width = '100%';
        setTimeout(() => {
            this.bar.style.width = '0%';
        }, 300);
    }
}

// =============================================================================
// PULL TO REFRESH (Mobile)
// =============================================================================

class PullToRefresh {
    constructor(app) {
        this.app = app;
        this.element = null;
        this.startY = 0;
        this.currentY = 0;
        this.pulling = false;
        this.threshold = 80;
        this.init();
    }

    init() {
        // Only enable on touch devices
        if (!('ontouchstart' in window)) return;

        this.element = document.createElement('div');
        this.element.className = 'pull-to-refresh';
        this.element.innerHTML = '<i class="fas fa-arrow-down"></i> <span>Pull to refresh</span>';
        document.body.appendChild(this.element);

        document.addEventListener('touchstart', (e) => this.onTouchStart(e), { passive: true });
        document.addEventListener('touchmove', (e) => this.onTouchMove(e), { passive: false });
        document.addEventListener('touchend', (e) => this.onTouchEnd(e), { passive: true });
    }

    onTouchStart(e) {
        if (window.scrollY === 0) {
            this.startY = e.touches[0].pageY;
            this.pulling = true;
        }
    }

    onTouchMove(e) {
        if (!this.pulling) return;

        this.currentY = e.touches[0].pageY;
        const pullDistance = this.currentY - this.startY;

        if (pullDistance > 0 && window.scrollY === 0) {
            e.preventDefault();
            const progress = Math.min(pullDistance / this.threshold, 1);
            this.element.style.setProperty('--pull-progress', progress);
            this.element.classList.add('pulling');

            if (progress >= 1) {
                this.element.classList.add('ready');
                this.element.querySelector('span').textContent = 'Release to refresh';
            } else {
                this.element.classList.remove('ready');
                this.element.querySelector('span').textContent = 'Pull to refresh';
            }
        }
    }

    onTouchEnd() {
        if (!this.pulling) return;

        const pullDistance = this.currentY - this.startY;

        if (pullDistance >= this.threshold) {
            this.refresh();
        } else {
            this.reset();
        }

        this.pulling = false;
    }

    refresh() {
        this.element.classList.remove('pulling', 'ready');
        this.element.classList.add('visible', 'refreshing');
        this.element.querySelector('i').className = 'fas fa-spinner';
        this.element.querySelector('span').textContent = 'Refreshing...';

        // Reload current page
        if (this.app) {
            this.app.reloadCurrentPage();
        }

        setTimeout(() => this.reset(), 1000);
    }

    reset() {
        this.element.classList.remove('pulling', 'ready', 'visible', 'refreshing');
        this.element.style.setProperty('--pull-progress', 0);
        this.element.querySelector('i').className = 'fas fa-arrow-down';
        this.element.querySelector('span').textContent = 'Pull to refresh';
    }
}

// =============================================================================
// TOAST NOTIFICATION SYSTEM
// =============================================================================

class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }

    show(type, title, message, duration = 4000) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="toast-icon ${icons[type] || icons.info}"></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">&times;</button>
        `;

        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.hide(toast));

        this.container.appendChild(toast);

        if (duration > 0) {
            setTimeout(() => this.hide(toast), duration);
        }

        return toast;
    }

    hide(toast) {
        toast.classList.add('toast-hiding');
        setTimeout(() => toast.remove(), 300);
    }

    success(title, message) { return this.show('success', title, message); }
    error(title, message) { return this.show('error', title, message, 6000); }
    warning(title, message) { return this.show('warning', title, message); }
    info(title, message) { return this.show('info', title, message); }
}

// =============================================================================
// THEME MANAGER (Dark Mode)
// =============================================================================

class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('skye-theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.theme);
    }

    toggle() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.theme);
        localStorage.setItem('skye-theme', this.theme);
        return this.theme;
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const icon = document.querySelector('.theme-toggle i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    isDark() {
        return this.theme === 'dark';
    }
}

// =============================================================================
// KEYBOARD SHORTCUTS
// =============================================================================

class KeyboardShortcuts {
    constructor(app) {
        this.app = app;
        this.hintElement = null;
        this.hintTimeout = null;
        this.init();
    }

    init() {
        this.createHintElement();
        document.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    createHintElement() {
        this.hintElement = document.createElement('div');
        this.hintElement.className = 'shortcut-hint';
        this.hintElement.innerHTML = `
            <kbd>1-9</kbd> Switch tabs &nbsp;|&nbsp;
            <kbd>D</kbd> Dark mode &nbsp;|&nbsp;
            <kbd>R</kbd> Refresh &nbsp;|&nbsp;
            <kbd>H</kbd> About &nbsp;|&nbsp;
            <kbd>?</kbd> Help
        `;
        document.body.appendChild(this.hintElement);
    }

    handleKeydown(e) {
        // Ignore if typing in input/textarea
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        // Number keys 1-9 for tab switching
        if (e.key >= '1' && e.key <= '9') {
            const tabs = document.querySelectorAll('.tab-button');
            const index = parseInt(e.key) - 1;
            if (tabs[index]) {
                tabs[index].click();
                window.toast?.info('Tab switched', `Switched to ${tabs[index].textContent.trim()}`);
            }
            return;
        }

        switch (e.key.toLowerCase()) {
            case 'd':
                if (!e.ctrlKey && !e.metaKey) {
                    const newTheme = window.themeManager?.toggle();
                    window.toast?.info('Theme changed', `Switched to ${newTheme} mode`);
                }
                break;
            case 'r':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    window.skyeApp?.reloadCurrentPage();
                    window.toast?.info('Refreshing', 'Reloading current page...');
                }
                break;
            case 'h':
                if (!e.ctrlKey && !e.metaKey) {
                    window.helpModal?.show();
                }
                break;
            case 'escape':
                window.helpModal?.hide();
                break;
            case '?':
                this.showHint();
                break;
        }
    }

    showHint() {
        this.hintElement.classList.add('visible');
        clearTimeout(this.hintTimeout);
        this.hintTimeout = setTimeout(() => {
            this.hintElement.classList.remove('visible');
        }, 3000);
    }
}

// =============================================================================
// SKELETON LOADER HELPERS
// =============================================================================

const Skeleton = {
    chart: () => `<div class="skeleton skeleton-chart"></div>`,
    price: () => `<div class="skeleton skeleton-price"></div>`,
    text: (width = '100%') => `<div class="skeleton skeleton-text" style="width: ${width}"></div>`,
    title: () => `<div class="skeleton skeleton-title"></div>`
};

// =============================================================================
// ERROR STATE WITH RETRY
// =============================================================================

function createErrorState(message, retryFn, retryable = true) {
    const retryButton = retryable ? `
        <button class="retry-btn" onclick="(${retryFn.toString()})()">
            <i class="fas fa-redo"></i> Try Again
        </button>
    ` : '';

    return `
        <div class="error-state">
            <div class="error-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="error-state-title">Failed to load data</div>
            <div class="error-state-message">${message}</div>
            ${retryButton}
        </div>
    `;
}

// =============================================================================
// API CLIENT WITH RETRY LOGIC
// =============================================================================

class APIClient {
    constructor() {
        this.defaultTimeout = 30000; // 30 seconds
        this.maxRetries = 3;
        this.retryDelay = 1000; // Start with 1 second
    }

    async fetch(url, options = {}) {
        const timeout = options.timeout || this.defaultTimeout;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timed out');
            }
            throw error;
        }
    }

    async fetchWithRetry(url, options = {}) {
        const maxRetries = options.maxRetries || this.maxRetries;
        let lastError;

        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                const response = await this.fetch(url, options);

                // Check if response indicates a retryable error
                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    if (data.retryable && attempt < maxRetries - 1) {
                        const delay = this.retryDelay * Math.pow(2, attempt);
                        await new Promise(resolve => setTimeout(resolve, delay));
                        continue;
                    }
                    throw new Error(data.error || `HTTP ${response.status}`);
                }

                return response;
            } catch (error) {
                lastError = error;
                if (attempt < maxRetries - 1) {
                    const delay = this.retryDelay * Math.pow(2, attempt);
                    console.log(`Retry ${attempt + 1}/${maxRetries} after ${delay}ms: ${error.message}`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }

        throw lastError;
    }

    async fetchJSON(url, options = {}) {
        const response = await this.fetchWithRetry(url, options);
        return response.json();
    }
}

// =============================================================================
// AUTO-REFRESH MANAGER
// =============================================================================

class AutoRefreshManager {
    constructor() {
        this.intervals = new Map();
        this.callbacks = new Map();
        this.paused = false;
    }

    register(id, callback, intervalMs) {
        this.callbacks.set(id, callback);
        this.start(id, intervalMs);
    }

    start(id, intervalMs) {
        this.stop(id); // Clear any existing interval
        const interval = setInterval(() => {
            if (!this.paused && document.visibilityState === 'visible') {
                const callback = this.callbacks.get(id);
                if (callback) callback();
            }
        }, intervalMs);
        this.intervals.set(id, interval);
    }

    stop(id) {
        const interval = this.intervals.get(id);
        if (interval) {
            clearInterval(interval);
            this.intervals.delete(id);
        }
    }

    stopAll() {
        this.intervals.forEach((_, id) => this.stop(id));
    }

    pause() {
        this.paused = true;
    }

    resume() {
        this.paused = false;
    }

    // Refresh a specific item immediately
    refresh(id) {
        const callback = this.callbacks.get(id);
        if (callback) callback();
    }
}

// =============================================================================
// TAB STATE PERSISTENCE
// =============================================================================

class TabPersistence {
    constructor() {
        this.storageKey = 'skye-last-tab';
    }

    save(tabId) {
        try {
            localStorage.setItem(this.storageKey, tabId);
        } catch (e) {
            // localStorage may be unavailable
        }
    }

    load() {
        try {
            return localStorage.getItem(this.storageKey);
        } catch (e) {
            return null;
        }
    }
}

// =============================================================================
// MAIN APPLICATION
// =============================================================================

class SkyeApp {
    constructor() {
        this.currentPage = null;
        this.tabStates = new Map();
        this.loadedScripts = new Set();
        this.noCachePages = new Set(['dashboard']);
        this.tabPersistence = new TabPersistence();
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const pageId = e.currentTarget.dataset.page;
                this.loadPage(pageId);
            });
        });

        document.querySelectorAll('.page-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const pageId = e.currentTarget.dataset.page;
                this.loadPage(pageId);
            });
        });

        const restartBtn = document.getElementById('restartBtn');
        if (restartBtn) {
            restartBtn.addEventListener('click', () => this.restartServer());
        }

        const themeBtn = document.getElementById('themeToggle');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => {
                const newTheme = window.themeManager?.toggle();
                window.toast?.info('Theme changed', `Switched to ${newTheme} mode`);
            });
        }
    }

    async restartServer() {
        const btn = document.getElementById('restartBtn');
        const originalHTML = btn.innerHTML;

        try {
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            btn.disabled = true;

            await fetch('/api/restart', { method: 'POST' });
            window.toast?.success('Restarting', 'Server is restarting...');

            setTimeout(() => {
                window.location.reload();
            }, 2000);

        } catch (error) {
            btn.innerHTML = originalHTML;
            btn.disabled = false;
            window.toast?.error('Restart failed', error.message);
        }
    }

    async loadPage(pageId) {
        if (this.currentPage === pageId) return;

        const content = document.getElementById('page-content');

        // Save current tab state
        if (this.currentPage && !this.noCachePages.has(this.currentPage)) {
            this.saveTabState(this.currentPage, content.innerHTML);
        }

        // Start page exit animation
        content.classList.add('page-exit');

        // Start progress bar
        window.progressBar?.start();

        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.page === pageId);
        });

        // Wait for exit animation
        await new Promise(resolve => setTimeout(resolve, 200));

        // Check if we have cached state
        if (this.tabStates.has(pageId) && !this.noCachePages.has(pageId)) {
            content.innerHTML = this.tabStates.get(pageId);
            this.currentPage = pageId;
            this.tabPersistence.save(pageId);

            // Start enter animation
            content.classList.remove('page-exit');
            content.classList.add('page-enter');
            requestAnimationFrame(() => {
                content.classList.add('page-enter-active');
                content.classList.remove('page-enter');
            });

            window.progressBar?.done();
            this.executeScripts(content);
            return;
        }

        // Show skeleton loading state
        content.innerHTML = `
            <div style="padding: 2rem;">
                ${Skeleton.title()}
                ${Skeleton.text('80%')}
                ${Skeleton.text('60%')}
                ${Skeleton.chart()}
            </div>
        `;

        // Reset animation classes for skeleton
        content.classList.remove('page-exit', 'page-enter', 'page-enter-active');

        try {
            const response = await fetch(`/page/${pageId}`);
            const data = await response.json();

            if (response.ok) {
                const pageContent = data.html || '<p>No content available</p>';

                // Prepare enter animation
                content.classList.add('page-enter');
                content.innerHTML = pageContent;

                // Trigger enter animation
                requestAnimationFrame(() => {
                    content.classList.add('page-enter-active');
                    content.classList.remove('page-enter');
                });

                this.currentPage = pageId;
                this.tabPersistence.save(pageId);

                if (!this.noCachePages.has(pageId)) {
                    this.saveTabState(pageId, pageContent);
                }

                window.progressBar?.done();
                this.executeScripts(content);
            } else {
                content.classList.remove('page-exit', 'page-enter');
                content.innerHTML = createErrorState(
                    data.error || 'Unknown error',
                    () => window.skyeApp.loadPage(pageId)
                );
                window.progressBar?.done();
                window.toast?.error('Load failed', data.error || 'Failed to load page');
            }
        } catch (error) {
            content.classList.remove('page-exit', 'page-enter');
            content.innerHTML = createErrorState(
                error.message,
                () => window.skyeApp.loadPage(pageId)
            );
            window.progressBar?.done();
            window.toast?.error('Load failed', error.message);
        }
    }

    reloadCurrentPage() {
        if (this.currentPage) {
            this.tabStates.delete(this.currentPage);
            const tempPage = this.currentPage;
            this.currentPage = null;
            this.loadPage(tempPage);
        }
    }

    saveTabState(pageId, content) {
        this.tabStates.set(pageId, content);
    }

    executeScripts(container) {
        const scripts = Array.from(container.querySelectorAll('script'));
        const externalScripts = scripts.filter(s => s.src);
        const inlineScripts = scripts.filter(s => !s.src);

        const loadExternalScripts = () => {
            const promises = externalScripts.map(script => {
                return new Promise((resolve) => {
                    if (this.loadedScripts.has(script.src)) {
                        resolve();
                        return;
                    }
                    this.loadedScripts.add(script.src);
                    const newScript = document.createElement('script');
                    newScript.src = script.src;
                    newScript.onload = resolve;
                    newScript.onerror = resolve;
                    document.head.appendChild(newScript);
                });
            });
            return Promise.all(promises);
        };

        const runInlineScripts = () => {
            inlineScripts.forEach(script => {
                const newScript = document.createElement('script');
                newScript.textContent = script.textContent;
                document.head.appendChild(newScript);
            });
        };

        loadExternalScripts().then(runInlineScripts);
    }

    getLastTab() {
        return this.tabPersistence.load();
    }
}

// =============================================================================
// HELP MODAL
// =============================================================================

class HelpModal {
    constructor() {
        this.overlay = null;
        this.modal = null;
        this.init();
    }

    init() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'help-modal-overlay';
        this.overlay.addEventListener('click', () => this.hide());

        // Create modal
        this.modal = document.createElement('div');
        this.modal.className = 'help-modal';
        this.modal.innerHTML = `
            <div class="help-modal-header">
                <h2><i class="fas fa-dog"></i> About Skye</h2>
                <button class="help-modal-close">&times;</button>
            </div>
            <div class="help-modal-content">
                <div class="loading">Loading...</div>
            </div>
        `;

        // Prevent clicks inside modal from closing it
        this.modal.addEventListener('click', (e) => e.stopPropagation());

        // Close button
        this.modal.querySelector('.help-modal-close').addEventListener('click', () => this.hide());

        document.body.appendChild(this.overlay);
        document.body.appendChild(this.modal);

        // Bind help button
        const helpBtn = document.getElementById('helpBtn');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => this.show());
        }
    }

    async show() {
        this.overlay.classList.add('visible');
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';

        // Fetch README content
        try {
            const response = await fetch('/api/readme');
            const data = await response.json();
            if (data.content) {
                const html = this.parseMarkdown(data.content);
                this.modal.querySelector('.help-modal-content').innerHTML = html;
            }
        } catch (error) {
            this.modal.querySelector('.help-modal-content').innerHTML =
                '<p>Failed to load README content.</p>';
        }
    }

    hide() {
        this.overlay.classList.remove('visible');
        this.modal.classList.remove('visible');
        document.body.style.overflow = '';
    }

    parseMarkdown(md) {
        // Simple markdown parser
        let html = md
            // Escape HTML
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            // Code blocks (must be before inline code)
            .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
                `<pre><code>${code.trim()}</code></pre>`)
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Headers
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^# (.+)$/gm, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
            // Unordered lists
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            // Ordered lists
            .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
            // Tables
            .replace(/\|(.+)\|/g, (match) => {
                const cells = match.split('|').filter(c => c.trim());
                if (cells.every(c => /^[-:]+$/.test(c.trim()))) {
                    return ''; // Skip separator row
                }
                const isHeader = !this._tableStarted;
                this._tableStarted = true;
                const tag = isHeader ? 'th' : 'td';
                const row = cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('');
                return `<tr>${row}</tr>`;
            })
            // Paragraphs (lines that aren't already wrapped)
            .replace(/^(?!<[hluotp]|<tr)(.+)$/gm, '<p>$1</p>')
            // Clean up empty paragraphs
            .replace(/<p><\/p>/g, '')
            // Wrap consecutive li elements in ul
            .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
            // Wrap table rows
            .replace(/(<tr>.*<\/tr>\n?)+/g, '<table>$&</table>');

        this._tableStarted = false;
        return html;
    }
}

// =============================================================================
// GLOBAL FUNCTIONS
// =============================================================================

function switchTab(pageId) {
    if (window.skyeApp) {
        window.skyeApp.loadPage(pageId);
    }
}

// =============================================================================
// CONNECTION STATUS MONITOR
// =============================================================================

class ConnectionMonitor {
    constructor() {
        this.online = navigator.onLine;
        this.init();
    }

    init() {
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());

        // Handle visibility changes (pause/resume auto-refresh)
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                window.autoRefresh?.resume();
                // Refresh dashboard data when tab becomes visible
                if (window.skyeApp?.currentPage === 'dashboard') {
                    window.autoRefresh?.refresh('dashboard-prices');
                }
            } else {
                window.autoRefresh?.pause();
            }
        });
    }

    handleOnline() {
        this.online = true;
        window.toast?.success('Back online', 'Connection restored');
        // Trigger refresh of current page
        window.skyeApp?.reloadCurrentPage();
    }

    handleOffline() {
        this.online = false;
        window.toast?.warning('Offline', 'No internet connection');
    }

    isOnline() {
        return this.online;
    }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize managers
    window.progressBar = new ProgressBar();
    window.toast = new ToastManager();
    window.themeManager = new ThemeManager();
    window.apiClient = new APIClient();
    window.autoRefresh = new AutoRefreshManager();
    window.connectionMonitor = new ConnectionMonitor();
    window.skyeApp = new SkyeApp();
    window.pullToRefresh = new PullToRefresh(window.skyeApp);
    window.shortcuts = new KeyboardShortcuts(window.skyeApp);
    window.helpModal = new HelpModal();

    // Load last active tab or default to home
    const lastTab = window.skyeApp.getLastTab();
    const initialTab = lastTab || 'home';
    window.skyeApp.loadPage(initialTab);

    // Welcome toast (only on first load, not tab restore)
    if (!lastTab) {
        setTimeout(() => {
            window.toast.info('Welcome to Skye', 'Press ? for keyboard shortcuts');
        }, 1000);
    }
});
