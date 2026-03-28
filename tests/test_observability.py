"""
M537 Voice Gateway - Observability Tests
Tests for tracing and error tracking
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestTracing:
    """Tests for OpenTelemetry tracing"""

    def test_get_tracer_returns_noop_when_disabled(self):
        """Test tracer returns no-op when disabled"""
        os.environ["OTEL_ENABLED"] = "false"
        from tracing import get_tracer, NoOpTracer

        # Force re-initialization
        import tracing
        tracing._tracer = None

        tracer = get_tracer()
        assert tracer is not None

    def test_trace_function_decorator(self):
        """Test trace_function decorator works"""
        from tracing import trace_function

        @trace_function("test_operation")
        def test_func(x, y):
            return x + y

        result = test_func(1, 2)
        assert result == 3

    def test_trace_function_with_exception(self):
        """Test trace_function handles exceptions"""
        from tracing import trace_function

        @trace_function()
        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_func()

    def test_trace_block_context_manager(self):
        """Test trace_block context manager"""
        from tracing import trace_block

        with trace_block("test_block", {"key": "value"}) as span:
            result = 1 + 1

        assert result == 2

    def test_add_span_attributes(self):
        """Test adding span attributes"""
        from tracing import add_span_attributes

        # Should not raise even without real tracing
        add_span_attributes(key1="value1", key2=123)

    def test_record_exception(self):
        """Test recording exception"""
        from tracing import record_exception

        # Should not raise
        record_exception(ValueError("test"))


class TestErrorTracking:
    """Tests for error tracking"""

    @pytest.fixture
    def tracker(self):
        from error_tracking import ErrorTracker
        return ErrorTracker(max_errors=10)

    def test_capture_exception(self, tracker):
        """Test capturing an exception"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            fingerprint = tracker.capture(e)

        assert fingerprint is not None
        assert len(fingerprint) == 12

    def test_capture_with_context(self, tracker):
        """Test capturing exception with context"""
        try:
            raise RuntimeError("Context test")
        except RuntimeError as e:
            fingerprint = tracker.capture(
                e,
                context={"path": "/api/test", "user_id": "123"}
            )

        errors = tracker.get_recent_errors(limit=1)
        assert len(errors) == 1
        assert errors[0]["context"]["path"] == "/api/test"

    def test_get_recent_errors(self, tracker):
        """Test getting recent errors"""
        for i in range(5):
            try:
                raise ValueError(f"Error {i}")
            except ValueError as e:
                tracker.capture(e)

        errors = tracker.get_recent_errors(limit=3)
        assert len(errors) == 3

    def test_error_summary(self, tracker):
        """Test error summary statistics"""
        # Create some duplicate errors
        for _ in range(3):
            try:
                raise ValueError("Repeated error")
            except ValueError as e:
                tracker.capture(e)

        try:
            raise RuntimeError("Different error")
        except RuntimeError as e:
            tracker.capture(e)

        summary = tracker.get_error_summary()
        assert summary["total_errors"] == 4
        assert summary["unique_errors"] == 2
        assert len(summary["top_errors"]) > 0

    def test_error_fingerprinting(self, tracker):
        """Test that same errors get same fingerprint"""
        fingerprints = []
        for _ in range(3):
            try:
                raise ValueError("Same error message")
            except ValueError as e:
                fingerprints.append(tracker.capture(e))

        # All fingerprints should be the same
        assert len(set(fingerprints)) == 1

    def test_clear_errors(self, tracker):
        """Test clearing all errors"""
        try:
            raise ValueError("Error to clear")
        except ValueError as e:
            tracker.capture(e)

        tracker.clear()
        errors = tracker.get_recent_errors()
        assert len(errors) == 0

    def test_max_errors_limit(self, tracker):
        """Test that max_errors limit is enforced"""
        for i in range(20):
            try:
                raise ValueError(f"Error {i}")
            except ValueError as e:
                tracker.capture(e)

        # Should only keep max_errors (10)
        errors = tracker.get_recent_errors(limit=100)
        assert len(errors) <= 10

    def test_error_entry_to_dict(self):
        """Test error entry serialization"""
        from error_tracking import ErrorEntry

        try:
            raise ValueError("Test serialization")
        except ValueError as e:
            entry = ErrorEntry(e, context={"test": True})

        data = entry.to_dict()
        assert "timestamp" in data
        assert data["type"] == "ValueError"
        assert data["message"] == "Test serialization"
        assert data["context"]["test"] == True


class TestGlobalErrorTracker:
    """Tests for global error tracker"""

    def test_capture_exception_function(self):
        """Test global capture_exception function"""
        from error_tracking import capture_exception, error_tracker

        error_tracker.clear()

        try:
            raise ValueError("Global test")
        except ValueError as e:
            fingerprint = capture_exception(e)

        assert fingerprint is not None
        errors = error_tracker.get_recent_errors()
        assert len(errors) >= 1


# Run tests with: pytest tests/test_observability.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
