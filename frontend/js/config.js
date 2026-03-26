/**
 * M537 Voice Gateway Configuration
 */
const CONFIG = {
    // API endpoints
    API_BASE_URL: '',  // Empty for same origin
    VOICE_QUERY_ENDPOINT: '/api/voice-query',
    HEALTH_ENDPOINT: '/health',

    // Speech recognition settings
    SPEECH_LANG: 'zh-CN',
    SPEECH_CONTINUOUS: false,
    SPEECH_INTERIM_RESULTS: true,

    // TTS settings
    TTS_RATE: 1.0,
    TTS_PITCH: 1.0,
    TTS_VOLUME: 1.0,

    // UI settings
    MAX_MESSAGES: 50,
    AUTO_SPEAK: true,

    // Debug
    DEBUG: false
};

// Log config in debug mode
if (CONFIG.DEBUG) {
    console.log('M537 Config:', CONFIG);
}
