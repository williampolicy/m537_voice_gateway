"""
M537 Voice Gateway - Health Check Routes
V5.3 compliant health check endpoints with deep health checks
"""
from fastapi import APIRouter, Query
from datetime import datetime, timezone
import os
import time
import asyncio
import psutil
from typing import Dict, Any

from settings import settings

router = APIRouter()

# Track startup time
_startup_time = time.time()


async def check_disk_space() -> Dict[str, Any]:
    """Check if disk space is adequate"""
    try:
        usage = psutil.disk_usage("/")
        healthy = usage.percent < 90
        return {
            "healthy": healthy,
            "percent_used": round(usage.percent, 1),
            "free_gb": round(usage.free / (1024**3), 2)
        }
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def check_memory() -> Dict[str, Any]:
    """Check if memory usage is acceptable"""
    try:
        mem = psutil.virtual_memory()
        healthy = mem.percent < 90
        return {
            "healthy": healthy,
            "percent_used": round(mem.percent, 1),
            "available_gb": round(mem.available / (1024**3), 2)
        }
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def check_cpu() -> Dict[str, Any]:
    """Check CPU load"""
    try:
        load_avg = psutil.getloadavg()
        cpu_count = psutil.cpu_count()
        # High load is when load average > cpu_count
        healthy = load_avg[0] < cpu_count * 2
        return {
            "healthy": healthy,
            "load_1m": round(load_avg[0], 2),
            "load_5m": round(load_avg[1], 2),
            "cpu_count": cpu_count
        }
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def check_projects_dir() -> Dict[str, Any]:
    """Check if projects directory is accessible"""
    path = settings.PROJECTS_BASE_PATH
    try:
        exists = os.path.exists(path)
        readable = os.access(path, os.R_OK) if exists else False
        project_count = len(os.listdir(path)) if readable else 0
        return {
            "healthy": exists and readable,
            "path": path,
            "readable": readable,
            "project_count": project_count
        }
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def check_services() -> Dict[str, Any]:
    """Check dependent services"""
    checks = {}

    # Check if Docker is available
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        checks["docker"] = result.returncode == 0
    except:
        checks["docker"] = False

    # Check if tmux is available
    try:
        import subprocess
        result = subprocess.run(
            ["tmux", "list-sessions"],
            capture_output=True,
            timeout=5
        )
        # tmux returns 1 when no sessions, 0 when sessions exist
        checks["tmux"] = result.returncode in [0, 1]
    except:
        checks["tmux"] = False

    return {
        "healthy": all(checks.values()),
        "services": checks
    }


@router.get("/health")
@router.get("/api/health")
async def health_check():
    """
    Health check endpoint (V5.3 required)
    Available at both /health and /api/health
    """
    uptime_seconds = int(time.time() - _startup_time)

    # Check if projects directory is accessible
    projects_accessible = os.path.exists(settings.PROJECTS_BASE_PATH)

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "project": f"{settings.PROJECT_ID}_{settings.PROJECT_NAME}",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "ecosystem": f"LIGHT HOPE {settings.ECOSYSTEM_VERSION}",
        "uptime_seconds": uptime_seconds,
        "checks": {
            "projects_dir_accessible": projects_accessible
        }
    }


@router.get("/api/health/deep")
async def deep_health_check(
    include_services: bool = Query(False, description="Include service checks (slower)")
):
    """
    Deep health check endpoint.
    Performs comprehensive system checks.
    """
    uptime_seconds = int(time.time() - _startup_time)

    # Run checks concurrently
    checks_to_run = [
        ("disk", check_disk_space()),
        ("memory", check_memory()),
        ("cpu", check_cpu()),
        ("projects_dir", check_projects_dir()),
    ]

    if include_services:
        checks_to_run.append(("services", check_services()))

    # Execute all checks
    results = await asyncio.gather(
        *[check for _, check in checks_to_run],
        return_exceptions=True
    )

    checks = {}
    all_healthy = True

    for (name, _), result in zip(checks_to_run, results):
        if isinstance(result, Exception):
            checks[name] = {"healthy": False, "error": str(result)}
            all_healthy = False
        else:
            checks[name] = result
            if not result.get("healthy", False):
                all_healthy = False

    # Overall status
    status = "healthy" if all_healthy else "degraded"

    return {
        "status": status,
        "version": settings.VERSION,
        "project": f"{settings.PROJECT_ID}_{settings.PROJECT_NAME}",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "ecosystem": f"LIGHT HOPE {settings.ECOSYSTEM_VERSION}",
        "uptime_seconds": uptime_seconds,
        "checks": checks
    }


@router.get("/api/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    Simple check that the service is running.
    """
    return {"status": "alive"}


@router.get("/api/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    Check if service is ready to accept traffic.
    """
    # Check critical dependencies
    projects_accessible = os.path.exists(settings.PROJECTS_BASE_PATH)

    if not projects_accessible:
        return {"status": "not_ready", "reason": "projects_dir_not_accessible"}

    return {"status": "ready"}


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
