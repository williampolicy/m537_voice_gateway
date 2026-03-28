"""
M537 Voice Gateway - Analytics Routes
API endpoints for usage analytics
"""
from fastapi import APIRouter, Query
from typing import Optional

from analytics import analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def get_analytics_summary():
    """
    Get analytics summary for the retention period.

    Returns aggregated metrics including:
    - Total and successful queries
    - Cache hit rate
    - Performance percentiles
    - Top intents
    - Language distribution
    """
    return analytics.get_summary()


@router.get("/trend")
async def get_hourly_trend(
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours (max 168)")
):
    """
    Get hourly query trend.

    Returns query counts per hour for the specified period.
    """
    return {
        "period_hours": hours,
        "trend": analytics.get_hourly_trend(hours)
    }


@router.get("/intents")
async def get_intent_breakdown():
    """
    Get detailed intent breakdown.

    Returns all intents with their counts and percentages.
    """
    return analytics.get_intent_breakdown()


@router.get("/errors")
async def get_error_breakdown():
    """
    Get error breakdown.

    Returns error codes with their counts.
    """
    return analytics.get_error_breakdown()


@router.get("/performance")
async def get_performance_stats():
    """
    Get detailed performance statistics.

    Returns latency percentiles and distribution.
    """
    return analytics.get_performance_stats()


@router.post("/reset")
async def reset_analytics():
    """
    Reset all analytics data.

    WARNING: This will clear all collected metrics.
    """
    analytics.reset()
    return {"success": True, "message": "Analytics data reset"}
