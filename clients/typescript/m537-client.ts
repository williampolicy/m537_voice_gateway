/**
 * M537 Voice Gateway - TypeScript Client
 * Enterprise-grade SDK with full feature support
 *
 * Features:
 * - API Key authentication
 * - Voice query with caching
 * - Analytics endpoints
 * - Webhook management
 * - Health monitoring
 * - Automatic retries with exponential backoff
 */

// ==================== Request Types ====================

export interface VoiceQueryRequest {
    transcript: string;
    session_id?: string;
    context?: Record<string, unknown>;
    language?: 'zh-CN' | 'en-US' | 'ja-JP';
    include_raw?: boolean;
}

export interface WebhookCreateRequest {
    url: string;
    events: WebhookEvent[];
    secret?: string;
    metadata?: Record<string, unknown>;
}

// ==================== Response Types ====================

export interface VoiceQueryResponse {
    success: boolean;
    data?: VoiceQueryData;
    error?: ErrorInfo;
    timestamp: string;
    request_id: string;
    api_version: string;
}

export interface VoiceQueryData {
    answer_text: string;
    intent: string;
    confidence: number;
    tool_used: string;
    suggestions: string[];
    cached: boolean;
    language: string;
    raw_data?: Record<string, unknown>;
}

export interface ErrorInfo {
    code: string;
    message: string;
    suggestions?: string[];
}

export interface HealthResponse {
    status: 'healthy' | 'degraded' | 'unhealthy';
    version: string;
    api_version: string;
    timestamp: string;
    uptime_seconds: number;
    checks: HealthCheck[];
}

export interface HealthCheck {
    name: string;
    status: 'healthy' | 'degraded' | 'unhealthy';
    latency_ms: number;
    details?: Record<string, unknown>;
}

export interface AnalyticsSummary {
    total_queries: number;
    successful_queries: number;
    failed_queries: number;
    cache_hit_rate: number;
    avg_latency_ms: number;
    p95_latency_ms: number;
    p99_latency_ms: number;
    top_intents: Array<{ intent: string; count: number; percentage: number }>;
    language_distribution: Record<string, number>;
}

export interface AnalyticsTrend {
    period_hours: number;
    trend: Array<{ hour: string; count: number }>;
}

export interface WebhookSubscription {
    id: string;
    url: string;
    events: string[];
    enabled: boolean;
    total_deliveries?: number;
    successful_deliveries?: number;
    failed_deliveries?: number;
    created_at?: string;
    last_delivery_at?: string;
    last_error?: string;
}

// ==================== Enums ====================

export type WebhookEvent =
    | 'query.completed'
    | 'query.failed'
    | 'health.degraded'
    | 'health.recovered'
    | 'rate_limit.exceeded'
    | 'error.threshold'
    | 'system.alert';

export enum RateLimitTier {
    FREE = 'free',
    STANDARD = 'standard',
    PREMIUM = 'premium',
    ENTERPRISE = 'enterprise'
}

// ==================== Error Classes ====================

export class M537ClientError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'M537ClientError';
    }
}

export class AuthenticationError extends M537ClientError {
    constructor(message: string = 'Invalid API key') {
        super(message);
        this.name = 'AuthenticationError';
    }
}

export class RateLimitError extends M537ClientError {
    retryAfter: number;

    constructor(message: string = 'Rate limit exceeded', retryAfter: number = 60) {
        super(message);
        this.name = 'RateLimitError';
        this.retryAfter = retryAfter;
    }
}

// ==================== Client Options ====================

export interface M537ClientOptions {
    baseUrl?: string;
    apiKey?: string;
    timeout?: number;
    maxRetries?: number;
    retryDelay?: number;
}

// ==================== Client Class ====================

export class M537Client {
    private baseUrl: string;
    private apiKey?: string;
    private timeout: number;
    private maxRetries: number;
    private retryDelay: number;

    constructor(options: M537ClientOptions = {}) {
        this.baseUrl = (options.baseUrl || 'http://localhost:5537').replace(/\/$/, '');
        this.apiKey = options.apiKey;
        this.timeout = options.timeout || 30000;
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000;
    }

    // ==================== Voice API ====================

    /**
     * Send a voice query
     */
    async query(request: VoiceQueryRequest): Promise<VoiceQueryResponse> {
        return this.post<VoiceQueryResponse>('/api/v1/voice-query', request);
    }

    /**
     * Quick query - returns just the answer text
     */
    async quickQuery(transcript: string): Promise<string> {
        const response = await this.query({ transcript });
        if (response.success && response.data) {
            return response.data.answer_text;
        }
        if (response.error) {
            throw new M537ClientError(response.error.message);
        }
        throw new M537ClientError('Unknown error');
    }

    // ==================== Health API ====================

    /**
     * Get detailed health status
     */
    async health(): Promise<HealthResponse> {
        return this.get<HealthResponse>('/api/v1/health');
    }

    /**
     * Get quick health summary
     */
    async healthSummary(): Promise<{ status: string; version: string; uptime_seconds: number }> {
        return this.get('/api/v1/health/summary');
    }

    /**
     * Check if service is healthy
     */
    async isHealthy(): Promise<boolean> {
        try {
            const result = await this.healthSummary();
            return result.status === 'healthy';
        } catch {
            return false;
        }
    }

    // ==================== Metrics API ====================

    /**
     * Get metrics in JSON format
     */
    async metrics(): Promise<Record<string, unknown>> {
        return this.get('/api/metrics/json');
    }

    /**
     * Get metrics in Prometheus format
     */
    async metricsPrometheus(): Promise<string> {
        return this.getText('/api/metrics');
    }

    // ==================== Analytics API ====================

    /**
     * Get analytics summary
     */
    async getAnalytics(): Promise<AnalyticsSummary> {
        return this.get<AnalyticsSummary>('/api/analytics/summary');
    }

    /**
     * Get hourly analytics trend
     */
    async getAnalyticsTrend(hours: number = 24): Promise<AnalyticsTrend> {
        return this.get<AnalyticsTrend>(`/api/analytics/trend?hours=${hours}`);
    }

    /**
     * Get intent usage breakdown
     */
    async getIntentBreakdown(): Promise<Record<string, unknown>> {
        return this.get('/api/analytics/intents');
    }

    /**
     * Get error breakdown
     */
    async getErrorBreakdown(): Promise<Record<string, unknown>> {
        return this.get('/api/analytics/errors');
    }

    /**
     * Get performance statistics
     */
    async getPerformanceStats(): Promise<Record<string, unknown>> {
        return this.get('/api/analytics/performance');
    }

    // ==================== Webhook API ====================

    /**
     * List all webhook subscriptions
     */
    async listWebhooks(): Promise<WebhookSubscription[]> {
        const result = await this.get<{ webhooks: WebhookSubscription[] }>('/api/webhooks');
        return result.webhooks || [];
    }

    /**
     * Create a webhook subscription
     */
    async createWebhook(request: WebhookCreateRequest): Promise<WebhookSubscription> {
        const result = await this.post<{ success: boolean; webhook: WebhookSubscription }>(
            '/api/webhooks',
            request
        );
        return result.webhook;
    }

    /**
     * Get webhook subscription details
     */
    async getWebhook(webhookId: string): Promise<WebhookSubscription> {
        return this.get<WebhookSubscription>(`/api/webhooks/${webhookId}`);
    }

    /**
     * Delete a webhook subscription
     */
    async deleteWebhook(webhookId: string): Promise<boolean> {
        const result = await this.delete<{ success: boolean }>(`/api/webhooks/${webhookId}`);
        return result.success;
    }

    /**
     * List available webhook events
     */
    async listWebhookEvents(): Promise<Array<{ name: string; description: string }>> {
        const result = await this.get<{ events: Array<{ name: string; description: string }> }>(
            '/api/webhooks/events/list'
        );
        return result.events || [];
    }

    // ==================== Internal Methods ====================

    private getHeaders(): Record<string, string> {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'M537-TypeScript-Client/1.0'
        };
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        return headers;
    }

    private async get<T>(path: string): Promise<T> {
        return this.request<T>('GET', path);
    }

    private async getText(path: string): Promise<string> {
        const response = await fetch(`${this.baseUrl}${path}`, {
            headers: this.getHeaders()
        });
        return response.text();
    }

    private async post<T>(path: string, data: unknown): Promise<T> {
        return this.request<T>('POST', path, data);
    }

    private async delete<T>(path: string): Promise<T> {
        return this.request<T>('DELETE', path);
    }

    private async request<T>(
        method: string,
        path: string,
        data?: unknown
    ): Promise<T> {
        let lastError: Error | null = null;

        for (let attempt = 0; attempt < this.maxRetries; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);

                const options: RequestInit = {
                    method,
                    headers: this.getHeaders(),
                    signal: controller.signal
                };

                if (data) {
                    options.body = JSON.stringify(data);
                }

                const response = await fetch(`${this.baseUrl}${path}`, options);
                clearTimeout(timeoutId);

                if (response.status === 401) {
                    throw new AuthenticationError();
                }

                if (response.status === 429) {
                    const retryAfter = parseInt(response.headers.get('Retry-After') || '60', 10);
                    throw new RateLimitError('Rate limit exceeded', retryAfter);
                }

                if (response.status >= 500) {
                    lastError = new M537ClientError(`HTTP ${response.status}`);
                    if (attempt < this.maxRetries - 1) {
                        const delay = this.retryDelay * Math.pow(2, attempt);
                        await this.sleep(delay);
                        continue;
                    }
                }

                return response.json();
            } catch (error) {
                if (error instanceof AuthenticationError || error instanceof RateLimitError) {
                    throw error;
                }

                lastError = error as Error;
                if (attempt < this.maxRetries - 1) {
                    const delay = this.retryDelay * Math.pow(2, attempt);
                    await this.sleep(delay);
                    continue;
                }
            }
        }

        throw new M537ClientError(
            `Request failed after ${this.maxRetries} attempts: ${lastError?.message}`
        );
    }

    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ==================== Webhook Signature Verification ====================

/**
 * Verify webhook signature
 */
export async function verifyWebhookSignature(
    payload: string,
    signature: string,
    secret: string,
    timestamp: string
): Promise<boolean> {
    const message = `${timestamp}.${payload}`;
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
        'raw',
        encoder.encode(secret),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
    );
    const signatureBuffer = await crypto.subtle.sign(
        'HMAC',
        key,
        encoder.encode(message)
    );
    const expected = `sha256=${Array.from(new Uint8Array(signatureBuffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('')}`;
    return signature === expected;
}

// ==================== Factory Functions ====================

/**
 * Create a new M537 client
 */
export function createClient(options?: M537ClientOptions): M537Client {
    return new M537Client(options);
}

/**
 * Quick query function
 */
export async function quickQuery(
    transcript: string,
    options?: M537ClientOptions
): Promise<string> {
    const client = createClient(options);
    return client.quickQuery(transcript);
}

export default M537Client;
