"""
M537 Voice Gateway - Health Check Routes
V5.3 compliant health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
import os
import time

from settings import settings

router = APIRouter()

# Track startup time
_startup_time = time.time()


@router.get("/health")
async def health_check():
    """
    Health check endpoint (V5.3 required)
    """
    uptime_seconds = int(time.time() - _startup_time)

    # Check if projects directory is accessible
    projects_accessible = os.path.exists(settings.PROJECTS_BASE_PATH)

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "project": f"{settings.PROJECT_ID}_{settings.PROJECT_NAME}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ecosystem": f"LIGHT HOPE {settings.ECOSYSTEM_VERSION}",
        "uptime_seconds": uptime_seconds,
        "checks": {
            "projects_dir_accessible": projects_accessible
        }
    }


@router.get("/api/version")
async def get_version():
    """
    Version information endpoint
    """
    return {
        "project_id": settings.PROJECT_ID,
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ecosystem_version": settings.ECOSYSTEM_VERSION
    }


# Note: Metrics endpoint moved to routes/metrics.py for V5.3 Prometheus compatibility
