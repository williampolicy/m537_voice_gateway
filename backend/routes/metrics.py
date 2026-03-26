"""
M537 Voice Gateway - Prometheus Metrics Route
V5.3 推荐的监控指标端点
"""
from fastapi import APIRouter, Response
from datetime import datetime, timezone
from collections import defaultdict
import time
import threading

from middleware import rate_limit_state

router = APIRouter()


class MetricsCollector:
    """Thread-safe metrics collector with histogram support"""

    def __init__(self):
        self._lock = threading.Lock()
        self.start_time = time.time()

        # Request counters
        self.requests_total = {"success": 0, "error": 0}

        # Intent classification
        self.intents_total = defaultdict(int)
        self.intents_not_recognized = 0

        # Tool execution
        self.tools_total = defaultdict(int)
        self.tools_errors = defaultdict(int)

        # Latency histogram buckets (in seconds)
        self.latency_buckets = [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        self.latency_counts = defaultdict(int)  # bucket -> count
        self.latency_sum = 0.0
        self.latency_count = 0

        # LLM fallback usage
        self.llm_fallback_total = 0
        self.llm_fallback_success = 0

    def record_request(self, success: bool, duration: float, intent: str = None, tool: str = None):
        """Record a request with all metrics"""
        with self._lock:
            # Basic counters
            if success:
                self.requests_total["success"] += 1
            else:
                self.requests_total["error"] += 1

            # Intent tracking
            if intent:
                self.intents_total[intent] += 1
            else:
                self.intents_not_recognized += 1

            # Tool tracking
            if tool:
                self.tools_total[tool] += 1

            # Latency histogram (record in the smallest fitting bucket)
            self.latency_sum += duration
            self.latency_count += 1
            for bucket in self.latency_buckets:
                if duration <= bucket:
                    self.latency_counts[bucket] += 1
                    break  # Only record in the first matching bucket

    def record_tool_error(self, tool: str):
        """Record a tool execution error"""
        with self._lock:
            self.tools_errors[tool] += 1

    def record_llm_fallback(self, success: bool):
        """Record LLM fallback usage"""
        with self._lock:
            self.llm_fallback_total += 1
            if success:
                self.llm_fallback_success += 1

    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus format metrics"""
        with self._lock:
            uptime = time.time() - self.start_time
            rl_metrics = rate_limit_state.get_metrics()

            lines = []

            # Request totals
            lines.append("# HELP m537_requests_total Total number of voice queries")
            lines.append("# TYPE m537_requests_total counter")
            lines.append(f'm537_requests_total{{status="success"}} {self.requests_total["success"]}')
            lines.append(f'm537_requests_total{{status="error"}} {self.requests_total["error"]}')
            lines.append("")

            # Intent classification
            lines.append("# HELP m537_intents_total Total intents classified by type")
            lines.append("# TYPE m537_intents_total counter")
            for intent, count in self.intents_total.items():
                lines.append(f'm537_intents_total{{intent="{intent}"}} {count}')
            lines.append(f'm537_intents_total{{intent="not_recognized"}} {self.intents_not_recognized}')
            lines.append("")

            # Tool execution
            lines.append("# HELP m537_tools_total Total tool executions by tool")
            lines.append("# TYPE m537_tools_total counter")
            for tool, count in self.tools_total.items():
                lines.append(f'm537_tools_total{{tool="{tool}"}} {count}')
            lines.append("")

            # Tool errors
            if self.tools_errors:
                lines.append("# HELP m537_tools_errors_total Tool execution errors by tool")
                lines.append("# TYPE m537_tools_errors_total counter")
                for tool, count in self.tools_errors.items():
                    lines.append(f'm537_tools_errors_total{{tool="{tool}"}} {count}')
                lines.append("")

            # Request latency histogram
            lines.append("# HELP m537_request_duration_seconds Request duration histogram")
            lines.append("# TYPE m537_request_duration_seconds histogram")
            cumulative = 0
            for bucket in self.latency_buckets:
                cumulative += self.latency_counts.get(bucket, 0)
                lines.append(f'm537_request_duration_seconds_bucket{{le="{bucket}"}} {cumulative}')
            lines.append(f'm537_request_duration_seconds_bucket{{le="+Inf"}} {self.latency_count}')
            lines.append(f"m537_request_duration_seconds_sum {self.latency_sum:.4f}")
            lines.append(f"m537_request_duration_seconds_count {self.latency_count}")
            lines.append("")

            # Uptime
            lines.append("# HELP m537_uptime_seconds Service uptime in seconds")
            lines.append("# TYPE m537_uptime_seconds gauge")
            lines.append(f"m537_uptime_seconds {uptime:.0f}")
            lines.append("")

            # Rate limiting
            lines.append("# HELP m537_rate_limit_total Total requests checked by rate limiter")
            lines.append("# TYPE m537_rate_limit_total counter")
            lines.append(f'm537_rate_limit_total {rl_metrics["total_requests"]}')
            lines.append("")

            lines.append("# HELP m537_rate_limit_blocked Requests blocked by rate limiter")
            lines.append("# TYPE m537_rate_limit_blocked counter")
            lines.append(f'm537_rate_limit_blocked {rl_metrics["blocked_requests"]}')
            lines.append("")

            lines.append("# HELP m537_rate_limit_active_clients Number of active rate limit clients")
            lines.append("# TYPE m537_rate_limit_active_clients gauge")
            lines.append(f'm537_rate_limit_active_clients {rl_metrics["active_clients"]}')
            lines.append("")

            # LLM fallback
            lines.append("# HELP m537_llm_fallback_total LLM fallback attempts")
            lines.append("# TYPE m537_llm_fallback_total counter")
            lines.append(f'm537_llm_fallback_total{{status="success"}} {self.llm_fallback_success}')
            lines.append(f'm537_llm_fallback_total{{status="failed"}} {self.llm_fallback_total - self.llm_fallback_success}')
            lines.append("")

            # Service info
            lines.append("# HELP m537_info Service information")
            lines.append("# TYPE m537_info gauge")
            lines.append('m537_info{version="1.0.0",ecosystem="LIGHT_HOPE_V5.3"} 1')

            return "\n".join(lines)

    def get_json_metrics(self) -> dict:
        """Get metrics as JSON"""
        with self._lock:
            uptime = time.time() - self.start_time
            avg_latency = self.latency_sum / self.latency_count if self.latency_count > 0 else 0

            return {
                "requests": {
                    "success": self.requests_total["success"],
                    "error": self.requests_total["error"],
                    "total": self.requests_total["success"] + self.requests_total["error"]
                },
                "intents": dict(self.intents_total),
                "tools": dict(self.tools_total),
                "performance": {
                    "avg_latency_ms": round(avg_latency * 1000, 2),
                    "uptime_seconds": round(uptime, 0)
                },
                "llm_fallback": {
                    "total": self.llm_fallback_total,
                    "success": self.llm_fallback_success
                },
                "version": "1.0.0",
                "ecosystem": "LIGHT HOPE V5.3",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }


# Global metrics collector
metrics_collector = MetricsCollector()


def record_request(success: bool, duration: float, intent: str = None, tool: str = None):
    """记录请求指标 (兼容旧接口)"""
    metrics_collector.record_request(success, duration, intent, tool)


@router.get("/metrics")
async def metrics():
    """
    返回 Prometheus 格式的监控指标

    包含：
    - 请求总数 (按状态和意图分)
    - 请求延迟直方图
    - 工具执行计数
    - 速率限制状态
    - LLM 回退统计
    - 服务运行时间
    """
    return Response(
        content=metrics_collector.get_prometheus_metrics(),
        media_type="text/plain; charset=utf-8"
    )


@router.get("/metrics/json")
async def metrics_json():
    """
    返回 JSON 格式的监控指标 (便于前端展示)
    """
    return metrics_collector.get_json_metrics()
