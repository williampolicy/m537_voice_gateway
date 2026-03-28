#!/usr/bin/env python3
"""
M537 Voice Gateway - OpenAPI Client Generator
Generates client SDKs for multiple languages from OpenAPI spec
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Languages to generate
SUPPORTED_LANGUAGES = {
    "python": {
        "generator": "python",
        "package_name": "m537_client",
        "output_dir": "clients/python"
    },
    "typescript": {
        "generator": "typescript-fetch",
        "package_name": "m537-client",
        "output_dir": "clients/typescript"
    },
    "go": {
        "generator": "go",
        "package_name": "m537client",
        "output_dir": "clients/go"
    }
}


def get_openapi_spec(base_url: str = "http://localhost:5537") -> dict:
    """Fetch OpenAPI spec from running server"""
    import urllib.request
    import urllib.error

    url = f"{base_url}/openapi.json"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching OpenAPI spec: {e}")
        print("Make sure the server is running on", base_url)
        sys.exit(1)


def save_spec(spec: dict, output_path: str):
    """Save OpenAPI spec to file"""
    with open(output_path, "w") as f:
        json.dump(spec, f, indent=2)
    print(f"Saved OpenAPI spec to {output_path}")


def generate_client(language: str, spec_path: str, project_root: str):
    """Generate client SDK using OpenAPI Generator"""
    if language not in SUPPORTED_LANGUAGES:
        print(f"Unsupported language: {language}")
        print(f"Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}")
        return False

    config = SUPPORTED_LANGUAGES[language]
    output_dir = os.path.join(project_root, config["output_dir"])

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Try using docker-based openapi-generator
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{project_root}:/local",
        "openapitools/openapi-generator-cli:latest",
        "generate",
        "-i", f"/local/{os.path.relpath(spec_path, project_root)}",
        "-g", config["generator"],
        "-o", f"/local/{config['output_dir']}",
        "--package-name", config["package_name"],
        "--additional-properties=projectName=m537-voice-gateway"
    ]

    print(f"\nGenerating {language} client...")
    print(f"Output directory: {output_dir}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Successfully generated {language} client")
            return True
        else:
            print(f"✗ Failed to generate {language} client")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("Docker not found. Please install Docker or use a different method.")
        print("\nAlternative: Install openapi-generator-cli:")
        print("  npm install @openapitools/openapi-generator-cli -g")
        print("  openapi-generator-cli generate -i openapi.json -g python -o clients/python")
        return False


def generate_typescript_types(spec: dict, output_path: str):
    """Generate TypeScript types manually (no external dependencies)"""
    types_content = '''/**
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
        this.baseUrl = baseUrl.replace(/\\/$/, '');
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
'''

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(types_content)
    print(f"Generated TypeScript types: {output_path}")


def generate_python_client(spec: dict, output_path: str):
    """Generate Python client manually (no external dependencies)"""
    client_content = '''"""
M537 Voice Gateway - Python Client
Auto-generated from OpenAPI specification
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import json
import urllib.request
import urllib.error


@dataclass
class VoiceQueryRequest:
    """Voice query request"""
    transcript: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    language: Optional[str] = None
    include_raw: bool = False


@dataclass
class VoiceQueryData:
    """Voice query response data"""
    answer_text: str
    intent: str
    confidence: float
    tool_used: str
    suggestions: List[str]
    cached: bool
    language: str
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class ErrorInfo:
    """Error information"""
    code: str
    message: str
    suggestions: Optional[List[str]] = None


@dataclass
class VoiceQueryResponse:
    """Voice query response"""
    success: bool
    timestamp: str
    request_id: str
    api_version: str
    data: Optional[VoiceQueryData] = None
    error: Optional[ErrorInfo] = None


@dataclass
class HealthCheck:
    """Health check result"""
    name: str
    status: str
    latency_ms: float
    details: Optional[Dict[str, Any]] = None


@dataclass
class HealthResponse:
    """Health check response"""
    status: str
    version: str
    api_version: str
    timestamp: str
    uptime_seconds: int
    checks: List[HealthCheck]


class M537Client:
    """M537 Voice Gateway API Client"""

    def __init__(self, base_url: str = "http://localhost:5537"):
        self.base_url = base_url.rstrip("/")

    def query(self, request: VoiceQueryRequest) -> VoiceQueryResponse:
        """Send a voice query"""
        data = {
            "transcript": request.transcript,
            "session_id": request.session_id,
            "context": request.context or {},
            "language": request.language,
            "include_raw": request.include_raw
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        result = self._post("/api/v1/voice-query", data)
        return self._parse_voice_response(result)

    def health(self) -> HealthResponse:
        """Get detailed health status"""
        result = self._get("/api/v1/health")
        return self._parse_health_response(result)

    def health_summary(self) -> Dict[str, Any]:
        """Get quick health summary"""
        return self._get("/api/v1/health/summary")

    def metrics(self) -> Dict[str, Any]:
        """Get metrics"""
        return self._get("/api/metrics/json")

    def _get(self, path: str) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection failed: {e.reason}"}

    def _post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            try:
                return json.loads(e.read().decode())
            except:
                return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection failed: {e.reason}"}

    def _parse_voice_response(self, data: Dict[str, Any]) -> VoiceQueryResponse:
        """Parse voice query response"""
        voice_data = None
        error = None

        if data.get("data"):
            d = data["data"]
            voice_data = VoiceQueryData(
                answer_text=d.get("answer_text", ""),
                intent=d.get("intent", ""),
                confidence=d.get("confidence", 0),
                tool_used=d.get("tool_used", ""),
                suggestions=d.get("suggestions", []),
                cached=d.get("cached", False),
                language=d.get("language", "zh-CN"),
                raw_data=d.get("raw_data")
            )

        if data.get("error"):
            e = data["error"]
            error = ErrorInfo(
                code=e.get("code", "UNKNOWN"),
                message=e.get("message", "Unknown error"),
                suggestions=e.get("suggestions")
            )

        return VoiceQueryResponse(
            success=data.get("success", False),
            timestamp=data.get("timestamp", ""),
            request_id=data.get("request_id", ""),
            api_version=data.get("api_version", "v1"),
            data=voice_data,
            error=error
        )

    def _parse_health_response(self, data: Dict[str, Any]) -> HealthResponse:
        """Parse health response"""
        checks = []
        for c in data.get("checks", []):
            checks.append(HealthCheck(
                name=c.get("name", ""),
                status=c.get("status", "unknown"),
                latency_ms=c.get("latency_ms", 0),
                details=c.get("details")
            ))

        return HealthResponse(
            status=data.get("status", "unknown"),
            version=data.get("version", ""),
            api_version=data.get("api_version", "v1"),
            timestamp=data.get("timestamp", ""),
            uptime_seconds=data.get("uptime_seconds", 0),
            checks=checks
        )


# Convenience function
def create_client(base_url: str = "http://localhost:5537") -> M537Client:
    """Create a new M537 client"""
    return M537Client(base_url)
'''

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(client_content)
    print(f"Generated Python client: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate M537 API clients")
    parser.add_argument(
        "--url",
        default="http://localhost:5537",
        help="Server URL to fetch OpenAPI spec"
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["python", "typescript"],
        help="Languages to generate clients for"
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory"
    )
    parser.add_argument(
        "--save-spec",
        action="store_true",
        help="Save OpenAPI spec to file"
    )

    args = parser.parse_args()
    project_root = os.path.abspath(args.output)

    print("M537 Voice Gateway - Client Generator")
    print("=" * 40)

    # Generate lightweight clients (no external dependencies needed)
    if "python" in args.languages:
        output_path = os.path.join(project_root, "clients", "python", "m537_client.py")
        generate_python_client({}, output_path)

    if "typescript" in args.languages:
        output_path = os.path.join(project_root, "clients", "typescript", "m537-client.ts")
        generate_typescript_types({}, output_path)

    print("\n" + "=" * 40)
    print("Client generation complete!")
    print(f"Clients saved to: {os.path.join(project_root, 'clients')}")


if __name__ == "__main__":
    main()
