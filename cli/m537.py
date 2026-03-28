#!/usr/bin/env python3
"""
M537 Voice Gateway CLI Client
Command-line interface for natural language server queries
"""
import argparse
import json
import os
import sys
from typing import Optional
import urllib.request
import urllib.error


# Configuration
DEFAULT_HOST = os.environ.get("M537_HOST", "http://localhost:5537")
VERSION = "1.0.0"


class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"

    @classmethod
    def disable(cls):
        """Disable colors for non-terminal output"""
        for attr in dir(cls):
            if not attr.startswith("_") and attr != "disable":
                setattr(cls, attr, "")


class M537Client:
    """M537 Voice Gateway API Client"""

    def __init__(self, host: str = DEFAULT_HOST):
        self.host = host.rstrip("/")
        self.session_id = os.environ.get("M537_SESSION", None)

    def query(self, transcript: str) -> dict:
        """Send a voice query"""
        data = {"transcript": transcript}
        if self.session_id:
            data["session_id"] = self.session_id

        return self._post("/api/voice-query", data)

    def health(self) -> dict:
        """Check health status"""
        return self._get("/health")

    def metrics(self) -> dict:
        """Get metrics"""
        return self._get("/api/metrics/json")

    def version(self) -> dict:
        """Get version info"""
        return self._get("/api/version")

    def _get(self, path: str) -> dict:
        """Make GET request"""
        url = f"{self.host}{path}"
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection failed: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def _post(self, path: str, data: dict) -> dict:
        """Make POST request"""
        url = f"{self.host}{path}"
        try:
            body = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(url, data=body, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            try:
                error_body = json.loads(e.read().decode())
                return error_body
            except:
                return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection failed: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}


def print_result(result: dict, raw: bool = False):
    """Pretty print query result"""
    if raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if "error" in result and isinstance(result["error"], str):
        print(f"{Colors.RED}Error: {result['error']}{Colors.RESET}")
        return

    if result.get("success"):
        data = result.get("data", {})
        answer = data.get("answer_text", "No response")

        print(f"\n{Colors.GREEN}{Colors.BOLD}Response:{Colors.RESET}")
        print(f"  {answer}")

        if data.get("intent"):
            print(f"\n{Colors.GRAY}Intent: {data['intent']} "
                  f"(confidence: {data.get('confidence', 0):.0%}){Colors.RESET}")

        if data.get("cached"):
            print(f"{Colors.GRAY}(cached){Colors.RESET}")

        suggestions = data.get("suggestions", [])
        if suggestions:
            print(f"\n{Colors.CYAN}Suggestions:{Colors.RESET}")
            for s in suggestions:
                print(f"  - {s}")

    elif result.get("error"):
        error = result["error"]
        print(f"\n{Colors.YELLOW}{error.get('message', 'Unknown error')}{Colors.RESET}")

        suggestions = error.get("suggestions", [])
        if suggestions:
            print(f"\n{Colors.CYAN}Try these queries:{Colors.RESET}")
            for s in suggestions:
                print(f"  - {s}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


def print_health(result: dict, raw: bool = False):
    """Pretty print health status"""
    if raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    status = result.get("status", "unknown")
    color = Colors.GREEN if status == "healthy" else Colors.RED

    print(f"\n{Colors.BOLD}M537 Voice Gateway{Colors.RESET}")
    print(f"  Status:    {color}{status}{Colors.RESET}")
    print(f"  Version:   {result.get('version', 'unknown')}")
    print(f"  Ecosystem: {result.get('ecosystem', 'unknown')}")

    uptime = result.get("uptime_seconds", 0)
    hours = uptime // 3600
    minutes = (uptime % 3600) // 60
    print(f"  Uptime:    {hours}h {minutes}m")

    checks = result.get("checks", {})
    if checks:
        print(f"\n{Colors.BOLD}Checks:{Colors.RESET}")
        for check, passed in checks.items():
            icon = Colors.GREEN + "✓" if passed else Colors.RED + "✗"
            print(f"  {icon} {check}{Colors.RESET}")


def print_metrics(result: dict, raw: bool = False):
    """Pretty print metrics"""
    if raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"\n{Colors.BOLD}Metrics{Colors.RESET}")

    requests = result.get("requests", {})
    print(f"\n  {Colors.CYAN}Requests:{Colors.RESET}")
    print(f"    Total:        {requests.get('total', 0)}")
    print(f"    Success:      {requests.get('success', 0)}")
    print(f"    Failed:       {requests.get('failed', 0)}")
    print(f"    Success Rate: {requests.get('success_rate', '0%')}")

    latency = result.get("latency", {})
    print(f"\n  {Colors.CYAN}Latency:{Colors.RESET}")
    print(f"    Average: {latency.get('avg_ms', 0):.1f}ms")
    print(f"    P95:     {latency.get('p95_ms', 0):.1f}ms")
    print(f"    Max:     {latency.get('max_ms', 0):.1f}ms")

    cache = result.get("cache", {})
    print(f"\n  {Colors.CYAN}Cache:{Colors.RESET}")
    print(f"    Hits:     {cache.get('hits', 0)}")
    print(f"    Misses:   {cache.get('misses', 0)}")
    print(f"    Hit Rate: {cache.get('hit_rate', '0%')}")


def interactive_mode(client: M537Client):
    """Run interactive query mode"""
    print(f"\n{Colors.BOLD}M537 Voice Gateway - Interactive Mode{Colors.RESET}")
    print(f"{Colors.GRAY}Type your query or 'exit' to quit.{Colors.RESET}")
    print(f"{Colors.GRAY}Commands: /health, /metrics, /clear{Colors.RESET}\n")

    while True:
        try:
            query = input(f"{Colors.BLUE}>{Colors.RESET} ").strip()

            if not query:
                continue

            if query.lower() in ("exit", "quit", "/exit", "/quit"):
                print(f"{Colors.GRAY}Goodbye!{Colors.RESET}")
                break

            if query == "/health":
                print_health(client.health())
                continue

            if query == "/metrics":
                print_metrics(client.metrics())
                continue

            if query == "/clear":
                os.system("clear" if os.name == "posix" else "cls")
                continue

            result = client.query(query)
            print_result(result)
            print()

        except KeyboardInterrupt:
            print(f"\n{Colors.GRAY}Goodbye!{Colors.RESET}")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description="M537 Voice Gateway CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  m537 "有多少个项目"
  m537 "系统状态怎么样"
  m537 --health
  m537 --metrics
  m537 -i  (interactive mode)

Environment variables:
  M537_HOST     API host (default: http://localhost:5537)
  M537_SESSION  Session ID for multi-turn dialogue
        """
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Voice query to send"
    )
    parser.add_argument(
        "-H", "--host",
        default=DEFAULT_HOST,
        help=f"API host (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Interactive mode"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Check health status"
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Show metrics"
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Output raw JSON"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"m537 {VERSION}"
    )

    args = parser.parse_args()

    # Disable colors if needed
    if args.no_color or not sys.stdout.isatty():
        Colors.disable()

    # Create client
    client = M537Client(args.host)

    # Execute command
    if args.health:
        print_health(client.health(), args.raw)
    elif args.metrics:
        print_metrics(client.metrics(), args.raw)
    elif args.interactive:
        interactive_mode(client)
    elif args.query:
        result = client.query(args.query)
        print_result(result, args.raw)
    else:
        # No query provided, show help or enter interactive mode
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
