/**
 * M537 Voice Output Module
 * Handles text-to-speech using Web Speech API
 */
class VoiceOutput {
    constructor(options = {}) {
        this.synth = window.speechSynthesis;
        this.voice = null;
        this.rate = options.rate || CONFIG.TTS_RATE;
        this.pitch = options.pitch || CONFIG.TTS_PITCH;
        this.volume = options.volume || CONFIG.TTS_VOLUME;
        this.onStart = options.onStart || (() => {});
        this.onEnd = options.onEnd || (() => {});
        this.onError = options.onError || (() => {});

        this.init();
    }

    init() {
        if (!this.synth) {
            console.error('Speech Synthesis not supported');
            return;
        }

        // Wait for voices to load
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = () => this.selectVoice();
        }

        // Try to select voice immediately
        this.selectVoice();
    }

    selectVoice() {
        const voices = this.synth.getVoices();

        if (voices.length === 0) {
            return;
        }

        // Priority: Chinese voices
        this.voice = voices.find(v => v.lang.includes('zh-CN'))
                  || voices.find(v => v.lang.includes('zh'))
                  || voices.find(v => v.lang.includes('cmn'))
                  || voices.find(v => v.name.includes('Chinese'))
                  || voices[0];

        if (CONFIG.DEBUG) {
            console.log('Selected voice:', this.voice?.name);
        }
    }

    speak(text) {
        if (!this.synth) {
            this.onError('not_supported');
            return false;
        }

        if (!text || text.trim() === '') {
            return false;
        }

        // Cancel any ongoing speech
        this.synth.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        if (this.voice) {
            utterance.voice = this.voice;
        }

        utterance.rate = this.rate;
        utterance.pitch = this.pitch;
        utterance.volume = this.volume;
        utterance.lang = CONFIG.SPEECH_LANG;

        utterance.onstart = () => {
            this.onStart();
            if (CONFIG.DEBUG) console.log('TTS started');
        };

        utterance.onend = () => {
            this.onEnd();
            if (CONFIG.DEBUG) console.log('TTS ended');
        };

        utterance.onerror = (event) => {
            this.onError(event.error);
            if (CONFIG.DEBUG) console.error('TTS error:', event.error);
        };

        this.synth.speak(utterance);
        return true;
    }

    stop() {
        if (this.synth) {
            this.synth.cancel();
        }
    }

    pause() {
        if (this.synth) {
            this.synth.pause();
        }
    }

    resume() {
        if (this.synth) {
            this.synth.resume();
        }
    }

    isSpeaking() {
        return this.synth ? this.synth.speaking : false;
    }

    isSupported() {
        return !!window.speechSynthesis;
    }
}
