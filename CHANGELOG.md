# Changelog

All notable changes to M537 Voice Gateway will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- API Key authentication system with tiered rate limiting
- Circuit breaker pattern for resilient external service calls
- Graceful shutdown with connection draining
- Webhook event notification support

## [1.0.0] - 2024-03-28

### Added

#### Core Features
- Natural language voice query interface
- Multi-language support (zh-CN, en-US, ja-JP)
- Real-time WebSocket status updates
- Intent recognition with confidence scoring
- 15+ built-in query tools (project count, system status, ports, etc.)

#### API
- RESTful API v1 with versioned endpoints
- OpenAPI/Swagger documentation
- Rate limiting (60 req/min, 10 req/sec burst)
- Request tracking with X-Request-ID
- Prometheus metrics endpoint
- JSON metrics endpoint

#### Frontend
- Progressive Web App (PWA) support
- Offline-capable with Service Worker
- Responsive design (mobile-optimized)
- Dark mode auto-detection
- Accessibility support (WCAG compliant)
- Toast notification system
- Real-time system status panel

#### Security
- XSS protection
- CSRF protection
- Input validation and sanitization
- Security headers (CSP, HSTS, etc.)
- Rate limiting per IP

#### Observability
- Prometheus metrics
- OpenTelemetry distributed tracing
- Structured logging with rotation
- Error tracking with Sentry integration (optional)
- Health checks (liveness, readiness, deep)

#### Deployment
- Docker multi-stage build
- Kubernetes Helm chart with HPA
- CI/CD with GitHub Actions
- Load testing with Locust

#### Client SDKs
- Python client library
- TypeScript/JavaScript client library

### Performance
- Query response < 100ms (p95)
- GZip compression for responses > 500 bytes
- In-memory LRU cache with TTL
- Connection pooling

## [0.9.0] - 2024-03-27

### Added
- Initial beta release
- Basic voice query functionality
- WebSocket real-time updates
- Health check endpoints

### Changed
- Improved intent parsing accuracy
- Enhanced error messages

### Fixed
- Memory leak in cache cleanup
- WebSocket reconnection issues

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | 2024-03-28 | Production release with full feature set |
| 0.9.0 | 2024-03-27 | Beta release |

## Migration Guide

### From 0.9.x to 1.0.0

1. **API Endpoint Changes**
   - Use `/api/v1/voice-query` instead of `/api/voice-query` (deprecated)
   - Use `/api/v1/health` for detailed health checks

2. **WebSocket Protocol**
   - Messages now include `api_version` field
   - Heartbeat interval changed from 60s to 30s

3. **Configuration**
   - New environment variables: `OTEL_ENABLED`, `SENTRY_DSN`
   - Rate limit configuration moved to `RATE_LIMIT_PER_MINUTE`

4. **Breaking Changes**
   - Removed `/api/status` endpoint (use `/api/v1/health/summary`)
   - Changed error response format to include `error.code`

## Contributors

- LIGHT HOPE Development Team
- Claude AI Assistant

---

*For detailed commit history, see [GitHub Releases](https://github.com/williampolicy/m537_voice_gateway/releases)*
