"""
M537 Voice Gateway - OpenTelemetry Tracing
Distributed tracing support for observability
"""
import os
import logging
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Tracing configuration
TRACING_ENABLED = os.environ.get("OTEL_ENABLED", "false").lower() == "true"
SERVICE_NAME = os.environ.get("OTEL_SERVICE_NAME", "m537-voice-gateway")
OTLP_ENDPOINT = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")


# Stub implementations for when OpenTelemetry is not available
class NoOpSpan:
    """No-op span for when tracing is disabled"""

    def set_attribute(self, key, value):
        pass

    def set_status(self, status):
        pass

    def record_exception(self, exception):
        pass

    def add_event(self, name, attributes=None):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class NoOpTracer:
    """No-op tracer for when tracing is disabled"""

    @contextmanager
    def start_as_current_span(self, name, **kwargs):
        yield NoOpSpan()

    def start_span(self, name, **kwargs):
        return NoOpSpan()


# Global tracer instance
_tracer = None


def init_tracing(service_name: str = None, service_version: str = None):
    """
    Initialize tracing with custom service name and version.

    Args:
        service_name: Override default service name
        service_version: Override default service version
    """
    global SERVICE_NAME
    if service_name:
        SERVICE_NAME = service_name

    # Force re-initialization of tracer
    global _tracer
    _tracer = None

    # Get tracer to initialize
    tracer = get_tracer()
    logger.info(f"Tracing initialized for {SERVICE_NAME}")
    return tracer


def get_tracer():
    """Get the tracer instance, initializing if needed"""
    global _tracer

    if _tracer is not None:
        return _tracer

    if not TRACING_ENABLED:
        logger.debug("Tracing disabled, using no-op tracer")
        _tracer = NoOpTracer()
        return _tracer

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import SERVICE_NAME as RESOURCE_SERVICE_NAME, Resource
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        # Create resource with service name
        resource = Resource(attributes={
            RESOURCE_SERVICE_NAME: SERVICE_NAME,
            "service.version": "1.0.0",
            "deployment.environment": os.environ.get("ENVIRONMENT", "development")
        })

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        _tracer = trace.get_tracer(__name__)
        logger.info(f"OpenTelemetry tracing initialized: endpoint={OTLP_ENDPOINT}")

    except ImportError:
        logger.warning("OpenTelemetry not installed, using no-op tracer")
        _tracer = NoOpTracer()
    except Exception as e:
        logger.error(f"Failed to initialize tracing: {e}")
        _tracer = NoOpTracer()

    return _tracer


def trace_function(name: Optional[str] = None):
    """
    Decorator to trace a function.

    Usage:
        @trace_function()
        def my_function():
            pass

        @trace_function("custom_name")
        def another_function():
            pass
    """
    def decorator(func):
        span_name = name or func.__name__

        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name) as span:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name) as span:
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


@contextmanager
def trace_block(name: str, attributes: Optional[dict] = None):
    """
    Context manager to trace a code block.

    Usage:
        with trace_block("process_query", {"query_type": "count"}):
            # code to trace
            pass
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        yield span


def add_span_attributes(**attributes):
    """Add attributes to the current span"""
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        for key, value in attributes.items():
            span.set_attribute(key, value)
    except ImportError:
        pass


def record_exception(exception: Exception):
    """Record an exception in the current span"""
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        span.record_exception(exception)
    except ImportError:
        pass


# FastAPI middleware for automatic request tracing
class TracingMiddleware:
    """ASGI middleware for automatic request tracing"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        tracer = get_tracer()
        method = scope.get("method", "?")
        path = scope.get("path", "?")

        with tracer.start_as_current_span(
            f"{method} {path}",
            attributes={
                "http.method": method,
                "http.url": path,
                "http.scheme": scope.get("scheme", "http"),
            }
        ) as span:
            # Capture response status
            status_code = 500

            async def send_wrapper(message):
                nonlocal status_code
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    span.set_attribute("http.status_code", status_code)
                await send(message)

            try:
                await self.app(scope, receive, send_wrapper)
            except Exception as e:
                span.record_exception(e)
                raise
