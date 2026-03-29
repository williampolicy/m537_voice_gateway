"""
M537 Voice Gateway - Admin Routes
API endpoints for administration and API key management
"""
import os
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from auth import api_key_manager, get_api_key, APIKeyInfo, RATE_LIMIT_TIERS

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin authentication - require master key or specific admin key
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")


def verify_admin(request: Request):
    """Verify admin access"""
    admin_key = request.headers.get("X-Admin-Key", "")
    if not admin_key:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "ADMIN_KEY_REQUIRED", "message": "Admin key required"}}
        )
    if ADMIN_SECRET and admin_key != ADMIN_SECRET:
        raise HTTPException(
            status_code=403,
            detail={"error": {"code": "INVALID_ADMIN_KEY", "message": "Invalid admin key"}}
        )
    return True


# ==================== Request/Response Models ====================

class CreateKeyRequest(BaseModel):
    """Request to create a new API key"""
    name: str = Field(..., min_length=1, max_length=100, description="Key name")
    tier: str = Field(default="standard", description="Rate limit tier")
    expires_days: Optional[int] = Field(default=None, ge=1, le=365, description="Days until expiration")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class CreateKeyResponse(BaseModel):
    """Response with new API key"""
    success: bool
    key_id: str
    api_key: str  # Only returned once!
    name: str
    tier: str
    rate_limit: int
    expires_at: Optional[str]
    message: str


class KeyInfo(BaseModel):
    """API key info (without sensitive data)"""
    key_id: str
    name: str
    tier: str
    rate_limit: int
    created_at: str
    expires_at: Optional[str]
    enabled: bool


class KeyUsageStats(BaseModel):
    """API key usage statistics"""
    key_id: str
    requests_last_minute: int
    rate_limit: int
    tier: str
    usage_percent: float


# ==================== API Key Management Routes ====================

@router.get("/keys", response_model=List[KeyInfo])
async def list_api_keys(admin: bool = Depends(verify_admin)):
    """
    List all API keys.

    Returns a list of all registered API keys with their metadata.
    Does not include the actual key values.
    """
    keys = api_key_manager.list_keys()
    result = []
    for k in keys:
        result.append(KeyInfo(
            key_id=k["key_id"],
            name=k["name"],
            tier=k["tier"],
            rate_limit=RATE_LIMIT_TIERS.get(k["tier"], 60),
            created_at=k["created_at"],
            expires_at=k["expires_at"],
            enabled=k["enabled"]
        ))
    return result


@router.post("/keys", response_model=CreateKeyResponse)
async def create_api_key(
    request: CreateKeyRequest,
    admin: bool = Depends(verify_admin)
):
    """
    Create a new API key.

    **Important**: The API key is only returned once. Store it securely.

    Tiers:
    - free: 30 req/min
    - standard: 60 req/min
    - premium: 300 req/min
    - enterprise: 1000 req/min
    """
    if request.tier not in RATE_LIMIT_TIERS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_TIER",
                    "message": f"Invalid tier. Valid tiers: {list(RATE_LIMIT_TIERS.keys())}"
                }
            }
        )

    raw_key, key_info = api_key_manager.generate_key(
        name=request.name,
        tier=request.tier,
        expires_days=request.expires_days,
        metadata=request.metadata
    )

    return CreateKeyResponse(
        success=True,
        key_id=key_info.key_id,
        api_key=raw_key,
        name=key_info.name,
        tier=key_info.tier,
        rate_limit=key_info.rate_limit,
        expires_at=key_info.expires_at.isoformat() if key_info.expires_at else None,
        message="API key created successfully. Store the key securely - it cannot be retrieved later."
    )


@router.get("/keys/{key_id}")
async def get_api_key_info(
    key_id: str,
    admin: bool = Depends(verify_admin)
):
    """Get details for a specific API key"""
    keys = api_key_manager.list_keys()
    for k in keys:
        if k["key_id"] == key_id:
            return KeyInfo(
                key_id=k["key_id"],
                name=k["name"],
                tier=k["tier"],
                rate_limit=RATE_LIMIT_TIERS.get(k["tier"], 60),
                created_at=k["created_at"],
                expires_at=k["expires_at"],
                enabled=k["enabled"]
            )

    raise HTTPException(
        status_code=404,
        detail={"error": {"code": "KEY_NOT_FOUND", "message": "API key not found"}}
    )


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    admin: bool = Depends(verify_admin)
):
    """
    Revoke an API key.

    The key will be disabled immediately. This action cannot be undone.
    """
    if api_key_manager.revoke_key(key_id):
        return {
            "success": True,
            "message": f"API key {key_id} has been revoked"
        }

    raise HTTPException(
        status_code=404,
        detail={"error": {"code": "KEY_NOT_FOUND", "message": "API key not found"}}
    )


@router.get("/keys/{key_id}/usage", response_model=KeyUsageStats)
async def get_key_usage(
    key_id: str,
    admin: bool = Depends(verify_admin)
):
    """Get usage statistics for an API key"""
    stats = api_key_manager.get_usage_stats(key_id)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "KEY_NOT_FOUND", "message": "API key not found"}}
        )

    usage_percent = (stats["requests_last_minute"] / stats["rate_limit"]) * 100

    return KeyUsageStats(
        key_id=stats["key_id"],
        requests_last_minute=stats["requests_last_minute"],
        rate_limit=stats["rate_limit"],
        tier=stats["tier"],
        usage_percent=round(usage_percent, 2)
    )


# ==================== System Administration Routes ====================

@router.get("/tiers")
async def list_rate_limit_tiers():
    """List available rate limit tiers"""
    return {
        "tiers": [
            {"name": name, "requests_per_minute": limit}
            for name, limit in RATE_LIMIT_TIERS.items()
            if name != "unlimited"
        ]
    }


@router.get("/stats")
async def get_system_stats(admin: bool = Depends(verify_admin)):
    """Get system-wide statistics"""
    keys = api_key_manager.list_keys()

    enabled_keys = sum(1 for k in keys if k["enabled"])
    tier_distribution = {}
    for k in keys:
        tier = k["tier"]
        tier_distribution[tier] = tier_distribution.get(tier, 0) + 1

    return {
        "total_keys": len(keys),
        "enabled_keys": enabled_keys,
        "disabled_keys": len(keys) - enabled_keys,
        "tier_distribution": tier_distribution,
        "available_tiers": list(RATE_LIMIT_TIERS.keys())
    }


@router.post("/cache/clear")
async def clear_cache(admin: bool = Depends(verify_admin)):
    """Clear all caches"""
    from services.cache import query_cache
    query_cache.clear()

    return {
        "success": True,
        "message": "Cache cleared successfully"
    }


@router.post("/analytics/reset")
async def reset_analytics(admin: bool = Depends(verify_admin)):
    """Reset all analytics data"""
    from analytics import analytics
    analytics.reset()

    return {
        "success": True,
        "message": "Analytics data reset successfully"
    }
