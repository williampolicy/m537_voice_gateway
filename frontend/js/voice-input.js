/**
 * M537 Voice Input Module
 * Handles speech recognition using Web Speech API
 */
class VoiceInput {
    constructor(options = {}) {
        this.recognition = null;
        this.isListening = false;
        this.onResult = options.onResult || (() => {});
        this.onInterim = options.onInterim || (() => {});
        this.onError = options.onError || (() => {});
        this.onStart = options.onStart || (() => {});
        this.onEnd = options.onEnd || (() => {});

        this.init();
    }

    init() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.error('Speech Recognition not supported');
            this.onError('browser_not_supported');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = CONFIG.SPEECH_CONTINUOUS;
        this.recognition.interimResults = CONFIG.SPEECH_INTERIM_RESULTS;
        this.recognition.lang = CONFIG.SPEECH_LANG;

        this.recognition.onstart = () => {
            this.isListening = true;
            this.onStart();
            if (CONFIG.DEBUG) console.log('Speech recognition started');
        };

        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (interimTranscript) {
                this.onInterim(interimTranscript);
            }

            if (finalTranscript) {
                this.onResult(finalTranscript);
            }
        };

        this.recognition.onerror = (event) => {
            if (CONFIG.DEBUG) console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.onError(event.error);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.onEnd();
            if (CONFIG.DEBUG) console.log('Speech recognition ended');
        };
    }

    start() {
        if (!this.recognition) {
            this.onError('not_initialized');
            return false;
        }

        if (this.isListening) {
            return false;
        }

        try {
            this.recognition.start();
            return true;
        } catch (error) {
            console.error('Failed to start recognition:', error);
            this.onError('start_failed');
            return false;
        }
    }

    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            return true;
        }
        return false;
    }

    abort() {
        if (this.recognition) {
            this.recognition.abort();
            this.isListening = false;
        }
    }

    isSupported() {
        return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    }
}
