"""
M537 Voice Gateway - API Tests
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_healthy(self):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_has_ecosystem_info(self):
        response = client.get("/health")
        data = response.json()
        assert "LIGHT HOPE" in data["ecosystem"]
        assert "V5.3" in data["ecosystem"]


class TestVersionEndpoint:
    """Test version endpoint"""

    def test_version_returns_200(self):
        response = client.get("/api/version")
        assert response.status_code == 200

    def test_version_has_project_info(self):
        response = client.get("/api/version")
        data = response.json()
        assert data["project_id"] == "m537"
        assert "version" in data


class TestVoiceQueryEndpoint:
    """Test voice query endpoint"""

    def test_voice_query_returns_200(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": "现在有多少个项目"}
        )
        assert response.status_code == 200

    def test_voice_query_returns_success_structure(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": "现在有多少个项目"}
        )
        data = response.json()
        assert "success" in data
        assert "timestamp" in data
        assert "request_id" in data

    def test_voice_query_recognizes_project_count(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": "现在有多少个项目"}
        )
        data = response.json()
        assert data["success"] == True
        assert data["data"]["intent"] == "count_projects"

    def test_voice_query_recognizes_system_status(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": "系统状态怎么样"}
        )
        data = response.json()
        assert data["success"] == True
        assert data["data"]["intent"] == "system_status"

    def test_voice_query_unrecognized_returns_suggestions(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": "今天天气怎么样"}
        )
        data = response.json()
        assert data["success"] == False
        assert "suggestions" in data["error"]

    def test_voice_query_empty_transcript_fails(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": ""}
        )
        assert response.status_code == 422  # Validation error

    def test_voice_query_sanitizes_dangerous_chars(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": "项目数量; rm -rf /"}
        )
        # Should still process normally, dangerous chars removed
        assert response.status_code == 200


class TestIntentParsing:
    """Test intent parsing"""

    def test_project_count_keywords(self):
        keywords = [
            "多少个项目",
            "项目数量",
            "一共有多少项目"
        ]
        for keyword in keywords:
            response = client.post(
                "/api/voice-query",
                json={"transcript": keyword}
            )
            data = response.json()
            assert data["success"] == True
            assert data["data"]["intent"] == "count_projects"

    def test_system_status_keywords(self):
        keywords = [
            "系统状态",
            "CPU使用率",
            "内存怎么样"
        ]
        for keyword in keywords:
            response = client.post(
                "/api/voice-query",
                json={"transcript": keyword}
            )
            data = response.json()
            assert data["success"] == True
            assert data["data"]["intent"] == "system_status"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
