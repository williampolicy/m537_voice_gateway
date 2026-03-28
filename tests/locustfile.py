"""
M537 Voice Gateway - Load Testing with Locust
Run: locust -f tests/locustfile.py --host=http://localhost:5537
"""
from locust import HttpUser, task, between, events
import json
import random


class M537User(HttpUser):
    """Simulates a typical user interacting with M537 Voice Gateway"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    # Test queries in different languages
    queries_zh = [
        "有多少个项目",
        "系统状态怎么样",
        "最近有什么错误",
        "P0服务状态如何",
        "当前有哪些端口在监听",
        "最近更新了什么",
        "系统健康状况",
    ]

    queries_en = [
        "how many projects",
        "system status",
        "recent errors",
        "P0 service status",
        "listening ports",
    ]

    def on_start(self):
        """Called when a simulated user starts"""
        # Verify server is healthy before starting tests
        response = self.client.get("/api/v1/health/summary")
        if response.status_code != 200:
            raise Exception("Server not healthy")

    @task(10)
    def voice_query_zh(self):
        """Test Chinese voice queries (most common)"""
        query = random.choice(self.queries_zh)
        self.client.post(
            "/api/v1/voice-query",
            json={"transcript": query, "language": "zh-CN"},
            headers={"Content-Type": "application/json"}
        )

    @task(3)
    def voice_query_en(self):
        """Test English voice queries"""
        query = random.choice(self.queries_en)
        self.client.post(
            "/api/v1/voice-query",
            json={"transcript": query, "language": "en-US"},
            headers={"Content-Type": "application/json"}
        )

    @task(5)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/api/v1/health")

    @task(3)
    def health_summary(self):
        """Test quick health summary"""
        self.client.get("/api/v1/health/summary")

    @task(2)
    def metrics(self):
        """Test metrics endpoint"""
        self.client.get("/api/metrics/json")

    @task(1)
    def voice_query_with_session(self):
        """Test voice query with session tracking"""
        session_id = f"load-test-{random.randint(1000, 9999)}"
        self.client.post(
            "/api/v1/voice-query",
            json={
                "transcript": "测试会话查询",
                "session_id": session_id,
                "language": "zh-CN"
            },
            headers={"Content-Type": "application/json"}
        )


class M537AdminUser(HttpUser):
    """Simulates admin/monitoring traffic"""

    wait_time = between(5, 10)
    weight = 1  # Less frequent than regular users

    @task
    def deep_health_check(self):
        """Test deep health check (admin monitoring)"""
        self.client.get("/api/health/deep")

    @task
    def liveness_check(self):
        """Test Kubernetes liveness probe"""
        self.client.get("/api/health/live")

    @task
    def readiness_check(self):
        """Test Kubernetes readiness probe"""
        self.client.get("/api/health/ready")

    @task
    def get_metrics(self):
        """Get detailed metrics"""
        self.client.get("/api/metrics/json")


class M537WebSocketUser(HttpUser):
    """Simulates WebSocket connection (as HTTP fallback)"""

    wait_time = between(10, 30)
    weight = 1

    @task
    def subscribe_status(self):
        """Simulate status subscription via polling"""
        self.client.get("/api/v1/health/summary")


# Custom event handlers for reporting
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log slow requests"""
    if response_time > 1000:  # > 1 second
        print(f"SLOW: {request_type} {name} took {response_time}ms")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary when test stops"""
    print("\n" + "=" * 50)
    print("Load Test Complete")
    print("=" * 50)
