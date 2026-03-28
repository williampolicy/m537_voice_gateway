#!/usr/bin/env python3
"""
M537 Voice Gateway - Load Testing Script
Simple load test without external dependencies
"""
import asyncio
import aiohttp
import time
import statistics
import argparse
from dataclasses import dataclass, field
from typing import List
import sys


@dataclass
class LoadTestResult:
    """Results from load test"""
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    latencies: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: float = 0
    end_time: float = 0

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def rps(self) -> float:
        return self.total_requests / self.duration if self.duration > 0 else 0

    @property
    def success_rate(self) -> float:
        return (self.successful / self.total_requests * 100) if self.total_requests > 0 else 0

    @property
    def avg_latency(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0

    @property
    def p50_latency(self) -> float:
        if not self.latencies:
            return 0
        return statistics.median(self.latencies)

    @property
    def p95_latency(self) -> float:
        if len(self.latencies) < 20:
            return max(self.latencies) if self.latencies else 0
        return statistics.quantiles(self.latencies, n=20)[18]

    @property
    def p99_latency(self) -> float:
        if len(self.latencies) < 100:
            return max(self.latencies) if self.latencies else 0
        return statistics.quantiles(self.latencies, n=100)[98]

    def print_summary(self):
        print("\n" + "=" * 60)
        print("LOAD TEST RESULTS")
        print("=" * 60)
        print(f"Duration:        {self.duration:.2f}s")
        print(f"Total Requests:  {self.total_requests}")
        print(f"Successful:      {self.successful}")
        print(f"Failed:          {self.failed}")
        print(f"Success Rate:    {self.success_rate:.1f}%")
        print(f"Requests/sec:    {self.rps:.1f}")
        print("-" * 60)
        print("LATENCY (ms)")
        print(f"  Average:       {self.avg_latency:.2f}")
        print(f"  p50:           {self.p50_latency:.2f}")
        print(f"  p95:           {self.p95_latency:.2f}")
        print(f"  p99:           {self.p99_latency:.2f}")
        print(f"  Min:           {min(self.latencies):.2f}" if self.latencies else "  Min: N/A")
        print(f"  Max:           {max(self.latencies):.2f}" if self.latencies else "  Max: N/A")

        if self.errors:
            print("-" * 60)
            print("ERRORS (first 5):")
            for err in self.errors[:5]:
                print(f"  - {err}")

        print("=" * 60)


class LoadTester:
    """Simple async load tester"""

    def __init__(self, base_url: str, concurrency: int = 10):
        self.base_url = base_url.rstrip("/")
        self.concurrency = concurrency

    async def make_request(
        self,
        session: aiohttp.ClientSession,
        method: str,
        path: str,
        json_data: dict = None,
        result: LoadTestResult = None
    ):
        """Make a single request and record results"""
        url = f"{self.base_url}{path}"
        start = time.perf_counter()

        try:
            async with session.request(method, url, json=json_data) as response:
                await response.text()
                latency = (time.perf_counter() - start) * 1000
                result.latencies.append(latency)
                result.total_requests += 1

                if 200 <= response.status < 300:
                    result.successful += 1
                else:
                    result.failed += 1
                    result.errors.append(f"HTTP {response.status} on {path}")

        except Exception as e:
            result.total_requests += 1
            result.failed += 1
            result.errors.append(str(e))

    async def run_health_test(self, duration: int = 10) -> LoadTestResult:
        """Load test health endpoint"""
        print(f"Testing GET /health for {duration}s with {self.concurrency} concurrent users...")
        result = LoadTestResult()
        result.start_time = time.time()

        async with aiohttp.ClientSession() as session:
            end_time = time.time() + duration

            while time.time() < end_time:
                tasks = [
                    self.make_request(session, "GET", "/health", result=result)
                    for _ in range(self.concurrency)
                ]
                await asyncio.gather(*tasks)

        result.end_time = time.time()
        return result

    async def run_voice_query_test(self, duration: int = 10) -> LoadTestResult:
        """Load test voice query endpoint"""
        print(f"Testing POST /api/voice-query for {duration}s with {self.concurrency} concurrent users...")
        result = LoadTestResult()
        result.start_time = time.time()

        queries = [
            {"transcript": "现在有多少个项目"},
            {"transcript": "系统状态怎么样"},
            {"transcript": "哪些端口在监听"},
            {"transcript": "磁盘空间够吗"},
            {"transcript": "运行时间多久了"},
        ]

        async with aiohttp.ClientSession() as session:
            end_time = time.time() + duration
            query_idx = 0

            while time.time() < end_time:
                tasks = []
                for _ in range(self.concurrency):
                    query = queries[query_idx % len(queries)]
                    tasks.append(
                        self.make_request(session, "POST", "/api/voice-query", json_data=query, result=result)
                    )
                    query_idx += 1

                await asyncio.gather(*tasks)

        result.end_time = time.time()
        return result

    async def run_mixed_test(self, duration: int = 10) -> LoadTestResult:
        """Load test with mixed endpoints"""
        print(f"Running mixed load test for {duration}s with {self.concurrency} concurrent users...")
        result = LoadTestResult()
        result.start_time = time.time()

        endpoints = [
            ("GET", "/health", None),
            ("GET", "/api/metrics/json", None),
            ("POST", "/api/voice-query", {"transcript": "系统状态"}),
            ("POST", "/api/voice-query", {"transcript": "项目数量"}),
        ]

        async with aiohttp.ClientSession() as session:
            end_time = time.time() + duration
            idx = 0

            while time.time() < end_time:
                tasks = []
                for _ in range(self.concurrency):
                    method, path, data = endpoints[idx % len(endpoints)]
                    tasks.append(
                        self.make_request(session, method, path, json_data=data, result=result)
                    )
                    idx += 1

                await asyncio.gather(*tasks)

        result.end_time = time.time()
        return result


async def main():
    parser = argparse.ArgumentParser(description="M537 Voice Gateway Load Test")
    parser.add_argument("--url", default="http://localhost:5537", help="Base URL")
    parser.add_argument("--duration", type=int, default=10, help="Test duration in seconds")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent users")
    parser.add_argument("--test", choices=["health", "voice", "mixed", "all"], default="all", help="Test type")

    args = parser.parse_args()

    tester = LoadTester(args.url, args.concurrency)

    print(f"\n🚀 M537 Voice Gateway Load Test")
    print(f"   URL: {args.url}")
    print(f"   Duration: {args.duration}s")
    print(f"   Concurrency: {args.concurrency}")
    print()

    if args.test in ("health", "all"):
        result = await tester.run_health_test(args.duration)
        result.print_summary()

    if args.test in ("voice", "all"):
        result = await tester.run_voice_query_test(args.duration)
        result.print_summary()

    if args.test in ("mixed", "all"):
        result = await tester.run_mixed_test(args.duration)
        result.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
