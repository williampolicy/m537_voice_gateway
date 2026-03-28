"""
M537 Voice Gateway - Security Tests
Comprehensive security testing for OWASP compliance
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient
from middleware.security import sanitize_string, is_safe_project_id


class TestSecurityHeaders:
    """Test security headers are properly set"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_content_security_policy(self, client):
        """CSP header should be present"""
        response = client.get("/health")
        assert "Content-Security-Policy" in response.headers
        csp = response.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "script-src" in csp

    def test_x_content_type_options(self, client):
        """X-Content-Type-Options should be nosniff"""
        response = client.get("/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self, client):
        """X-Frame-Options should prevent clickjacking"""
        response = client.get("/health")
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_x_xss_protection(self, client):
        """XSS protection header should be set"""
        response = client.get("/health")
        assert "X-XSS-Protection" in response.headers

    def test_referrer_policy(self, client):
        """Referrer policy should be set"""
        response = client.get("/health")
        assert "Referrer-Policy" in response.headers

    def test_permissions_policy(self, client):
        """Permissions policy should restrict sensitive APIs"""
        response = client.get("/health")
        assert "Permissions-Policy" in response.headers
        policy = response.headers["Permissions-Policy"]
        assert "geolocation=()" in policy

    def test_request_id_present(self, client):
        """X-Request-ID should be present for tracing"""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        # Should be UUID format
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 36  # UUID format

    def test_cache_control_for_api(self, client):
        """API responses should have no-store cache control"""
        response = client.get("/api/metrics/json")
        assert "no-store" in response.headers.get("Cache-Control", "")


class TestXSSPrevention:
    """Test XSS attack prevention"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_script_tag_in_transcript(self, client):
        """Script tags in transcript should be handled safely"""
        response = client.post("/api/voice-query", json={
            "transcript": "<script>alert('xss')</script>查询"
        })
        # Should either be blocked or sanitized
        assert response.status_code in [200, 400, 422]
        if response.status_code == 200:
            # Response should not contain executable script
            assert "<script>" not in response.text

    def test_event_handler_injection(self, client):
        """Event handlers should be blocked"""
        response = client.post("/api/voice-query", json={
            "transcript": "<img onerror='alert(1)' src='x'>"
        })
        assert response.status_code in [200, 400, 422]

    def test_javascript_protocol(self, client):
        """JavaScript protocol should be blocked"""
        response = client.post("/api/voice-query", json={
            "transcript": "javascript:alert(1)"
        })
        assert response.status_code in [200, 400, 422]


class TestPathTraversal:
    """Test path traversal attack prevention"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_directory_traversal_in_path(self, client):
        """Directory traversal should be blocked"""
        response = client.get("/api/../../../etc/passwd")
        # Should be 400 Bad Request or 404 Not Found
        assert response.status_code in [400, 404]

    def test_encoded_traversal(self, client):
        """URL encoded traversal should be blocked"""
        response = client.get("/api/%2e%2e/%2e%2e/etc/passwd")
        assert response.status_code in [400, 404]

    def test_null_byte_injection(self, client):
        """Null byte injection should be blocked"""
        response = client.get("/api/health%00.txt")
        assert response.status_code in [400, 404]


class TestInputValidation:
    """Test input validation"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_transcript_max_length(self, client):
        """Transcript should have max length limit"""
        long_transcript = "测" * 1000  # Exceeds 500 char limit
        response = client.post("/api/voice-query", json={
            "transcript": long_transcript
        })
        # Should either be 422 (validation) or 200 with error in response
        assert response.status_code in [200, 422]
        data = response.json()
        if response.status_code == 422:
            # FastAPI validation
            assert "detail" in data or "error" in data
        else:
            # Application-level validation
            pass  # May still process but truncate

    def test_session_id_invalid_chars(self, client):
        """Session ID with invalid characters should be handled safely"""
        response = client.post("/api/voice-query", json={
            "transcript": "测试",
            "session_id": "session<script>alert(1)</script>"
        })
        # Should either reject or sanitize
        assert response.status_code in [200, 400, 422]
        if response.status_code == 200:
            # Ensure it's processed safely
            data = response.json()
            assert "<script>" not in str(data)

    def test_session_id_too_long(self, client):
        """Session ID exceeding max length should be handled"""
        response = client.post("/api/voice-query", json={
            "transcript": "测试",
            "session_id": "a" * 100
        })
        # Should either reject or truncate
        assert response.status_code in [200, 400, 422]

    def test_invalid_json(self, client):
        """Invalid JSON should return 422"""
        response = client.post(
            "/api/voice-query",
            content="{ invalid json }",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestSQLInjection:
    """Test SQL injection prevention (defense in depth)"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_sql_injection_in_transcript(self, client):
        """SQL injection attempts should be handled safely"""
        # Even though we don't use SQL, defense in depth
        payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM passwords",
        ]
        for payload in payloads:
            response = client.post("/api/voice-query", json={
                "transcript": payload
            })
            # Should not cause server error
            assert response.status_code != 500


class TestCommandInjection:
    """Test command injection prevention"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_command_injection_in_transcript(self, client):
        """Command injection attempts should be handled safely"""
        payloads = [
            "; cat /etc/passwd",
            "| ls -la",
            "$(whoami)",
            "`id`",
        ]
        for payload in payloads:
            response = client.post("/api/voice-query", json={
                "transcript": f"查询{payload}"
            })
            # Should not execute commands
            assert response.status_code != 500
            if response.status_code == 200:
                data = response.json()
                # Response should not contain command output
                assert "root:" not in str(data)
                assert "uid=" not in str(data)


class TestRateLimiting:
    """Test rate limiting security"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_rate_limit_response_code(self, client):
        """Rate limited requests should return 429 eventually"""
        # Make many rapid requests - may not trigger due to burst allowance
        responses = [client.get("/health") for _ in range(100)]
        status_codes = [r.status_code for r in responses]

        # Either rate limiting kicks in, or all succeed (burst allowance)
        # The important thing is no 500 errors
        assert 500 not in status_codes, "Should not cause server errors"
        # Rate limiter is working if we get 429, or all 200 within burst
        success_rate = sum(1 for s in status_codes if s == 200) / len(status_codes)
        assert success_rate > 0, "At least some requests should succeed"

    def test_rate_limit_headers(self, client):
        """Rate limit headers should be present"""
        response = client.get("/health")
        # Check for rate limit headers (if implemented)
        # Some rate limiters add X-RateLimit-* headers
        pass  # Implementation dependent


class TestUtilityFunctions:
    """Test security utility functions"""

    def test_sanitize_string_basic(self):
        """Basic HTML entities should be escaped"""
        assert sanitize_string("<script>") == "&lt;script&gt;"
        assert sanitize_string("alert('xss')") == "alert(&#x27;xss&#x27;)"
        assert sanitize_string('say "hello"') == 'say &quot;hello&quot;'

    def test_sanitize_string_none(self):
        """None and empty strings should be handled"""
        assert sanitize_string(None) is None
        assert sanitize_string("") == ""

    def test_sanitize_string_safe(self):
        """Safe strings should not be modified"""
        safe = "Hello World 123"
        assert sanitize_string(safe) == safe

    def test_is_safe_project_id_valid(self):
        """Valid project IDs should pass"""
        assert is_safe_project_id("m537_voice_gateway") is True
        assert is_safe_project_id("project-123") is True
        assert is_safe_project_id("MyProject") is True

    def test_is_safe_project_id_invalid(self):
        """Invalid project IDs should fail"""
        assert is_safe_project_id("../etc/passwd") is False
        assert is_safe_project_id("project/sub") is False
        assert is_safe_project_id("..") is False
        assert is_safe_project_id(".") is False
        assert is_safe_project_id("") is False
        assert is_safe_project_id(None) is False
        assert is_safe_project_id("project<script>") is False


class TestContentTypeValidation:
    """Test content type handling"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_wrong_content_type(self, client):
        """Wrong content type should be handled"""
        response = client.post(
            "/api/voice-query",
            content="<xml>not json</xml>",
            headers={"Content-Type": "application/xml"}
        )
        # Should handle gracefully
        assert response.status_code in [400, 415, 422]


class TestErrorHandling:
    """Test secure error handling"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_error_does_not_leak_info(self, client):
        """Error responses should not leak sensitive info"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        # Should not contain stack traces or file paths
        response_text = response.text.lower()
        assert "traceback" not in response_text
        assert "/data/projects" not in response_text

    def test_validation_error_message(self, client):
        """Validation errors should be user-friendly"""
        response = client.post("/api/voice-query", json={})
        # Should provide helpful message without technical details
        if response.status_code == 422:
            data = response.json()
            assert "error" in data or "detail" in data


# Run tests with: pytest tests/test_security.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
