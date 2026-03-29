# M537 语音生态入口 (Voice Gateway)

[![CI/CD](https://github.com/lighthope-ai/m537-voice-gateway/actions/workflows/ci.yml/badge.svg)](https://github.com/lighthope-ai/m537-voice-gateway/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

> **版本**: 1.1.0 | **优先级**: P1 | **状态**: Production Ready
> **合规标准**: LIGHT HOPE 生态系统标准 V5.3
> **测试覆盖**: 300 测试 (100% 通过) | **代码行数**: 15,000+
> **端口**: 5537 | **域名**: [voice.x1000.ai](https://voice.x1000.ai)

---

## 核心价值

**构建 LIGHT HOPE 生态的统一语音访问层** —— 让每个用户都能通过自然语言访问属于自己的数据、任务、状态和建议。

这不是"做一个语音功能"，而是**平台级基础设施**。

## 特性亮点

| 功能 | 描述 | 技术实现 |
|------|------|----------|
| 自然语言理解 | 中文语音转意图解析 | 规则引擎 + LLM 降级 |
| 实时响应 | P95 < 100ms | 查询缓存 + 异步执行 |
| 企业级认证 | API Key 多级限流 | free/standard/premium/enterprise |
| 熔断器模式 | 外部服务故障隔离 | Circuit Breaker Pattern |
| 优雅关闭 | 连接排空与清理回调 | Graceful Shutdown |
| 分布式追踪 | OpenTelemetry 集成 | Jaeger/Zipkin 兼容 |
| Webhook 通知 | 事件驱动集成 | HMAC 签名验证 |
| 使用分析 | 实时统计与趋势 | Analytics Dashboard |
| 可观测性 | Prometheus + Sentry | 全链路监控 |

## 快速开始

### 前置要求

- Docker 24.0+
- Docker Compose V2
- 可选: Cloudflare Tunnel (外网访问)

### 一键启动

```bash
# 克隆项目
git clone https://github.com/lighthope-ai/m537-voice-gateway.git
cd m537-voice-gateway

# 复制环境变量
cp .env.example .env

# 启动服务
docker compose up -d --build

# 验证服务
curl http://localhost:5537/health
```

### 访问方式

| 入口 | URL | 说明 |
|------|-----|------|
| Web 前端 | http://localhost:5537 | 语音交互界面 |
| API 文档 | http://localhost:5537/docs | Swagger UI |
| 健康检查 | http://localhost:5537/health | V5.3 规范 |
| Prometheus | http://localhost:5537/api/metrics | 监控指标 |

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        第1层：前端交互层                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  录音按钮   │  │  波形可视化  │  │  语音播报   │              │
│  │  (Web API)  │  │  (Canvas)   │  │  (TTS)      │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        第2层：API网关层                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Rate Limit │  │  Audit Log  │  │  Metrics    │              │
│  │  (60/min)   │  │  (Security) │  │  (Prom)     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  FastAPI: /api/voice-query │ /health │ /metrics                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        第3层：命令解释层                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Input      │  │  Intent     │  │  LLM        │              │
│  │  Sanitizer  │→ │  Parser     │→ │  Fallback   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  规则匹配 (优先) → 意图分类 → 参数提取 → Session 上下文           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        第4层：执行层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Cache      │  │  Query      │  │  Response   │              │
│  │  (LRU+TTL)  │→ │  Executor   │→ │  Builder    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  白名单脚本库 (只读安全): 项目统计、端口检测、系统状态...          │
└─────────────────────────────────────────────────────────────────┘
```

## 支持的语音查询

| # | 问题示例 | 意图 | 缓存TTL |
|---|----------|------|---------|
| 1 | 现在总共有多少个项目？ | count_projects | 60s |
| 2 | 当前有哪些端口在监听？ | list_ports | 30s |
| 3 | 哪些 Docker 容器在运行？ | docker_containers | 30s |
| 4 | CPU、内存、磁盘状态？ | system_status | 30s |
| 5 | 最近 24 小时有什么错误？ | recent_errors | 60s |
| 6 | m536 是什么项目？ | project_summary | 300s |
| 7 | 哪些项目没有 README？ | missing_readme | 600s |
| 8 | 最近 7 天更新了哪些项目？ | recent_updates | 120s |
| 9 | P0 关键服务状态如何？ | p0_health | 30s |
| 10 | 当前有哪些 tmux session？ | tmux_sessions | 30s |

### 多轮对话支持

```
用户: m537是什么项目？
助手: m537 是语音生态入口项目，端口 5537...

用户: 它有哪些依赖？  ← "它" 自动解析为 m537
助手: m537 的依赖包括: fastapi, uvicorn...
```

## API 文档

详细 API 文档请参考 [docs/API.md](docs/API.md)

### 快速示例

```bash
# 语音查询
curl -X POST https://voice.x1000.ai/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript": "现在有多少个项目"}'

# 响应
{
  "success": true,
  "data": {
    "answer_text": "当前共有 327 个项目",
    "intent": "count_projects",
    "confidence": 0.95,
    "cached": false
  },
  "request_id": "req_a1b2c3d4e5f6"
}
```

## 监控与告警

### Grafana Dashboard

项目包含预配置的 Grafana 仪表板，展示：

- 请求速率与成功率
- 响应时间分位数 (P50/P95/P99)
- 意图分布饼图
- 缓存命中率
- LLM 降级统计
- 速率限制触发次数

```bash
# 启动监控栈
cd monitoring
docker compose -f ../docker-compose.yml -f docker-compose.monitoring.yml up -d

# 访问
# Grafana: http://localhost:3000 (admin / m537admin)
# Prometheus: http://localhost:9090
```

### Uptime Kuma 集成

```
监控地址: https://voice.x1000.ai/api/uptime
期望响应: "OK"
检查间隔: 60s
```

## 测试

```bash
# 单元测试
cd backend && pytest tests/ -v

# API 集成测试
./scripts/api_test.sh http://localhost:5537

# 安全测试
./scripts/security_test.sh http://localhost:5537

# 性能基准
python scripts/benchmark.py
```

### 测试覆盖率

| 类型 | 测试数 | 覆盖范围 |
|------|--------|----------|
| 单元测试 | 61 | 意图解析、响应构建、工具执行 |
| API测试 | 23 | 所有端点、错误处理 |
| 安全测试 | 12 | 注入防护、XSS、路径遍历 |

## 技术栈

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 运行时 | Python | 3.11+ | 异步支持 |
| Web框架 | FastAPI | 0.104+ | 高性能异步 |
| 服务器 | Uvicorn | 0.24+ | ASGI |
| 前端 | Vanilla JS | ES6+ | 零依赖 |
| 语音 | Web Speech API | - | 浏览器原生 |
| 可视化 | Web Audio API | - | 波形渲染 |
| 容器 | Docker | 24.0+ | V5.3 标准 |
| 监控 | Prometheus | 2.48+ | 指标采集 |
| 仪表板 | Grafana | 10.2+ | 可视化 |

## V5.3 合规清单

| 要求 | 状态 | 实现 |
|------|------|------|
| 内存限制 | ✅ | 1GB (deploy.resources.limits) |
| 自动重启 | ✅ | unless-stopped |
| 健康检查 | ✅ | /health, interval 30s |
| 日志限制 | ✅ | max-size 10m, max-file 3 |
| README | ✅ | 详细文档 (300+ 行) |
| 版本标识 | ✅ | /api/version 端点 |
| Prometheus | ✅ | /api/metrics 端点 |

## 安全设计

### 防护措施

| 威胁 | 防护 | 实现 |
|------|------|------|
| 命令注入 | 输入消毒 | 移除 ; \| & \` $ ( ) { } < > |
| XSS 攻击 | HTML 转义 | script/event handler 过滤 |
| 暴力攻击 | 速率限制 | Token Bucket 60/min |
| 信息泄露 | 错误抽象 | 无堆栈跟踪返回 |
| 路径遍历 | 路径验证 | 禁止 .. 和编码绕过 |

### 安全边界

**绝对禁止**:
- LLM 直接执行 shell 命令
- 前端直接访问服务器内部
- 未经白名单的任何操作
- 访问敏感路径 (/etc, /root, ~/.ssh)

**允许**:
- 只读查询
- 白名单脚本调用
- 结构化数据返回

## 目录结构

```
m537_voice_gateway/
├── README.md                 # 项目说明
├── docker-compose.yml        # Docker 编排
├── Dockerfile                # 后端镜像
├── pyproject.toml            # Python 项目配置
├── .env.example              # 环境变量模板
├── .github/
│   └── workflows/ci.yml      # GitHub Actions
├── frontend/                 # 前端静态文件
│   ├── index.html
│   ├── css/styles.css
│   └── js/
│       ├── app.js
│       └── voice-visualizer.js
├── backend/                  # 后端 FastAPI
│   ├── main.py               # 应用入口
│   ├── settings.py           # 配置管理
│   ├── routes/               # API 路由
│   │   ├── health.py
│   │   ├── voice.py
│   │   └── metrics.py
│   ├── services/             # 业务逻辑
│   │   ├── intent_parser.py
│   │   ├── query_executor.py
│   │   ├── response_builder.py
│   │   ├── llm_assistant.py
│   │   ├── session_manager.py
│   │   ├── cache.py
│   │   └── audit_logger.py
│   ├── middleware/           # 中间件
│   │   └── rate_limiter.py
│   ├── tools/                # 查询工具
│   └── tests/                # 单元测试
├── scripts/                  # 运维脚本
│   ├── api_test.sh
│   ├── security_test.sh
│   └── benchmark.py
├── monitoring/               # 监控配置
│   ├── grafana-dashboard.json
│   ├── prometheus.yml
│   ├── alerts.yml
│   └── docker-compose.monitoring.yml
└── docs/                     # 文档
    ├── API.md
    ├── DEPLOYMENT.md
    └── ARCHITECTURE.md
```

## 扩展路径

| 版本 | 功能 | 目标 | 状态 |
|------|------|------|------|
| V1.0 | 运维入口 (MVP) | 10 个问题 | ✅ 完成 |
| V1.1 | 多轮对话 | 上下文理解 | ✅ 完成 |
| V1.2 | LLM 降级 | 复杂意图 | ✅ 完成 |
| V1.3 | 学生入口 | 学习查询 | 规划中 |
| V1.4 | 家长入口 | 进度查看 | 规划中 |
| V2.0 | 多场景 | 养老/医疗 | 长期 |

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 代码规范

```bash
# 格式化
ruff format backend/

# 检查
ruff check backend/

# 测试
pytest backend/tests/ -v
```

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系我们

| 渠道 | 信息 |
|------|------|
| 组织 | LIGHT HOPE LLC |
| 邮箱 | info@x1000.ai |
| 地址 | Boston, MA, USA |
| 使命 | EMPOWER GOOD WITH AI |

---

<p align="center">
  <strong>M537 Voice Gateway</strong><br>
  <em>构建语音交互的未来</em><br><br>
  <sub>文档编号: M537-README-V1.1 | 合规标准: LIGHT HOPE V5.3</sub>
</p>
