/**
 * M537 Voice Gateway - Keyboard Shortcuts
 * Enhances accessibility and power user experience
 */
class KeyboardShortcuts {
    constructor(app) {
        this.app = app;
        this.enabled = true;
        this.shortcuts = new Map();
        this.helpModal = null;

        this.init();
    }

    init() {
        // Register default shortcuts
        this.register('Space', 'Toggle recording', () => {
            if (document.activeElement.tagName !== 'INPUT' &&
                document.activeElement.tagName !== 'TEXTAREA') {
                this.app.toggleRecording();
            }
        });

        this.register('Escape', 'Stop recording/speaking', () => {
            if (this.app.isRecording) {
                this.app.voiceInput.stop();
            }
            if (this.app.voiceOutput.isSpeaking) {
                this.app.voiceOutput.cancel();
            }
        });

        this.register('1', 'Quick: Count projects', () => this.quickQuery(0));
        this.register('2', 'Quick: System status', () => this.quickQuery(1));
        this.register('3', 'Quick: List ports', () => this.quickQuery(2));
        this.register('4', 'Quick: Recent errors', () => this.quickQuery(3));
        this.register('5', 'Quick: P0 health', () => this.quickQuery(4));

        this.register('/', 'Focus search/command', () => {
            // Future: focus command input
        });

        this.register('?', 'Show keyboard shortcuts', () => {
            this.showHelp();
        });

        this.register('c', 'Clear chat history', () => {
            this.clearChat();
        });

        this.register('m', 'Toggle mute (TTS)', () => {
            this.toggleMute();
        });

        this.register('r', 'Refresh system status', () => {
            if (window.systemMonitor && window.systemMonitor.client) {
                window.systemMonitor.client.refresh();
            }
        });

        // Listen for key events
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));

        console.log('[Shortcuts] Keyboard shortcuts enabled');
    }

    register(key, description, handler) {
        this.shortcuts.set(key.toLowerCase(), {
            key,
            description,
            handler
        });
    }

    handleKeyDown(event) {
        if (!this.enabled) return;

        // Ignore if in input field (except for specific keys)
        const inInput = ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName);
        const allowInInput = ['Escape'];

        if (inInput && !allowInInput.includes(event.key)) {
            return;
        }

        // Ignore if modifier keys pressed (except for ?)
        if (event.ctrlKey || event.altKey || event.metaKey) {
            return;
        }

        const key = event.key.toLowerCase();
        const shortcut = this.shortcuts.get(key);

        if (shortcut) {
            event.preventDefault();
            shortcut.handler();
        }
    }

    quickQuery(index) {
        const buttons = document.querySelectorAll('.quick-btn');
        if (buttons[index]) {
            const query = buttons[index].dataset.query;
            if (query) {
                this.app.processQuery(query);
            }
        }
    }

    clearChat() {
        const chatContainer = document.getElementById('chatContainer');
        const messages = chatContainer.querySelectorAll('.message');
        messages.forEach(m => m.remove());

        // Show confirmation
        this.showToast('聊天记录已清空');
    }

    toggleMute() {
        const config = window.CONFIG || {};
        config.AUTO_SPEAK = !config.AUTO_SPEAK;
        this.showToast(config.AUTO_SPEAK ? '语音播报已开启' : '语音播报已关闭');
    }

    showHelp() {
        if (this.helpModal) {
            this.closeHelp();
            return;
        }

        const modal = document.createElement('div');
        modal.className = 'shortcuts-modal';
        modal.innerHTML = `
            <div class="shortcuts-content">
                <div class="shortcuts-header">
                    <h3>键盘快捷键</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="shortcuts-body">
                    ${this.getShortcutsHTML()}
                </div>
                <div class="shortcuts-footer">
                    按 Esc 或 ? 关闭
                </div>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.id = 'shortcuts-style';
        style.textContent = `
            .shortcuts-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                animation: fadeIn 0.2s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            .shortcuts-content {
                background: white;
                border-radius: 12px;
                width: 90%;
                max-width: 400px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                animation: slideUp 0.3s ease;
            }

            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            @media (prefers-color-scheme: dark) {
                .shortcuts-content {
                    background: #1e1e1e;
                    color: #fff;
                }
            }

            .shortcuts-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                border-bottom: 1px solid #eee;
            }

            @media (prefers-color-scheme: dark) {
                .shortcuts-header { border-color: #333; }
            }

            .shortcuts-header h3 {
                margin: 0;
                font-size: 18px;
            }

            .close-btn {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #666;
            }

            .shortcuts-body {
                padding: 15px 20px;
                max-height: 300px;
                overflow-y: auto;
            }

            .shortcut-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
            }

            .shortcut-key {
                background: #f0f0f0;
                padding: 4px 10px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 14px;
            }

            @media (prefers-color-scheme: dark) {
                .shortcut-key { background: #333; }
            }

            .shortcuts-footer {
                padding: 12px 20px;
                text-align: center;
                border-top: 1px solid #eee;
                font-size: 12px;
                color: #999;
            }

            .toast {
                position: fixed;
                bottom: 100px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 14px;
                z-index: 10000;
                animation: toastIn 0.3s ease, toastOut 0.3s ease 2s forwards;
            }

            @keyframes toastIn {
                from { opacity: 0; transform: translateX(-50%) translateY(10px); }
                to { opacity: 1; transform: translateX(-50%) translateY(0); }
            }

            @keyframes toastOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;

        if (!document.getElementById('shortcuts-style')) {
            document.head.appendChild(style);
        }

        document.body.appendChild(modal);
        this.helpModal = modal;

        // Close handlers
        modal.querySelector('.close-btn').addEventListener('click', () => this.closeHelp());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeHelp();
        });
    }

    closeHelp() {
        if (this.helpModal) {
            this.helpModal.remove();
            this.helpModal = null;
        }
    }

    getShortcutsHTML() {
        let html = '';
        for (const [key, shortcut] of this.shortcuts) {
            html += `
                <div class="shortcut-item">
                    <span class="shortcut-desc">${shortcut.description}</span>
                    <span class="shortcut-key">${this.formatKey(shortcut.key)}</span>
                </div>
            `;
        }
        return html;
    }

    formatKey(key) {
        const keyMap = {
            'space': 'Space',
            'escape': 'Esc',
            '/': '/',
            '?': '?'
        };
        return keyMap[key.toLowerCase()] || key.toUpperCase();
    }

    showToast(message) {
        // Remove existing toast
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.remove(), 2300);
    }
}

// Initialize when app is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for app to be initialized
    setTimeout(() => {
        if (window.app) {
            window.keyboardShortcuts = new KeyboardShortcuts(window.app);
        }
    }, 100);
});
