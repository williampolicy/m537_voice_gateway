/**
 * M537 API Client Module
 * Handles communication with the backend
 */
class ApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || CONFIG.API_BASE_URL;
    }

    async voiceQuery(transcript, sessionId = null) {
        const url = `${this.baseUrl}${CONFIG.VOICE_QUERY_ENDPOINT}`;

        const body = {
            transcript: transcript,
            session_id: sessionId,
            context: {}
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async healthCheck() {
        const url = `${this.baseUrl}${CONFIG.HEALTH_ENDPOINT}`;

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }
}
