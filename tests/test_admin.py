"""
Tests for Admin API routes
"""
import pytest
import os
from fastapi.testclient import TestClient

# Set admin secret for testing
os.environ["ADMIN_SECRET"] = "test-admin-secret"

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

client = TestClient(app)

ADMIN_HEADERS = {"X-Admin-Key": "test-admin-secret"}


class TestAdminAuth:
    """Test admin authentication"""

    def test_list_keys_requires_admin(self):
        """List keys without admin key should fail"""
        response = client.get("/api/admin/keys")
        assert response.status_code == 401
        assert "ADMIN_KEY_REQUIRED" in response.text

    def test_list_keys_with_invalid_admin_key(self):
        """List keys with invalid admin key should fail"""
        response = client.get(
            "/api/admin/keys",
            headers={"X-Admin-Key": "invalid-key"}
        )
        assert response.status_code == 403

    def test_list_keys_with_valid_admin_key(self):
        """List keys with valid admin key should succeed"""
        response = client.get("/api/admin/keys", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAPIKeyManagement:
    """Test API key CRUD operations"""

    def test_create_api_key(self):
        """Create a new API key"""
        response = client.post(
            "/api/admin/keys",
            headers=ADMIN_HEADERS,
            json={
                "name": "Test Key",
                "tier": "standard"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "api_key" in data
        assert data["api_key"].startswith("m537_")
        assert data["tier"] == "standard"
        assert data["rate_limit"] == 60

    def test_create_api_key_with_expiration(self):
        """Create API key with expiration"""
        response = client.post(
            "/api/admin/keys",
            headers=ADMIN_HEADERS,
            json={
                "name": "Expiring Key",
                "tier": "free",
                "expires_days": 30
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expires_at"] is not None

    def test_create_api_key_invalid_tier(self):
        """Create API key with invalid tier should fail"""
        response = client.post(
            "/api/admin/keys",
            headers=ADMIN_HEADERS,
            json={
                "name": "Invalid Key",
                "tier": "super-premium"
            }
        )
        assert response.status_code == 400
        assert "INVALID_TIER" in response.text

    def test_list_api_keys(self):
        """List all API keys"""
        # Create a key first
        client.post(
            "/api/admin/keys",
            headers=ADMIN_HEADERS,
            json={"name": "List Test Key", "tier": "standard"}
        )

        response = client.get("/api/admin/keys", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        keys = response.json()
        assert isinstance(keys, list)
        assert len(keys) > 0

    def test_get_api_key_info(self):
        """Get specific API key info"""
        # Create a key first
        create_response = client.post(
            "/api/admin/keys",
            headers=ADMIN_HEADERS,
            json={"name": "Info Test Key", "tier": "premium"}
        )
        key_id = create_response.json()["key_id"]

        response = client.get(f"/api/admin/keys/{key_id}", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["key_id"] == key_id
        assert data["tier"] == "premium"

    def test_get_nonexistent_key(self):
        """Get nonexistent key should return 404"""
        response = client.get(
            "/api/admin/keys/nonexistent-key",
            headers=ADMIN_HEADERS
        )
        assert response.status_code == 404

    def test_revoke_api_key(self):
        """Revoke an API key"""
        # Create a key first
        create_response = client.post(
            "/api/admin/keys",
            headers=ADMIN_HEADERS,
            json={"name": "Revoke Test Key", "tier": "standard"}
        )
        key_id = create_response.json()["key_id"]

        # Revoke it
        response = client.delete(
            f"/api/admin/keys/{key_id}",
            headers=ADMIN_HEADERS
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify it's disabled
        info_response = client.get(
            f"/api/admin/keys/{key_id}",
            headers=ADMIN_HEADERS
        )
        assert info_response.json()["enabled"] is False

    def test_revoke_nonexistent_key(self):
        """Revoke nonexistent key should return 404"""
        response = client.delete(
            "/api/admin/keys/nonexistent-key",
            headers=ADMIN_HEADERS
        )
        assert response.status_code == 404

    def test_get_key_usage(self):
        """Get API key usage statistics"""
        # Create a key
        create_response = client.post(
            "/api/admin/keys",
            headers=ADMIN_HEADERS,
            json={"name": "Usage Test Key", "tier": "standard"}
        )
        key_id = create_response.json()["key_id"]

        response = client.get(
            f"/api/admin/keys/{key_id}/usage",
            headers=ADMIN_HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert "requests_last_minute" in data
        assert "rate_limit" in data
        assert "usage_percent" in data


class TestAdminRateLimitTiers:
    """Test rate limit tier management"""

    def test_list_tiers(self):
        """List available rate limit tiers"""
        response = client.get("/api/admin/tiers")
        assert response.status_code == 200
        data = response.json()
        assert "tiers" in data
        tiers = data["tiers"]
        assert len(tiers) > 0

        # Check standard tier exists
        tier_names = [t["name"] for t in tiers]
        assert "free" in tier_names
        assert "standard" in tier_names
        assert "premium" in tier_names
        assert "enterprise" in tier_names


class TestAdminSystemStats:
    """Test system statistics"""

    def test_get_system_stats(self):
        """Get system statistics"""
        response = client.get("/api/admin/stats", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "total_keys" in data
        assert "enabled_keys" in data
        assert "tier_distribution" in data


class TestAdminCacheOperations:
    """Test cache operations"""

    def test_clear_cache(self):
        """Clear cache"""
        response = client.post("/api/admin/cache/clear", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_clear_cache_requires_admin(self):
        """Clear cache requires admin key"""
        response = client.post("/api/admin/cache/clear")
        assert response.status_code == 401


class TestAdminAnalyticsOperations:
    """Test analytics operations"""

    def test_reset_analytics(self):
        """Reset analytics"""
        response = client.post("/api/admin/analytics/reset", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_reset_analytics_requires_admin(self):
        """Reset analytics requires admin key"""
        response = client.post("/api/admin/analytics/reset")
        assert response.status_code == 401
