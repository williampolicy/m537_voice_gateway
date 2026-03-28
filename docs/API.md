# M537 Voice Gateway API 文档

> **版本**: 1.0.0
> **基础URL**: `https://voice.x1000.ai`
> **协议**: HTTPS / WSS
> **标准**: LIGHT HOPE V5.3

---

## 概览

M537 Voice Gateway 提供统一的语音接口，支持自然语言查询服务器和项目状态。

### 认证

当前版本不需要认证。未来版本将支持 API Key 认证。

### 速率限制

| 参数 | 值 |
|------|-----|
| 请求限制 | 60 次/分钟 |
| 突发限制 | 10 次/秒 |
| 超限响应 | HTTP 429 |

---

## 端点列表

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/voice-query` | 语音查询主接口 |
| GET | `/health` | 健康检查 |
| GET | `/api/health` | 健康检查（别名） |
| GET | `/api/version` | 版本信息 |
| GET | `/api/metrics` | Prometheus 指标 |
| GET | `/api/metrics/json` | JSON 格式指标 |
| GET | `/api/uptime` | Uptime Kuma 监控 |
| WS | `/ws` | WebSocket 实时状态 |
| WS | `/ws/metrics` | WebSocket 指标流 |

---

## 语音查询 API

### POST /api/voice-query

处理自然语言查询，返回结构化响应。

#### 请求

```http
POST /api/voice-query HTTP/1.1
Content-Type: application/json

{
    "transcript": "现在有多少个项目",
    "session_id": "optional-session-id",
    "context": {}
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| transcript | string | ✅ | 用户语音文本 (1-500字符) |
| session_id | string | ❌ | 会话ID，用于多轮对话 |
| context | object | ❌ | 额外上下文信息 |

#### 成功响应 (200)

```json
{
    "success": true,
    "data": {
        "answer_text": "当前共有 327 个项目，其中 P0 项目 15 个，P1 项目 42 个",
        "intent": "count_projects",
        "confidence": 0.95,
        "tool_used": "count_projects",
        "raw_data": {
            "total": 327,
            "p0": 15,
            "p1": 42,
            "p2": 120,
            "p3": 150
        },
        "suggestions": [
            "哪些是 P0 项目？",
            "最近更新了哪些项目？"
        ],
        "cached": false
    },
    "error": null,
    "timestamp": "2026-03-26T12:00:00.000Z",
    "request_id": "req_abc123def456"
}
```

#### 未识别意图响应

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "INTENT_NOT_RECOGNIZED",
        "message": "抱歉，我没有理解你的问题。请尝试以下查询方式：",
        "suggestions": [
            "现在有多少个项目？",
            "系统状态怎么样？",
            "当前有哪些端口在监听？"
        ]
    },
    "timestamp": "2026-03-26T12:00:00.000Z",
    "request_id": "req_abc123def456"
}
```

---

## 支持的意图 (17种)

### 项目管理

| 意图 | 关键词 | 示例 |
|------|--------|------|
| count_projects | 多少项目、项目数 | "现在有多少个项目" |
| project_summary | 是什么、介绍 | "m537是什么项目" |
| missing_readme | 没有readme | "哪些项目没有README" |
| recent_updates | 最近更新 | "最近7天更新了什么" |
| git_status | git、代码状态 | "git仓库状态" |

### 系统监控

| 意图 | 关键词 | 示例 |
|------|--------|------|
| system_status | cpu、内存、状态 | "系统状态怎么样" |
| disk_usage | 磁盘、存储 | "磁盘空间够吗" |
| uptime_info | 运行时间 | "系统运行多久了" |
| process_list | 进程、程序 | "有哪些进程在运行" |

### 网络状态

| 意图 | 关键词 | 示例 |
|------|--------|------|
| list_ports | 端口 | "哪些端口在监听" |
| network_info | 网络、ip | "网络状态" |

### 容器服务

| 意图 | 关键词 | 示例 |
|------|--------|------|
| list_containers | docker、容器 | "哪些容器在运行" |
| p0_health | p0、关键服务 | "P0服务状态如何" |
| list_tmux | tmux、会话 | "有哪些tmux会话" |

### 日志分析

| 意图 | 关键词 | 示例 |
|------|--------|------|
| recent_errors | 错误、报错 | "最近有什么错误" |
| service_logs | 日志 | "查看服务日志" |

### 任务调度

| 意图 | 关键词 | 示例 |
|------|--------|------|
| cron_jobs | 定时任务、cron | "有哪些定时任务" |

---

## 健康检查 API

### GET /health

```json
{
    "status": "healthy",
    "version": "1.0.0",
    "project": "m537_voice_gateway",
    "timestamp": "2026-03-26T12:00:00.000Z",
    "ecosystem": "LIGHT HOPE V5.3",
    "uptime_seconds": 86400,
    "checks": {
        "projects_dir_accessible": true
    }
}
```

---

## 指标 API

### GET /api/metrics

Prometheus 格式指标输出。

### GET /api/metrics/json

```json
{
    "requests": {
        "total": 1234,
        "success": 1200,
        "failed": 34,
        "success_rate": "97.2%"
    },
    "latency": {
        "avg_ms": 45.6,
        "min_ms": 12.3,
        "max_ms": 234.5,
        "p95_ms": 89.2
    },
    "cache": {
        "hits": 456,
        "misses": 778,
        "hit_rate": "36.9%"
    }
}
```

---

## WebSocket API

### WS /ws

实时系统状态推送，每5秒更新一次。

```javascript
const ws = new WebSocket('wss://voice.x1000.ai/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.data.system); // {cpu, memory, disk}
};
```

---

## 多轮对话

通过 `session_id` 支持多轮对话，系统会记住上下文。

```bash
# 第一轮
curl -X POST /api/voice-query \
  -d '{"transcript": "m537是什么项目", "session_id": "sess_123"}'

# 第二轮 - "它"会自动解析为m537
curl -X POST /api/voice-query \
  -d '{"transcript": "它有多少个文件", "session_id": "sess_123"}'
```

支持的代词：`它`、`这个`、`那个`、`这个项目`、`那个项目`

---

## 错误码

| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| INTENT_NOT_RECOGNIZED | 200 | 意图未识别 |
| EXECUTION_FAILED | 200 | 工具执行失败 |
| VALIDATION_ERROR | 422 | 参数验证失败 |
| RATE_LIMITED | 429 | 速率限制 |
| INTERNAL_ERROR | 500 | 内部错误 |

---

## 使用示例

### cURL

```bash
curl -X POST https://voice.x1000.ai/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript": "现在有多少个项目"}'
```

### Python

```python
import requests

result = requests.post(
    'https://voice.x1000.ai/api/voice-query',
    json={'transcript': '系统状态怎么样'}
).json()

print(result['data']['answer_text'])
```

### JavaScript

```javascript
const result = await fetch('/api/voice-query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transcript: '系统状态怎么样' })
}).then(r => r.json());

console.log(result.data.answer_text);
```

---

*文档编号: M537-API-V1.0 | 合规标准: LIGHT HOPE V5.3*
