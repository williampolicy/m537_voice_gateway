"""
M537 Voice Gateway - API v1 Tests
Tests for versioned API endpoints
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient


class TestVoiceQueryV1:
    """Tests for /api/v1/voice-query endpoint"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_voice_query_success(self, client):
        """Test successful voice query"""
        response = client.post("/api/v1/voice-query", json={
            "transcript": "有多少个项目"
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "request_id" in data
        assert data["api_version"] == "v1"

    def test_voice_query_with_language(self, client):
        """Test voice query with language parameter"""
        response = client.post(
            "/api/v1/voice-query",
            json={
                "transcript": "system status",
                "language": "en-US"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["api_version"] == "v1"

    def test_voice_query_with_session(self, client):
        """Test voice query with session ID"""
        response = client.post("/api/v1/voice-query", json={
            "transcript": "有多少个项目",
            "session_id": "test-session-123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["api_version"] == "v1"

    def test_voice_query_with_include_raw(self, client):
        """Test voice query with raw data included"""
        response = client.post("/api/v1/voice-query", json={
            "transcript": "系统状态",
            "include_raw": True
        })
        assert response.status_code == 200
        data = response.json()
        if data.get("success"):
            # raw_data should be present when requested
            assert data["data"] is not None

    def test_voice_query_invalid_transcript(self, client):
        """Test with empty transcript"""
        response = client.post("/api/v1/voice-query", json={
            "transcript": ""
        })
        assert response.status_code == 422

    def test_voice_query_accept_language_header(self, client):
        """Test Accept-Language header detection"""
        response = client.post(
            "/api/v1/voice-query",
            json={"transcript": "status"},
            headers={"Accept-Language": "ja-JP"}
        )
        assert response.status_code == 200

    def test_voice_query_request_id_header(self, client):
        """Test X-Request-ID header passthrough"""
        custom_id = "my-custom-request-id"
        response = client.post(
            "/api/v1/voice-query",
            json={"transcript": "测试"},
            headers={"X-Request-ID": custom_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == custom_id


class TestHealthV1:
    """Tests for /api/v1/health endpoint"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_health_check(self, client):
        """Test health check returns detailed info"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["api_version"] == "v1"
        assert "checks" in data
        assert isinstance(data["checks"], list)

    def test_health_check_includes_cpu(self, client):
        """Test health check includes CPU check"""
        response = client.get("/api/v1/health")
        data = response.json()
        check_names = [c["name"] for c in data["checks"]]
        assert "cpu" in check_names

    def test_health_check_includes_memory(self, client):
        """Test health check includes memory check"""
        response = client.get("/api/v1/health")
        data = response.json()
        check_names = [c["name"] for c in data["checks"]]
        assert "memory" in check_names

    def test_health_check_includes_disk(self, client):
        """Test health check includes disk check"""
        response = client.get("/api/v1/health")
        data = response.json()
        check_names = [c["name"] for c in data["checks"]]
        assert "disk" in check_names

    def test_health_summary(self, client):
        """Test quick health summary"""
        response = client.get("/api/v1/health/summary")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime_seconds" in data

    def test_health_check_latency(self, client):
        """Test health check includes latency info"""
        response = client.get("/api/v1/health")
        data = response.json()
        for check in data["checks"]:
            assert "latency_ms" in check
            assert check["latency_ms"] >= 0


class TestScheduler:
    """Tests for background scheduler"""

    def test_scheduler_initialization(self):
        """Test scheduler initializes correctly"""
        from services.scheduler import scheduler
        stats = scheduler.get_stats()
        assert "task_count" in stats
        assert stats["task_count"] > 0

    def test_scheduler_has_cleanup_tasks(self):
        """Test scheduler has cleanup tasks registered"""
        from services.scheduler import scheduler
        stats = scheduler.get_stats()
        task_names = list(stats["tasks"].keys())
        assert "cleanup_expired_cache" in task_names
        assert "cleanup_expired_sessions" in task_names

    def test_scheduler_task_intervals(self):
        """Test task intervals are set correctly"""
        from services.scheduler import scheduler
        stats = scheduler.get_stats()

        # Cache cleanup every 5 minutes
        assert stats["tasks"]["cleanup_expired_cache"]["interval_seconds"] == 300

        # Session cleanup every 10 minutes
        assert stats["tasks"]["cleanup_expired_sessions"]["interval_seconds"] == 600


# Run tests with: pytest tests/test_v1_api.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
