/**
 * M537 Voice Gateway - TypeScript Types
 * Auto-generated from OpenAPI specification
 */

// Request types
export interface VoiceQueryRequest {
    transcript: string;
    session_id?: string;
    context?: Record<string, any>;
    language?: 'zh-CN' | 'en-US' | 'ja-JP';
    include_raw?: boolean;
}

// Response types
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
    raw_data?: Record<string, any>;
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
    details?: Record<string, any>;
}

// Client class
export class M537Client {
    private baseUrl: string;
    private defaultHeaders: Record<string, string>;

    constructor(baseUrl: string = 'http://localhost:5537') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    async query(request: VoiceQueryRequest): Promise<VoiceQueryResponse> {
        const response = await fetch(`${this.baseUrl}/api/v1/voice-query`, {
            method: 'POST',
            headers: this.defaultHeaders,
            body: JSON.stringify(request)
        });
        return response.json();
    }

    async health(): Promise<HealthResponse> {
        const response = await fetch(`${this.baseUrl}/api/v1/health`, {
            headers: this.defaultHeaders
        });
        return response.json();
    }

    async healthSummary(): Promise<{ status: string; version: string; uptime_seconds: number }> {
        const response = await fetch(`${this.baseUrl}/api/v1/health/summary`, {
            headers: this.defaultHeaders
        });
        return response.json();
    }

    async metrics(): Promise<Record<string, any>> {
        const response = await fetch(`${this.baseUrl}/api/metrics/json`, {
            headers: this.defaultHeaders
        });
        return response.json();
    }
}

export default M537Client;
