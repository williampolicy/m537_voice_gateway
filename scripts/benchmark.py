#!/usr/bin/env python3
"""
M537 Voice Gateway - Performance Benchmark
Tests API response times and throughput
"""
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any

BASE_URL = "http://localhost:5537"

# Test queries
TEST_QUERIES = [
    "现在有多少个项目",
    "系统状态怎么样",
    "当前有哪些端口在监听",
    "最近有什么错误",
    "哪些Docker容器在运行",
]


async def make_request(session: aiohttp.ClientSession, query: str) -> Dict[str, Any]:
    """Make a single API request and measure time"""
    start = time.perf_counter()

    try:
        async with session.post(
            f"{BASE_URL}/api/voice-query",
            json={"transcript": query},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            data = await response.json()
            elapsed = (time.perf_counter() - start) * 1000

            return {
                "success": response.status == 200 and data.get("success", False),
                "latency_ms": elapsed,
                "status_code": response.status,
                "cached": data.get("data", {}).get("cached", False) if data.get("success") else False
            }
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return {
            "success": False,
            "latency_ms": elapsed,
            "status_code": 0,
            "error": str(e)
        }


async def run_sequential_benchmark(num_requests: int = 50) -> Dict[str, Any]:
    """Run sequential requests to measure baseline latency"""
    print(f"\n{'='*60}")
    print("Sequential Benchmark")
    print(f"{'='*60}")

    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(num_requests):
            query = TEST_QUERIES[i % len(TEST_QUERIES)]
            result = await make_request(session, query)
            results.append(result)

            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{num_requests} requests")

    # Calculate stats
    latencies = [r["latency_ms"] for r in results if r["success"]]
    success_count = sum(1 for r in results if r["success"])
    cached_count = sum(1 for r in results if r.get("cached", False))

    stats = {
        "total_requests": num_requests,
        "successful": success_count,
        "cached": cached_count,
        "failed": num_requests - success_count,
        "latency_min_ms": min(latencies) if latencies else 0,
        "latency_max_ms": max(latencies) if latencies else 0,
        "latency_avg_ms": statistics.mean(latencies) if latencies else 0,
        "latency_p50_ms": statistics.median(latencies) if latencies else 0,
        "latency_p95_ms": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0,
        "latency_p99_ms": sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0,
    }

    print(f"\nResults:")
    print(f"  Success Rate: {success_count}/{num_requests} ({success_count/num_requests*100:.1f}%)")
    print(f"  Cache Hits: {cached_count}")
    print(f"  Latency (min/avg/max): {stats['latency_min_ms']:.1f} / {stats['latency_avg_ms']:.1f} / {stats['latency_max_ms']:.1f} ms")
    print(f"  Latency P50: {stats['latency_p50_ms']:.1f} ms")
    print(f"  Latency P95: {stats['latency_p95_ms']:.1f} ms")
    print(f"  Latency P99: {stats['latency_p99_ms']:.1f} ms")

    return stats


async def run_concurrent_benchmark(num_requests: int = 100, concurrency: int = 10) -> Dict[str, Any]:
    """Run concurrent requests to measure throughput"""
    print(f"\n{'='*60}")
    print(f"Concurrent Benchmark (concurrency={concurrency})")
    print(f"{'='*60}")

    results = []
    start_time = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        # Create tasks in batches
        for batch_start in range(0, num_requests, concurrency):
            batch_size = min(concurrency, num_requests - batch_start)
            tasks = []

            for i in range(batch_size):
                query = TEST_QUERIES[(batch_start + i) % len(TEST_QUERIES)]
                tasks.append(make_request(session, query))

            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            print(f"  Completed {len(results)}/{num_requests} requests")

    total_time = time.perf_counter() - start_time

    # Calculate stats
    latencies = [r["latency_ms"] for r in results if r["success"]]
    success_count = sum(1 for r in results if r["success"])

    stats = {
        "total_requests": num_requests,
        "concurrency": concurrency,
        "total_time_s": total_time,
        "successful": success_count,
        "failed": num_requests - success_count,
        "throughput_rps": num_requests / total_time,
        "latency_avg_ms": statistics.mean(latencies) if latencies else 0,
        "latency_p95_ms": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0,
    }

    print(f"\nResults:")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"  Success Rate: {success_count}/{num_requests} ({success_count/num_requests*100:.1f}%)")
    print(f"  Throughput: {stats['throughput_rps']:.1f} req/s")
    print(f"  Avg Latency: {stats['latency_avg_ms']:.1f} ms")
    print(f"  P95 Latency: {stats['latency_p95_ms']:.1f} ms")

    return stats


async def run_health_check():
    """Quick health check before benchmarks"""
    print("Checking service health...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    print("  Service is healthy!")
                    return True
                else:
                    print(f"  Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"  Cannot connect to service: {e}")
            return False


async def main():
    print("=" * 60)
    print("M537 Voice Gateway Performance Benchmark")
    print("=" * 60)

    # Health check
    if not await run_health_check():
        print("\nService not available. Exiting.")
        return

    # Run benchmarks
    seq_results = await run_sequential_benchmark(50)
    conc_results = await run_concurrent_benchmark(100, 10)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Sequential: {seq_results['latency_avg_ms']:.1f}ms avg, P95={seq_results['latency_p95_ms']:.1f}ms")
    print(f"Concurrent: {conc_results['throughput_rps']:.1f} req/s, P95={conc_results['latency_p95_ms']:.1f}ms")

    # Performance rating
    avg_latency = seq_results['latency_avg_ms']
    if avg_latency < 100:
        rating = "Excellent"
    elif avg_latency < 500:
        rating = "Good"
    elif avg_latency < 1000:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    print(f"\nPerformance Rating: {rating}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
