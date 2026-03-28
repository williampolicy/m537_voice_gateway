"""
M537 Voice Gateway - Health Check API v1
Enhanced health check with detailed diagnostics
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import time
import asyncio
import psutil
import os

from settings import settings

router = APIRouter()

# Track startup time
_startup_time = time.time()


class HealthCheck(BaseModel):
    """Health check result"""
    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: float
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health response model"""
    status: str
    version: str
    api_version: str = "v1"
    timestamp: str
    uptime_seconds: int
    checks: List[HealthCheck]


async def check_with_timeout(name: str, check_func, timeout: float = 5.0) -> HealthCheck:
    """Run a health check with timeout"""
    start = time.perf_counter()
    try:
        result = await asyncio.wait_for(check_func(), timeout=timeout)
        latency = (time.perf_counter() - start) * 1000
        return HealthCheck(
            name=name,
            status="healthy" if result.get("healthy") else "degraded",
            latency_ms=round(latency, 2),
            details=result
        )
    except asyncio.TimeoutError:
        return HealthCheck(
            name=name,
            status="unhealthy",
            latency_ms=timeout * 1000,
            details={"error": "timeout"}
        )
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return HealthCheck(
            name=name,
            status="unhealthy",
            latency_ms=round(latency, 2),
            details={"error": str(e)}
        )


async def check_cpu() -> Dict[str, Any]:
    """Check CPU health"""
    load = psutil.getloadavg()
    cpu_count = psutil.cpu_count()
    healthy = load[0] < cpu_count * 2
    return {
        "healthy": healthy,
        "load_1m": round(load[0], 2),
        "load_5m": round(load[1], 2),
        "load_15m": round(load[2], 2),
        "cpu_count": cpu_count,
        "percent": round(psutil.cpu_percent(interval=0.1), 1)
    }


async def check_memory() -> Dict[str, Any]:
    """Check memory health"""
    mem = psutil.virtual_memory()
    healthy = mem.percent < 90
    return {
        "healthy": healthy,
        "percent": round(mem.percent, 1),
        "total_gb": round(mem.total / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "used_gb": round(mem.used / (1024**3), 2)
    }


async def check_disk() -> Dict[str, Any]:
    """Check disk health"""
    usage = psutil.disk_usage("/")
    healthy = usage.percent < 90
    return {
        "healthy": healthy,
        "percent": round(usage.percent, 1),
        "total_gb": round(usage.total / (1024**3), 2),
        "free_gb": round(usage.free / (1024**3), 2),
        "used_gb": round(usage.used / (1024**3), 2)
    }


async def check_projects_dir() -> Dict[str, Any]:
    """Check projects directory"""
    path = settings.PROJECTS_BASE_PATH
    exists = os.path.exists(path)
    readable = os.access(path, os.R_OK) if exists else False

    if readable:
        try:
            count = len([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
        except:
            count = 0
    else:
        count = 0

    return {
        "healthy": exists and readable,
        "path": path,
        "exists": exists,
        "readable": readable,
        "project_count": count
    }


async def check_network() -> Dict[str, Any]:
    """Check network connectivity"""
    try:
        connections = len(psutil.net_connections(kind='inet'))
        return {
            "healthy": True,
            "active_connections": connections
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e)
        }


@router.get("/health", response_model=HealthResponse)
async def health_v1():
    """
    Enhanced health check (v1).

    Returns detailed health status with individual check results.
    """
    uptime = int(time.time() - _startup_time)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Run all checks concurrently
    checks = await asyncio.gather(
        check_with_timeout("cpu", check_cpu),
        check_with_timeout("memory", check_memory),
        check_with_timeout("disk", check_disk),
        check_with_timeout("projects_dir", check_projects_dir),
        check_with_timeout("network", check_network)
    )

    # Determine overall status
    unhealthy_count = sum(1 for c in checks if c.status == "unhealthy")
    degraded_count = sum(1 for c in checks if c.status == "degraded")

    if unhealthy_count > 0:
        status = "unhealthy"
    elif degraded_count > 0:
        status = "degraded"
    else:
        status = "healthy"

    return HealthResponse(
        status=status,
        version=settings.VERSION,
        timestamp=timestamp,
        uptime_seconds=uptime,
        checks=list(checks)
    )


@router.get("/health/summary")
async def health_summary():
    """Quick health summary"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "uptime_seconds": int(time.time() - _startup_time)
    }
