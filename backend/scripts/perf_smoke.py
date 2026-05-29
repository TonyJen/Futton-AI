"""
Lightweight backend performance smoke test.

Runs a configurable number of GET requests against common API endpoints and
fails when the observed p95 latency crosses the configured threshold or when
requests fail.
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
from time import perf_counter

import httpx


DEFAULT_ENDPOINTS = [
    "/health",
    "/api/v1/inventory",
    "/api/v1/dashboard/kpis",
    "/api/v1/agents/available",
]


async def time_request(client: httpx.AsyncClient, endpoint: str) -> tuple[str, float, int]:
    started = perf_counter()
    response = await client.get(endpoint)
    elapsed_ms = (perf_counter() - started) * 1000
    return endpoint, elapsed_ms, response.status_code


async def run_smoke(base_url: str, requests: int, concurrency: int) -> list[tuple[str, float, int]]:
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    timeout = httpx.Timeout(20.0)
    async with httpx.AsyncClient(base_url=base_url, limits=limits, timeout=timeout) as client:
        tasks = [
            time_request(client, DEFAULT_ENDPOINTS[index % len(DEFAULT_ENDPOINTS)])
            for index in range(requests)
        ]
        return await asyncio.gather(*tasks)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * pct)))
    return ordered[index]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a basic backend latency smoke test.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL")
    parser.add_argument("--requests", type=int, default=40, help="Total requests to issue")
    parser.add_argument("--concurrency", type=int, default=8, help="Concurrent requests")
    parser.add_argument(
        "--p95-threshold-ms",
        type=float,
        default=1500,
        help="Fail if p95 latency exceeds this threshold",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = asyncio.run(run_smoke(args.base_url, args.requests, args.concurrency))

    latencies = [duration for _, duration, status in results if status < 500]
    failures = [(endpoint, status) for endpoint, _, status in results if status >= 400]

    avg_latency = statistics.fmean(latencies) if latencies else 0.0
    p95_latency = percentile(latencies, 0.95)

    print(f"Requests: {len(results)}")
    print(f"Average latency: {avg_latency:.1f}ms")
    print(f"P95 latency: {p95_latency:.1f}ms")
    if failures:
        print("Failures:")
        for endpoint, status in failures:
            print(f"  {endpoint}: HTTP {status}")

    if failures or p95_latency > args.p95_threshold_ms:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
