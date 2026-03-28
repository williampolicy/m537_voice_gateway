"""
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
