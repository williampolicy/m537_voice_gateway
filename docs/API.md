# M537 Voice Gateway - API 文档

> 版本: 1.0.0 | 标准: LIGHT HOPE V5.3

## 概述

M537 Voice Gateway 提供语音查询接口，支持自然语言访问服务器状态和项目信息。

## 基础信息

- **基础 URL**: `http://localhost:5537` 或 `https://voice.x1000.ai`
- **内容类型**: `application/json`
- **字符编码**: UTF-8

---

## 接口列表

### 1. 语音查询 (主接口)

**POST** `/api/voice-query`

将语音转文字后的文本发送到后端进行意图解析和查询执行。

#### 请求体

```json
{
    "transcript": "现在有多少个项目",
    "session_id": "optional-session-id",
    "context": {}
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| transcript | string | 是 | 语音转文字结果，1-500 字符 |
| session_id | string | 否 | 会话 ID，用于上下文追踪 |
| context | object | 否 | 额外上下文信息 |

#### 成功响应

```json
{
    "success": true,
    "data": {
        "answer_text": "当前共有 138 个项目，其中 P0 项目 0 个，P1 项目 2 个，P2 项目 0 个，P3 项目 136 个。",
        "intent": "count_projects",
        "confidence": 0.95,
        "tool_used": "count_projects",
        "raw_data": {
            "total": 138,
            "p0": 0,
            "p1": 2,
            "p2": 0,
            "p3": 136
        },
        "suggestions": [
            "哪些是 P0 项目？",
            "最近更新了哪些项目？"
        ]
    },
    "error": null,
    "timestamp": "2026-03-25T03:16:39.646858Z",
    "request_id": "req_2eb8134a0ee4"
}
```

#### 错误响应

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "INTENT_NOT_RECOGNIZED",
        "message": "抱歉，我没有理解你的问题。",
        "suggestions": [
            "现在有多少个项目？",
            "系统状态怎么样？"
        ]
    },
    "timestamp": "2026-03-25T03:16:39.646858Z",
    "request_id": "req_abc123"
}
```

---

### 2. 健康检查

**GET** `/api/health` 或 `/health`

检查服务运行状态，用于容器健康检查和监控。

#### 响应

```json
{
    "status": "healthy",
    "version": "1.0.0",
    "project": "m537_voice_gateway",
    "timestamp": "2026-03-25T03:17:34.928545Z",
    "ecosystem": "LIGHT HOPE V5.3",
    "uptime_seconds": 3690,
    "checks": {
        "projects_dir_accessible": true
    }
}
```

---

### 3. Prometheus 指标

**GET** `/api/metrics`

返回 Prometheus 格式的监控指标。

#### 响应

```text
# HELP m537_requests_total Total number of voice queries
# TYPE m537_requests_total counter
m537_requests_total{status="success"} 42
m537_requests_total{status="error"} 3

# HELP m537_request_duration_seconds Request duration in seconds
# TYPE m537_request_duration_seconds histogram
m537_request_duration_seconds_bucket{le="0.1"} 35
m537_request_duration_seconds_bucket{le="0.5"} 40
m537_request_duration_seconds_bucket{le="1.0"} 45
```

---

## 支持的查询意图

| 意图 | 关键词示例 | 工具 |
|------|-----------|------|
| count_projects | "有多少个项目" | count_projects |
| list_ports | "哪些端口" | list_ports |
| list_containers | "容器在运行" | list_containers |
| system_status | "系统状态"、"CPU" | system_status |
| recent_errors | "有什么错误" | recent_errors |
| project_summary | "m536是什么" | get_project_summary |
| missing_readme | "没有README" | scan_missing_readme |
| recent_updates | "最近更新" | recent_updates |
| p0_health | "P0服务" | p0_health_check |
| list_tmux | "tmux会话" | list_tmux |

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| INTENT_NOT_RECOGNIZED | 无法识别用户意图 |
| TOOL_EXECUTION_FAILED | 工具执行失败 |
| INVALID_PROJECT_ID | 无效的项目编号 |
| RATE_LIMIT_EXCEEDED | 请求频率超限 |
| INTERNAL_ERROR | 内部服务错误 |

---

## 使用示例

### cURL

```bash
# 查询项目数量
curl -X POST http://localhost:5537/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript": "现在有多少个项目"}'

# 健康检查
curl http://localhost:5537/health
```

### JavaScript

```javascript
const response = await fetch('/api/voice-query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transcript: '系统状态怎么样' })
});
const data = await response.json();
console.log(data.data.answer_text);
```

### Python

```python
import requests

response = requests.post(
    'http://localhost:5537/api/voice-query',
    json={'transcript': '最近有什么错误'}
)
print(response.json()['data']['answer_text'])
```

---

*LIGHT HOPE V5.3 Compliant*
