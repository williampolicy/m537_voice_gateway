# Changelog

All notable changes to M537 Voice Gateway will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2024-03-29

### Added

#### Enterprise Features
- **API Key Authentication**: Multi-tier rate limiting (free/standard/premium/enterprise)
- **Circuit Breaker**: Automatic fault isolation with configurable thresholds
- **Graceful Shutdown**: Connection draining with cleanup callbacks
- **Usage Analytics**: Query statistics, performance percentiles, trend analysis
- **Webhook Events**: HMAC-signed notifications for system events

#### Observability
- **OpenTelemetry Integration**: Full distributed tracing support
- **Error Tracking**: Sentry integration with error fingerprinting
- **Structured Logging**: Log rotation (main 10MBx5, error 5MBx3, access daily)

#### SDK Enhancements
- **Python SDK**: API Key support, retries with backoff, analytics/webhooks API
- **TypeScript SDK**: Full type definitions, async support, webhook verification

#### Kubernetes
- **Helm Chart v1.1.0**: OpenTelemetry, Sentry, API Key secrets support

#### Documentation
- Milestone reports in `_docs/milestones/`
- Enterprise API SOP in `_docs/sop/`
- Architecture design in `_docs/architecture/`
- Audit reports in `_docs/audit/`
- Lessons learned in `_docs/lessons-learned/`

### Changed
- Main application now integrates all enterprise features
- Enhanced middleware stack with tracing and shutdown support

### Testing
- 282 tests (100% pass rate)
- Security, performance, enterprise feature coverage

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
| 1.1.0 | 2024-03-29 | Enterprise features, SDKs, observability |
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
