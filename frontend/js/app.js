/**
 * M537 Voice Gateway Main Application
 */
class App {
    constructor() {
        // Elements
        this.recordButton = document.getElementById('recordButton');
        this.recordStatus = document.getElementById('recordStatus');
        this.currentInput = document.getElementById('currentInput');
        this.chatContainer = document.getElementById('chatContainer');
        this.quickButtons = document.querySelectorAll('.quick-btn');

        // State
        this.isRecording = false;
        this.isProcessing = false;
        this.sessionId = this.generateSessionId();

        // Modules
        this.api = new ApiClient();
        this.voiceInput = new VoiceInput({
            onResult: (text) => this.handleVoiceResult(text),
            onInterim: (text) => this.handleInterimResult(text),
            onError: (error) => this.handleVoiceError(error),
            onStart: () => this.handleRecordingStart(),
            onEnd: () => this.handleRecordingEnd()
        });
        this.voiceOutput = new VoiceOutput({
            onStart: () => this.handleSpeakingStart(),
            onEnd: () => this.handleSpeakingEnd()
        });

        // Voice visualizer
        this.visualizer = new VoiceVisualizer('voiceVisualizer', {
            barCount: 40,
            barColor: '#2563eb',
            barColorActive: '#ef4444',
            smoothing: 0.85
        });
        window.voiceVisualizer = this.visualizer;

        this.init();
    }

    init() {
        // Check browser support
        if (!this.voiceInput.isSupported()) {
            this.showMessage('error', '您的浏览器不支持语音识别，请使用 Chrome 或 Edge 浏览器。');
            this.recordButton.disabled = true;
            return;
        }

        // Bind events
        this.recordButton.addEventListener('click', () => this.toggleRecording());

        this.quickButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.dataset.query;
                if (query) {
                    this.processQuery(query);
                }
            });
        });

        // Clear welcome message on first interaction
        this.clearWelcomeOnce = false;

        if (CONFIG.DEBUG) {
            console.log('M537 App initialized');
        }
    }

    generateSessionId() {
        return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    toggleRecording() {
        if (this.isProcessing) return;

        if (this.isRecording) {
            this.voiceInput.stop();
        } else {
            this.voiceInput.start();
        }
    }

    handleRecordingStart() {
        this.isRecording = true;
        this.recordButton.classList.add('recording');
        this.recordButton.querySelector('.mic-icon').classList.add('hidden');
        this.recordButton.querySelector('.stop-icon').classList.remove('hidden');
        this.recordStatus.textContent = '录音中...';
        this.recordStatus.classList.add('recording');
        this.currentInput.textContent = '正在聆听...';
        this.currentInput.classList.add('interim');

        // Start visualizer
        this.visualizer.start();
    }

    handleRecordingEnd() {
        this.isRecording = false;
        this.recordButton.classList.remove('recording');
        this.recordButton.querySelector('.mic-icon').classList.remove('hidden');
        this.recordButton.querySelector('.stop-icon').classList.add('hidden');
        this.recordStatus.textContent = '点击开始录音';
        this.recordStatus.classList.remove('recording');

        // Stop visualizer
        this.visualizer.stop();
    }

    handleInterimResult(text) {
        this.currentInput.textContent = text;
        this.currentInput.classList.add('interim');
    }

    handleVoiceResult(text) {
        this.currentInput.textContent = text;
        this.currentInput.classList.remove('interim');
        this.processQuery(text);
    }

    handleVoiceError(error) {
        console.error('Voice error:', error);

        let message = '语音识别出错';
        switch (error) {
            case 'not-allowed':
                message = '请允许麦克风访问权限';
                break;
            case 'no-speech':
                message = '未检测到语音，请重试';
                break;
            case 'network':
                message = '网络错误，请检查网络连接';
                break;
            case 'browser_not_supported':
                message = '您的浏览器不支持语音识别';
                break;
        }

        this.recordStatus.textContent = message;
        this.currentInput.textContent = message;
    }

    handleSpeakingStart() {
        // Could add visual indicator for speaking
    }

    handleSpeakingEnd() {
        // Speaking finished
    }

    async processQuery(text) {
        if (!text || text.trim() === '') return;

        // Clear welcome message on first query
        if (!this.clearWelcomeOnce) {
            const welcome = this.chatContainer.querySelector('.welcome-message');
            if (welcome) welcome.remove();
            this.clearWelcomeOnce = true;
        }

        // Show user message
        this.showMessage('user', text);

        // Set processing state
        this.isProcessing = true;
        this.recordButton.classList.add('processing');
        this.recordStatus.textContent = '处理中...';
        this.currentInput.textContent = '等待响应...';

        // Show processing animation
        this.visualizer.drawProcessingAnimation();

        try {
            const response = await this.api.voiceQuery(text, this.sessionId);

            if (response.success) {
                const answerText = response.data.answer_text;
                this.showMessage('system', answerText);

                // Auto speak response
                if (CONFIG.AUTO_SPEAK) {
                    this.voiceOutput.speak(answerText);
                }

                // Show suggestions if available
                if (response.data.suggestions && response.data.suggestions.length > 0) {
                    const suggestText = '你还可以问：' + response.data.suggestions.slice(0, 2).join('、');
                    // Don't show suggestions in chat, just log
                    if (CONFIG.DEBUG) console.log('Suggestions:', suggestText);
                }
            } else {
                const errorMsg = response.error?.message || '请求失败';
                this.showMessage('error', errorMsg);

                if (response.error?.suggestions) {
                    const suggestText = '你可以尝试问：' + response.error.suggestions.slice(0, 3).join('、');
                    this.showMessage('system', suggestText);
                }
            }
        } catch (error) {
            this.showMessage('error', '请求失败：' + error.message);
        } finally {
            this.isProcessing = false;
            this.recordButton.classList.remove('processing');
            this.recordStatus.textContent = '点击开始录音';
            this.currentInput.textContent = '等待录音...';

            // Stop processing animation
            this.visualizer.stopProcessingAnimation();
        }
    }

    showMessage(type, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const label = type === 'user' ? '你' : (type === 'error' ? '错误' : '系统');
        messageDiv.innerHTML = `<span class="label">${label}</span>${this.escapeHtml(text)}`;

        this.chatContainer.appendChild(messageDiv);

        // Scroll to bottom
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;

        // Limit messages
        const messages = this.chatContainer.querySelectorAll('.message');
        if (messages.length > CONFIG.MAX_MESSAGES) {
            messages[0].remove();
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
