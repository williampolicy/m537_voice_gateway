"""
M537 Voice Gateway - Prometheus Metrics Route
V5.3 推荐的监控指标端点
"""
from fastapi import APIRouter, Response
from datetime import datetime
import time

router = APIRouter()

# 简单的内存计数器 (生产环境应使用 prometheus_client)
_metrics = {
    "requests_total": {"success": 0, "error": 0},
    "request_duration_sum": 0.0,
    "request_count": 0,
    "start_time": time.time(),
}


def record_request(success: bool, duration: float):
    """记录请求指标"""
    if success:
        _metrics["requests_total"]["success"] += 1
    else:
        _metrics["requests_total"]["error"] += 1
    _metrics["request_duration_sum"] += duration
    _metrics["request_count"] += 1


@router.get("/metrics")
async def metrics():
    """
    返回 Prometheus 格式的监控指标

    包含：
    - 请求总数 (按状态分)
    - 请求平均耗时
    - 服务运行时间
    """
    uptime = time.time() - _metrics["start_time"]
    avg_duration = (
        _metrics["request_duration_sum"] / _metrics["request_count"]
        if _metrics["request_count"] > 0
        else 0
    )

    metrics_text = f"""# HELP m537_requests_total Total number of voice queries
# TYPE m537_requests_total counter
m537_requests_total{{status="success"}} {_metrics["requests_total"]["success"]}
m537_requests_total{{status="error"}} {_metrics["requests_total"]["error"]}

# HELP m537_request_duration_seconds Average request duration in seconds
# TYPE m537_request_duration_seconds gauge
m537_request_duration_seconds {avg_duration:.4f}

# HELP m537_uptime_seconds Service uptime in seconds
# TYPE m537_uptime_seconds gauge
m537_uptime_seconds {uptime:.0f}

# HELP m537_info Service information
# TYPE m537_info gauge
m537_info{{version="1.0.0",ecosystem="LIGHT_HOPE_V5.3"}} 1
"""

    return Response(
        content=metrics_text,
        media_type="text/plain; charset=utf-8"
    )


@router.get("/metrics/json")
async def metrics_json():
    """
    返回 JSON 格式的监控指标 (便于前端展示)
    """
    uptime = time.time() - _metrics["start_time"]
    avg_duration = (
        _metrics["request_duration_sum"] / _metrics["request_count"]
        if _metrics["request_count"] > 0
        else 0
    )

    return {
        "requests": {
            "success": _metrics["requests_total"]["success"],
            "error": _metrics["requests_total"]["error"],
            "total": _metrics["request_count"]
        },
        "performance": {
            "avg_duration_ms": round(avg_duration * 1000, 2),
            "uptime_seconds": round(uptime, 0)
        },
        "version": "1.0.0",
        "ecosystem": "LIGHT HOPE V5.3",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
