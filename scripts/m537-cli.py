#!/usr/bin/env python3
"""
M537 Voice Gateway - CLI Management Tool

Usage:
    m537-cli.py query "服务器状态"
    m537-cli.py health
    m537-cli.py keys list
    m537-cli.py keys create --name "My Key" --tier standard
    m537-cli.py keys revoke <key_id>
    m537-cli.py analytics summary
    m537-cli.py cache clear
"""
import argparse
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'clients', 'python'))

from m537_client import (
    M537Client,
    VoiceQueryRequest,
    M537ClientError,
    AuthenticationError,
    RateLimitError
)


class CLI:
    """M537 CLI Tool"""

    def __init__(self):
        self.base_url = os.environ.get("M537_URL", "http://localhost:5537")
        self.api_key = os.environ.get("M537_API_KEY", "")
        self.admin_key = os.environ.get("M537_ADMIN_KEY", "")
        self.client = M537Client(base_url=self.base_url, api_key=self.api_key)

    def _admin_headers(self):
        """Get admin headers"""
        return {"X-Admin-Key": self.admin_key} if self.admin_key else {}

    def _print_json(self, data):
        """Pretty print JSON"""
        print(json.dumps(data, indent=2, ensure_ascii=False))

    def _print_error(self, message):
        """Print error message"""
        print(f"\033[91mError: {message}\033[0m", file=sys.stderr)

    def _print_success(self, message):
        """Print success message"""
        print(f"\033[92m{message}\033[0m")

    # ==================== Query Commands ====================

    def query(self, args):
        """Send a voice query"""
        try:
            response = self.client.query(VoiceQueryRequest(
                transcript=args.transcript,
                language=args.language
            ))

            if response.success and response.data:
                print(f"\n\033[1mAnswer:\033[0m {response.data.answer_text}")
                print(f"\033[90mIntent: {response.data.intent} (confidence: {response.data.confidence:.2f})")
                print(f"Tool: {response.data.tool_used} | Cached: {response.data.cached}\033[0m")

                if response.data.suggestions:
                    print(f"\n\033[90mSuggestions: {', '.join(response.data.suggestions)}\033[0m")
            else:
                self._print_error(response.error.message if response.error else "Unknown error")
                return 1

        except AuthenticationError:
            self._print_error("Authentication failed. Check your API key.")
            return 1
        except RateLimitError as e:
            self._print_error(f"Rate limit exceeded. Retry after {e.retry_after}s")
            return 1
        except M537ClientError as e:
            self._print_error(str(e))
            return 1

        return 0

    # ==================== Health Commands ====================

    def health(self, args):
        """Check service health"""
        try:
            if args.summary:
                result = self.client.health_summary()
                status = result.get("status", "unknown")
                color = "\033[92m" if status == "healthy" else "\033[93m" if status == "degraded" else "\033[91m"
                print(f"{color}Status: {status}\033[0m")
                print(f"Version: {result.get('version', 'unknown')}")
                print(f"Uptime: {result.get('uptime_seconds', 0)}s")
            else:
                health = self.client.health()
                status = health.status
                color = "\033[92m" if status == "healthy" else "\033[93m" if status == "degraded" else "\033[91m"
                print(f"{color}Status: {status}\033[0m")
                print(f"Version: {health.version}")
                print(f"API Version: {health.api_version}")
                print(f"Uptime: {health.uptime_seconds}s")
                print(f"\nChecks:")
                for check in health.checks:
                    check_color = "\033[92m" if check.status == "healthy" else "\033[91m"
                    print(f"  {check_color}● {check.name}: {check.status} ({check.latency_ms:.1f}ms)\033[0m")

        except M537ClientError as e:
            self._print_error(str(e))
            return 1

        return 0

    # ==================== Key Management Commands ====================

    def keys_list(self, args):
        """List API keys"""
        import urllib.request
        import urllib.error

        url = f"{self.base_url}/api/admin/keys"
        req = urllib.request.Request(url)
        req.add_header("X-Admin-Key", self.admin_key)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                keys = json.loads(response.read().decode())

            if not keys:
                print("No API keys found.")
                return 0

            print(f"\n{'ID':<20} {'Name':<20} {'Tier':<12} {'Enabled':<10}")
            print("-" * 62)
            for key in keys:
                enabled = "\033[92m✓\033[0m" if key["enabled"] else "\033[91m✗\033[0m"
                print(f"{key['key_id']:<20} {key['name']:<20} {key['tier']:<12} {enabled}")

        except urllib.error.HTTPError as e:
            if e.code == 401:
                self._print_error("Admin key required. Set M537_ADMIN_KEY environment variable.")
            else:
                self._print_error(f"HTTP {e.code}: {e.reason}")
            return 1
        except urllib.error.URLError as e:
            self._print_error(f"Connection failed: {e.reason}")
            return 1

        return 0

    def keys_create(self, args):
        """Create a new API key"""
        import urllib.request
        import urllib.error

        url = f"{self.base_url}/api/admin/keys"
        data = json.dumps({
            "name": args.name,
            "tier": args.tier,
            "expires_days": args.expires
        }).encode()

        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Admin-Key", self.admin_key)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())

            self._print_success("API key created successfully!")
            print(f"\n\033[1mKey ID:\033[0m {result['key_id']}")
            print(f"\033[1mAPI Key:\033[0m {result['api_key']}")
            print(f"\033[1mTier:\033[0m {result['tier']} ({result['rate_limit']} req/min)")
            if result['expires_at']:
                print(f"\033[1mExpires:\033[0m {result['expires_at']}")
            print(f"\n\033[93mWarning: Store this key securely. It cannot be retrieved later.\033[0m")

        except urllib.error.HTTPError as e:
            if e.code == 401:
                self._print_error("Admin key required. Set M537_ADMIN_KEY environment variable.")
            else:
                try:
                    error = json.loads(e.read().decode())
                    self._print_error(error.get("detail", {}).get("error", {}).get("message", str(e)))
                except:
                    self._print_error(f"HTTP {e.code}: {e.reason}")
            return 1
        except urllib.error.URLError as e:
            self._print_error(f"Connection failed: {e.reason}")
            return 1

        return 0

    def keys_revoke(self, args):
        """Revoke an API key"""
        import urllib.request
        import urllib.error

        url = f"{self.base_url}/api/admin/keys/{args.key_id}"
        req = urllib.request.Request(url, method="DELETE")
        req.add_header("X-Admin-Key", self.admin_key)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())

            self._print_success(result.get("message", "Key revoked"))

        except urllib.error.HTTPError as e:
            if e.code == 404:
                self._print_error("API key not found")
            elif e.code == 401:
                self._print_error("Admin key required")
            else:
                self._print_error(f"HTTP {e.code}: {e.reason}")
            return 1
        except urllib.error.URLError as e:
            self._print_error(f"Connection failed: {e.reason}")
            return 1

        return 0

    # ==================== Analytics Commands ====================

    def analytics(self, args):
        """Get analytics"""
        try:
            stats = self.client.get_analytics()
            print(f"\n\033[1mAnalytics Summary\033[0m")
            print("-" * 40)
            print(f"Total Queries: {stats.total_queries}")
            print(f"Successful: {stats.successful_queries}")
            print(f"Failed: {stats.failed_queries}")
            print(f"Cache Hit Rate: {stats.cache_hit_rate:.1%}")
            print(f"\nLatency:")
            print(f"  Average: {stats.avg_latency_ms:.1f}ms")
            print(f"  P95: {stats.p95_latency_ms:.1f}ms")
            print(f"  P99: {stats.p99_latency_ms:.1f}ms")

            if stats.top_intents:
                print(f"\nTop Intents:")
                for intent in stats.top_intents[:5]:
                    print(f"  {intent.get('intent', 'unknown')}: {intent.get('count', 0)}")

        except M537ClientError as e:
            self._print_error(str(e))
            return 1

        return 0

    # ==================== Cache Commands ====================

    def cache_clear(self, args):
        """Clear cache"""
        import urllib.request
        import urllib.error

        url = f"{self.base_url}/api/admin/cache/clear"
        req = urllib.request.Request(url, method="POST")
        req.add_header("X-Admin-Key", self.admin_key)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())

            self._print_success(result.get("message", "Cache cleared"))

        except urllib.error.HTTPError as e:
            if e.code == 401:
                self._print_error("Admin key required")
            else:
                self._print_error(f"HTTP {e.code}: {e.reason}")
            return 1
        except urllib.error.URLError as e:
            self._print_error(f"Connection failed: {e.reason}")
            return 1

        return 0

    # ==================== Metrics Commands ====================

    def metrics(self, args):
        """Get metrics"""
        try:
            if args.prometheus:
                metrics = self.client.metrics_prometheus()
                print(metrics)
            else:
                metrics = self.client.metrics()
                self._print_json(metrics)

        except M537ClientError as e:
            self._print_error(str(e))
            return 1

        return 0


def main():
    parser = argparse.ArgumentParser(
        description="M537 Voice Gateway CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  M537_URL         API base URL (default: http://localhost:5537)
  M537_API_KEY     API key for authentication
  M537_ADMIN_KEY   Admin key for management operations

Examples:
  %(prog)s query "服务器状态"
  %(prog)s health
  %(prog)s keys list
  %(prog)s keys create --name "My App" --tier standard
  %(prog)s analytics
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Query command
    query_parser = subparsers.add_parser("query", help="Send a voice query")
    query_parser.add_argument("transcript", help="Query text")
    query_parser.add_argument("--language", "-l", default="zh-CN", help="Language code")

    # Health command
    health_parser = subparsers.add_parser("health", help="Check service health")
    health_parser.add_argument("--summary", "-s", action="store_true", help="Show summary only")

    # Keys commands
    keys_parser = subparsers.add_parser("keys", help="Manage API keys")
    keys_subparsers = keys_parser.add_subparsers(dest="keys_command")

    keys_list_parser = keys_subparsers.add_parser("list", help="List API keys")

    keys_create_parser = keys_subparsers.add_parser("create", help="Create API key")
    keys_create_parser.add_argument("--name", "-n", required=True, help="Key name")
    keys_create_parser.add_argument("--tier", "-t", default="standard",
                                     choices=["free", "standard", "premium", "enterprise"],
                                     help="Rate limit tier")
    keys_create_parser.add_argument("--expires", "-e", type=int, help="Days until expiration")

    keys_revoke_parser = keys_subparsers.add_parser("revoke", help="Revoke API key")
    keys_revoke_parser.add_argument("key_id", help="Key ID to revoke")

    # Analytics command
    analytics_parser = subparsers.add_parser("analytics", help="View analytics")

    # Cache command
    cache_parser = subparsers.add_parser("cache", help="Cache operations")
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command")
    cache_clear_parser = cache_subparsers.add_parser("clear", help="Clear cache")

    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="View metrics")
    metrics_parser.add_argument("--prometheus", "-p", action="store_true",
                                 help="Output in Prometheus format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    cli = CLI()

    if args.command == "query":
        return cli.query(args)
    elif args.command == "health":
        return cli.health(args)
    elif args.command == "keys":
        if args.keys_command == "list":
            return cli.keys_list(args)
        elif args.keys_command == "create":
            return cli.keys_create(args)
        elif args.keys_command == "revoke":
            return cli.keys_revoke(args)
        else:
            keys_parser.print_help()
    elif args.command == "analytics":
        return cli.analytics(args)
    elif args.command == "cache":
        if args.cache_command == "clear":
            return cli.cache_clear(args)
        else:
            cache_parser.print_help()
    elif args.command == "metrics":
        return cli.metrics(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
