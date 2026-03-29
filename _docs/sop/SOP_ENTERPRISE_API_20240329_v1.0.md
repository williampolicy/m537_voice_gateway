# SOP: 企业级 API 服务开发标准

## 文档信息

| 属性 | 值 |
|------|-----|
| **文档编号** | SOP-API-001 |
| **版本** | v1.0 |
| **创建日期** | 2024-03-29 |
| **验证状态** | ✅ 已验证 (M537 项目) |
| **适用范围** | FastAPI 企业级 API 开发 |

---

## 1. 概述

本 SOP 定义了企业级 API 服务的开发标准流程，基于 M537 Voice Gateway 项目的成功实践提炼而成。

### 1.1 适用场景

- RESTful API 服务开发
- 需要高可用性的生产系统
- 需要完整可观测性的服务
- 多语言/多地区服务

### 1.2 前置条件

- Python 3.11+
- FastAPI 框架
- Docker 环境
- Git 版本控制

---

## 2. 项目结构标准

### 2.1 目录结构

```
project/
├── backend/                 # 后端代码
│   ├── main.py             # 应用入口
│   ├── settings.py         # 配置管理
│   ├── routes/             # API 路由
│   │   ├── __init__.py
│   │   ├── v1/             # 版本化路由
│   │   └── health.py       # 健康检查
│   ├── services/           # 业务逻辑
│   ├── middleware/         # 中间件
│   ├── auth.py             # 认证模块
│   ├── tracing.py          # 追踪模块
│   ├── error_tracking.py   # 错误追踪
│   ├── circuit_breaker.py  # 熔断器
│   ├── graceful_shutdown.py# 优雅关闭
│   ├── analytics.py        # 分析模块
│   └── webhooks.py         # Webhook
├── frontend/               # 前端代码 (可选)
├── tests/                  # 测试代码
│   ├── test_*.py          # 测试文件
│   └── conftest.py        # 测试配置
├── _docs/                  # 项目文档
│   ├── milestones/        # 里程碑
│   ├── sop/               # SOP 文档
│   ├── standards/         # 标准规范
│   └── audit/             # 审计记录
├── helm/                   # Kubernetes 部署
├── clients/                # 客户端 SDK
├── scripts/                # 工具脚本
├── Dockerfile              # 容器构建
├── docker-compose.yml      # 本地开发
├── pyproject.toml          # 项目配置
├── CHANGELOG.md            # 变更日志
└── README.md               # 项目说明
```

---

## 3. 核心模块标准

### 3.1 API 版本控制

**标准**: 所有 API 必须版本化

```python
# routes/v1/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/v1")
router.include_router(voice_router, tags=["voice-v1"])
router.include_router(health_router, tags=["health-v1"])
```

**要求**:
- 使用 `/api/v1/` 前缀
- 响应包含 `api_version` 字段
- 支持版本协商头

### 3.2 认证模块

**标准**: 支持 API Key 认证

```python
# auth.py 核心组件
class APIKeyManager:
    - generate_key()      # 生成密钥
    - validate_key()      # 验证密钥
    - check_rate_limit()  # 限流检查
    - revoke_key()        # 吊销密钥

RATE_LIMIT_TIERS = {
    "free": 30,
    "standard": 60,
    "premium": 300,
    "enterprise": 1000
}
```

### 3.3 熔断器模式

**标准**: 外部调用必须使用熔断器

```python
# circuit_breaker.py 使用
from circuit_breaker import circuit_breaker

@circuit_breaker("external_api", failure_threshold=5)
async def call_external_service():
    ...
```

**配置**:
- failure_threshold: 5 次失败触发
- timeout: 30 秒恢复尝试
- half_open_max_calls: 3 次测试

### 3.4 优雅关闭

**标准**: 必须支持优雅关闭

```python
# graceful_shutdown.py 核心流程
1. 停止接受新请求 (返回 503)
2. 等待现有请求完成 (drain_timeout)
3. 执行清理回调
4. 关闭服务
```

### 3.5 健康检查

**标准**: 三级健康检查

| 端点 | 用途 | 检查项 |
|------|------|--------|
| `/health/live` | K8s 存活探针 | 进程存活 |
| `/health/ready` | K8s 就绪探针 | 依赖就绪 |
| `/health/deep` | 深度检查 | CPU/内存/磁盘/网络 |

---

## 4. 可观测性标准

### 4.1 日志标准

```python
# logging_config.py 配置
- 主日志: 10MB x 5 轮转
- 错误日志: 5MB x 3 轮转
- 访问日志: 按天轮转, 30天保留

格式:
%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s
```

### 4.2 指标标准

```python
# 必须暴露的指标
- request_count_total
- request_duration_seconds
- error_count_total
- active_connections
- cache_hit_ratio
```

### 4.3 追踪标准

```python
# tracing.py 使用
@trace_function("operation_name")
async def business_operation():
    with trace_block("sub_operation"):
        ...
```

---

## 5. 安全标准

### 5.1 必须实现的安全措施

| 措施 | 实现方式 |
|------|----------|
| XSS 防护 | 输入清理 + CSP 头 |
| CSRF 防护 | Token 验证 |
| 注入防护 | 参数化查询 |
| 速率限制 | 令牌桶算法 |
| 安全头 | SecurityHeadersMiddleware |

### 5.2 安全头配置

```python
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000
```

---

## 6. 测试标准

### 6.1 测试覆盖要求

| 类型 | 覆盖率 | 必须覆盖 |
|------|--------|----------|
| 单元测试 | > 80% | 核心业务逻辑 |
| 集成测试 | > 60% | API 端点 |
| 安全测试 | 100% | OWASP Top 10 |
| 性能测试 | 关键路径 | 响应时间 < 100ms |

### 6.2 测试命名规范

```python
# test_{module}.py
class Test{Feature}:
    def test_{action}_{expected_result}(self):
        ...
```

---

## 7. 部署标准

### 7.1 Docker 构建

```dockerfile
# 多阶段构建
FROM python:3.12-slim AS builder
# ... 构建阶段

FROM python:3.12-slim AS production
# ... 生产阶段
USER appuser  # 非 root 运行
```

### 7.2 Kubernetes 部署

必须配置:
- HorizontalPodAutoscaler
- PodDisruptionBudget
- ResourceQuota
- NetworkPolicy

---

## 8. 文档标准

### 8.1 必须文档

| 文档 | 位置 | 更新频率 |
|------|------|----------|
| API 文档 | docs/API.md | 每次 API 变更 |
| 开发指南 | docs/DEVELOPMENT.md | 季度 |
| 变更日志 | CHANGELOG.md | 每次发布 |
| 里程碑 | _docs/milestones/ | 重大版本 |

### 8.2 文档命名规范

```
{TYPE}_{PROJECT}_{DATE}_{VERSION}.md

示例:
MILESTONE_v1.0.0_20240329_001.md
SOP_ENTERPRISE_API_20240329_v1.0.md
```

---

## 9. 验证清单

### 9.1 发布前检查

- [ ] 所有测试通过
- [ ] 安全扫描无高危
- [ ] 文档已更新
- [ ] CHANGELOG 已更新
- [ ] 版本号已更新
- [ ] 健康检查正常
- [ ] 指标导出正常
- [ ] 日志格式正确

### 9.2 上线后检查

- [ ] 健康检查端点响应
- [ ] 日志正常输出
- [ ] 指标正常采集
- [ ] 告警规则生效
- [ ] 回滚方案就绪

---

## 10. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2024-03-29 | 初始版本，基于 M537 项目验证 |

---

**文档结束**

*基于 M537 Voice Gateway 项目实践验证 | LIGHT HOPE LLC*
