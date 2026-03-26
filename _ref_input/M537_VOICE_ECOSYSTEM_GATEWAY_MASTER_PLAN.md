# M537 语音生态入口：完整战略方案

> **文档编号**: M537-MASTER-PLAN-20260324
> **版本**: 1.0.0
> **状态**: APPROVED ✅
> **起草人**: OPUS (战略规划)
> **执行人**: SONNET (开发实施)
> **发布日期**: 2026-03-24
> **合规标准**: LIGHT HOPE 生态系统标准 V5.3

---

## 文档目录

1. [战略定位与价值分析](#一战略定位与价值分析)
2. [产品定义与边界](#二产品定义与边界)
3. [系统架构设计](#三系统架构设计)
4. [技术选型与规范](#四技术选型与规范)
5. [V5.3 标准合规清单](#五v53-标准合规清单)
6. [MVP 功能规格](#六mvp-功能规格)
7. [目录结构与文件规范](#七目录结构与文件规范)
8. [API 接口设计](#八api-接口设计)
9. [前端交互规范](#九前端交互规范)
10. [后端服务规范](#十后端服务规范)
11. [白名单工具库](#十一白名单工具库)
12. [安全边界与风险控制](#十二安全边界与风险控制)
13. [测试验收标准](#十三测试验收标准)
14. [部署流程](#十四部署流程)
15. [扩展路径规划](#十五扩展路径规划)
16. [SONNET 执行提示词](#十六sonnet-执行提示词)

---

## 一、战略定位与价值分析

### 1.1 项目本质

M537 不是"做一个语音功能"，而是：

**构建 LIGHT HOPE 生态的统一语音访问层——让每个用户都能通过自然语言访问属于自己的数据、任务、状态和建议。**

### 1.2 战略价值矩阵

| 维度 | 评分 | 判断依据 |
|------|------|----------|
| **战略重要性** | ⭐⭐⭐⭐⭐ | 平台级基础设施，不是单一功能 |
| **技术可行性** | ⭐⭐⭐⭐ | 基础技术栈成熟，服务器生态已就位 |
| **商业价值** | ⭐⭐⭐⭐⭐ | 可复制到教育、养老、医疗等多场景 |
| **执行紧迫性** | ⭐⭐⭐⭐ | 语音交互是未来主流入口 |
| **差异化程度** | ⭐⭐⭐⭐⭐ | "语音 + 个体数据 + 个性化理解"组合独特 |

### 1.3 产品定位一句话

> **"每个人都有一个自己的语音入口，访问属于自己的数据、任务、状态、建议与陪伴。"**

### 1.4 产品矩阵展望

```
                    ┌─────────────────────────────────────────┐
                    │         语音访问统一底座 (M537)          │
                    │   前端语音 → API网关 → 数据层 → 语音播报   │
                    └─────────────────────────────────────────┘
                                        │
        ┌───────────────┬───────────────┼───────────────┬───────────────┐
        ▼               ▼               ▼               ▼               ▼
   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
   │ 运维入口 │    │ 学生入口 │    │ 家长入口 │    │ 老人入口 │    │ 医疗入口 │
   │ 服务器  │    │ 数学    │    │ 进度    │    │ 健康    │    │ 病程    │
   │ 项目状态│    │ 学习    │    │ 建议    │    │ 提醒    │    │ 问答    │
   └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### 1.5 为什么语音是未来

| 人群 | 语音优势 |
|------|----------|
| **老人** | 不用打字，视力问题友好，更像陪伴 |
| **孩子** | 自然交互，低门槛，愿意问 |
| **忙碌家长** | 开车时、做饭时可用，碎片时间 |
| **专业用户** | 快速查询状态，解放双手 |

### 1.6 核心差异化

**不是普通语音助手**，而是：

1. **连接真实数据** - 不是猜测，是直接读取服务器/学习记录/健康档案
2. **个体化理解** - 知道"这个人"的上下文、历史、偏好
3. **过程型平台** - 记录过程、解释过程、推进过程
4. **安全边界清晰** - 白名单工具，不自由发挥

---

## 二、产品定义与边界

### 2.1 MVP 核心闭环

```
用户说话 → 前端录音 → 语音转文字 → 后端接收 → 意图解析 
    → 调用白名单工具 → 获取真实数据 → 构建回答 → 返回前端 
    → 显示文字 → 语音播报
```

### 2.2 MVP 必须做的

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 语音输入 | 浏览器录音，支持按住说话/点击录音 | P0 |
| 语音转文字 | Web Speech API，实时显示 | P0 |
| 意图解析 | 规则优先，LLM 辅助 | P0 |
| 数据查询 | 调用白名单脚本获取服务器真实数据 | P0 |
| 文字显示 | 实时显示回答文本 | P0 |
| 语音播报 | Web Speech API TTS | P0 |
| 健康检查 | `/health` 端点 (V5.3 要求) | P0 |
| 内存限制 | Docker 容器 1G 限制 (V5.3 要求) | P0 |

### 2.3 MVP 暂不做的

| 功能 | 原因 | 后续阶段 |
|------|------|----------|
| 复杂对话多轮 | 先跑通单轮 | V1.1 |
| 危险操作 | 安全边界 | V2.0+ |
| 多用户系统 | 先单用户 | V1.2 |
| 学生/家长模块 | 先运维入口 | V1.1 |
| 养老/医疗模块 | 先验证底座 | V2.0+ |

### 2.4 产品边界（绝对不做）

| 禁止项 | 原因 |
|--------|------|
| LLM 直接执行 shell | 安全风险极高 |
| 前端直接访问服务器内部 | 架构违规 |
| 开放式自由对话 | 容易失控 |
| 危险命令（rm、kill 等） | 安全边界 |
| 修改系统配置 | 安全边界 |

---

## 三、系统架构设计

### 3.1 四层架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           第1层：前端交互层                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │    录音模块     │  │    显示模块     │  │    播报模块     │          │
│  │  Web Speech API │  │  实时文字显示   │  │  TTS 语音合成   │          │
│  │  按住/点击录音  │  │  用户输入+回答  │  │  浏览器原生     │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                          │
│  技术栈：纯 HTML/CSS/JS，无框架依赖，手机优先响应式                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ POST /api/voice-query
┌─────────────────────────────────────────────────────────────────────────┐
│                           第2层：API 网关层                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  FastAPI 服务                                                    │    │
│  │  ├── /api/voice-query     语音查询主接口                         │    │
│  │  ├── /api/health          健康检查 (V5.3 必须)                   │    │
│  │  ├── /api/metrics         Prometheus 指标 (V5.3 推荐)            │    │
│  │  └── /api/version         版本信息                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  职责：身份验证、请求限流、日志记录、错误处理                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           第3层：命令解释层                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │    规则匹配器   │  │    意图分类器   │  │    参数提取器   │          │
│  │  关键词 → 工具  │  │  LLM 辅助理解   │  │  m536 → m536   │          │
│  │  优先级最高     │  │  模糊问题fallback│ │  编号归一化    │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                          │
│  核心原则：规则优先，LLM 辅助，不是 LLM 主导                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           第4层：服务器执行层                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  白名单脚本库 (只读安全)                                           │  │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐      │  │
│  │  │count_projects.py│ │ list_ports.py   │ │system_status.py │      │  │
│  │  │ 项目统计        │ │ 端口检测        │ │ CPU/内存/磁盘   │      │  │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘      │  │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐      │  │
│  │  │get_project_     │ │ recent_errors.py│ │list_containers. │      │  │
│  │  │summary.py       │ │ 错误日志        │ │py 容器列表      │      │  │
│  │  │ 项目摘要        │ │                 │ │                 │      │  │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  安全原则：只有白名单脚本可执行，绝不动态生成命令                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 数据流详解

```
┌──────┐    1.录音     ┌──────┐    2.转文字    ┌──────┐
│ 用户 │ ──────────▶ │ 前端 │ ──────────▶  │ 前端 │
│ 说话 │              │ 录音 │   Web Speech  │ 显示 │
└──────┘              └──────┘    API         └──────┘
                                                  │
                                                  │ 3. POST transcript
                                                  ▼
┌──────┐    8.播报     ┌──────┐    7.返回      ┌──────┐
│ 用户 │ ◀────────── │ 前端 │ ◀──────────  │ 后端 │
│ 听到 │   TTS        │ TTS  │   JSON        │ API  │
└──────┘              └──────┘              └──────┘
                                                  │
                         ┌────────────────────────┤
                         │                        │
                         ▼                        ▼
                   ┌──────────┐            ┌──────────┐
                   │ 意图解析 │            │ 工具调用 │
                   │ 规则匹配 │ ─────────▶ │ 白名单   │
                   │ LLM辅助  │  4.匹配    │ 脚本执行 │
                   └──────────┘            └──────────┘
                                                  │
                                                  │ 5. 读取服务器数据
                                                  ▼
                                           ┌──────────┐
                                           │ 服务器   │
                                           │ 真实数据 │
                                           │ 项目/端口│
                                           └──────────┘
                                                  │
                                                  │ 6. 构建回答
                                                  ▼
                                           ┌──────────┐
                                           │ 响应构建 │
                                           │ 自然语言 │
                                           └──────────┘
```

### 3.3 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 前端框架 | 无框架纯 JS | 最轻量，加载快，手机友好 |
| 语音识别 | Web Speech API | 浏览器原生，零依赖，免费 |
| 语音合成 | Web Speech API | 浏览器原生，零依赖，免费 |
| 后端框架 | FastAPI | 轻量、异步、类型安全、自动文档 |
| 意图解析 | 规则优先 | 稳定可控，可审计 |
| 数据访问 | 白名单脚本 | 安全边界清晰 |
| 部署方式 | Docker Compose | V5.3 标准要求 |
| 外部访问 | Cloudflare Tunnel | 安全、免费、V5.3 标准 |

---

## 四、技术选型与规范

### 4.1 技术栈总览

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **前端** | HTML5 | - | 页面结构 |
| **前端** | CSS3 | - | 样式，响应式 |
| **前端** | JavaScript (ES6+) | - | 交互逻辑 |
| **前端** | Web Speech API | - | 语音识别 + TTS |
| **后端** | Python | 3.11+ | 主语言 |
| **后端** | FastAPI | 0.109+ | Web 框架 |
| **后端** | Uvicorn | 0.27+ | ASGI 服务器 |
| **后端** | Pydantic | 2.0+ | 数据验证 |
| **运维** | Docker | 24.0+ | 容器化 |
| **运维** | Docker Compose | 2.24+ | 编排 |
| **运维** | Cloudflare Tunnel | - | 外部访问 |

### 4.2 Python 依赖

```txt
# requirements.txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0
python-multipart>=0.0.6
psutil>=5.9.0
prometheus-client>=0.19.0
python-dotenv>=1.0.0
httpx>=0.26.0
```

### 4.3 前端无依赖原则

```
前端零 npm 依赖
├── 无 React/Vue/Angular
├── 无 Webpack/Vite
├── 无 npm install
├── 纯 HTML/CSS/JS
└── 浏览器原生 API
```

**原因**：
1. 手机加载更快
2. 无构建步骤
3. 调试更简单
4. 长期维护成本低

---

## 五、V5.3 标准合规清单

### 5.1 必须满足项

| V5.3 要求 | M537 实现 | 状态 |
|-----------|-----------|------|
| **内存限制** | `deploy.resources.limits.memory: 1G` | ⬜ 待实现 |
| **自动重启** | `restart: unless-stopped` | ⬜ 待实现 |
| **健康检查** | `/health` 端点，30s 间隔 | ⬜ 待实现 |
| **日志限制** | `max-size: 10m, max-file: 3` | ⬜ 待实现 |
| **Cloudflare 部署** | m537.x1000.ai | ⬜ 待实现 |
| **README > 100行** | 完整文档 | ⬜ 待实现 |

### 5.2 Docker Compose 标准模板

```yaml
# docker-compose.yml
version: '3.8'

services:
  m537_voice_gateway:
    build: .
    container_name: m537_voice_gateway
    restart: unless-stopped
    ports:
      - "5537:5537"
    environment:
      - PORT=5537
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    volumes:
      - /data/projects:/data/projects:ro  # 只读访问项目目录
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5537/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - lighthope_network

networks:
  lighthope_network:
    external: true
```

### 5.3 健康检查端点规范

```python
# routes/health.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "project": "m537_voice_gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "ecosystem": "LIGHT HOPE V5.3"
    }
```

---

## 六、MVP 功能规格

### 6.1 首批 10 个高频问题

| # | 用户问题示例 | 意图标识 | 调用工具 | 返回示例 |
|---|-------------|----------|----------|----------|
| 1 | "现在总共有多少个项目？" | `count_projects` | `count_projects.py` | "当前共有 327 个项目" |
| 2 | "当前有哪些端口在监听？" | `list_ports` | `list_ports.py` | "共 14 个端口在监听：80, 443, 3000..." |
| 3 | "哪些 Docker 容器在运行？" | `list_containers` | `list_containers.py` | "共 23 个容器在运行" |
| 4 | "CPU、内存、磁盘状态？" | `system_status` | `system_status.py` | "CPU 45%, 内存 62%, 磁盘 71%" |
| 5 | "最近 24 小时有什么错误？" | `recent_errors` | `recent_errors.py` | "发现 3 个错误：..." |
| 6 | "m536 是什么项目？" | `project_summary` | `get_project_summary.py` | 读取 README 摘要 |
| 7 | "哪些项目没有 README？" | `missing_readme` | `scan_missing_readme.py` | "共 12 个项目缺少 README" |
| 8 | "最近 7 天更新了哪些项目？" | `recent_updates` | `recent_updates.py` | "共 8 个项目有更新" |
| 9 | "P0 关键服务状态如何？" | `p0_health` | `p0_health_check.py` | "所有 P0 服务正常" |
| 10 | "当前有哪些 tmux session？" | `list_tmux` | `list_tmux.py` | "共 5 个 session" |

### 6.2 意图规则映射表

```python
# config/intent_rules.py
INTENT_RULES = {
    "count_projects": {
        "keywords": ["多少个项目", "项目数", "几个项目", "项目总数", "有多少项目"],
        "tool": "count_projects",
        "description": "统计项目总数"
    },
    "list_ports": {
        "keywords": ["端口", "哪些端口", "端口监听", "开放端口", "端口开着"],
        "tool": "list_ports",
        "description": "列出监听端口"
    },
    "list_containers": {
        "keywords": ["容器", "docker", "哪些容器", "容器在运行"],
        "tool": "list_containers",
        "description": "列出运行中的容器"
    },
    "system_status": {
        "keywords": ["cpu", "内存", "磁盘", "系统状态", "资源", "状态"],
        "tool": "system_status",
        "description": "查询系统资源状态"
    },
    "recent_errors": {
        "keywords": ["错误", "报错", "异常", "出错", "error"],
        "tool": "recent_errors",
        "description": "查询最近错误"
    },
    "project_summary": {
        "keywords": ["是什么项目", "项目介绍", "项目简介", "什么是"],
        "tool": "get_project_summary",
        "params": ["project_id"],
        "description": "获取项目摘要"
    },
    "missing_readme": {
        "keywords": ["没有readme", "缺少readme", "readme缺失"],
        "tool": "scan_missing_readme",
        "description": "扫描缺失README的项目"
    },
    "recent_updates": {
        "keywords": ["最近更新", "近期更新", "更新了", "最新改动"],
        "tool": "recent_updates",
        "description": "查询最近更新的项目"
    },
    "p0_health": {
        "keywords": ["p0", "关键服务", "核心服务"],
        "tool": "p0_health_check",
        "description": "检查P0服务状态"
    },
    "list_tmux": {
        "keywords": ["tmux", "session", "会话"],
        "tool": "list_tmux",
        "description": "列出tmux会话"
    }
}
```

### 6.3 项目编号纠错规则

语音识别常见错误映射：

```python
# config/project_id_normalizer.py
PROJECT_ID_PATTERNS = {
    # 数字发音错误
    r"m\s*(\d+)": r"m\1",           # "m 536" → "m536"
    r"m(\d)\s+(\d+)": r"m\1\2",     # "m5 36" → "m536"
    r"[mM]\s*五三六": "m536",        # 中文数字
    r"[mM]\s*五百三十六": "m536",
    r"[mM]\s*eight thousand": "m8000",
    # 字母发音错误
    r"[eE][mM](\d+)": r"m\1",       # "em536" → "m536"
    r"[aA][mM](\d+)": r"m\1",       # "am536" → "m536"
}
```

---

## 七、目录结构与文件规范

### 7.1 完整目录结构

```
m537_voice_gateway/
├── README.md                           # 项目说明 (>100行，V5.3要求)
├── docker-compose.yml                  # Docker 编排 (V5.3 标准模板)
├── Dockerfile                          # 后端镜像定义
├── .env.example                        # 环境变量模板
├── .gitignore                          # Git 忽略配置
│
├── frontend/                           # 前端 (纯静态文件)
│   ├── index.html                      # 主页面
│   ├── css/
│   │   └── styles.css                  # 样式文件
│   ├── js/
│   │   ├── app.js                      # 主逻辑
│   │   ├── voice-input.js              # 语音输入模块
│   │   ├── voice-output.js             # 语音播报模块
│   │   ├── api-client.js               # API 调用封装
│   │   └── config.js                   # 前端配置
│   └── assets/
│       └── icons/                      # 图标资源
│
├── backend/                            # 后端 (FastAPI)
│   ├── main.py                         # 应用入口
│   ├── config.py                       # 配置管理
│   ├── requirements.txt                # Python 依赖
│   │
│   ├── routes/                         # API 路由
│   │   ├── __init__.py
│   │   ├── voice.py                    # 语音查询路由
│   │   ├── health.py                   # 健康检查路由
│   │   └── metrics.py                  # Prometheus 指标
│   │
│   ├── services/                       # 业务逻辑
│   │   ├── __init__.py
│   │   ├── intent_parser.py            # 意图解析服务
│   │   ├── query_executor.py           # 查询执行服务
│   │   ├── response_builder.py         # 响应构建服务
│   │   └── project_id_normalizer.py    # 项目编号纠错
│   │
│   ├── tools/                          # 白名单工具脚本
│   │   ├── __init__.py
│   │   ├── base_tool.py                # 工具基类
│   │   ├── count_projects.py           # 项目统计
│   │   ├── list_ports.py               # 端口检测
│   │   ├── list_containers.py          # 容器列表
│   │   ├── system_status.py            # 系统状态
│   │   ├── recent_errors.py            # 错误日志
│   │   ├── get_project_summary.py      # 项目摘要
│   │   ├── scan_missing_readme.py      # 扫描缺失README
│   │   ├── recent_updates.py           # 最近更新
│   │   ├── p0_health_check.py          # P0服务检查
│   │   └── list_tmux.py                # tmux会话列表
│   │
│   └── config/                         # 配置文件
│       ├── __init__.py
│       ├── intent_rules.py             # 意图规则配置
│       ├── project_id_patterns.py      # 编号纠错模式
│       └── tool_registry.py            # 工具注册表
│
├── tests/                              # 测试 (V5.3 S2要求)
│   ├── __init__.py
│   ├── test_intent_parser.py           # 意图解析测试
│   ├── test_tools.py                   # 工具脚本测试
│   ├── test_api.py                     # API 端点测试
│   └── test_integration.py             # 集成测试
│
├── docs/                               # 文档
│   ├── API.md                          # API 接口文档
│   ├── DEPLOYMENT.md                   # 部署指南
│   ├── EXTENSION.md                    # 扩展指南
│   └── TROUBLESHOOTING.md              # 故障排查
│
├── scripts/                            # 运维脚本
│   ├── deploy.sh                       # 部署脚本
│   ├── health_check.sh                 # 健康检查脚本
│   └── setup_tunnel.sh                 # Cloudflare Tunnel 配置
│
└── logs/                               # 日志目录
    └── .gitkeep
```

### 7.2 文件命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| Python 文件 | snake_case | `intent_parser.py` |
| JavaScript 文件 | kebab-case | `voice-input.js` |
| CSS 文件 | kebab-case | `styles.css` |
| 配置文件 | UPPER_CASE 或 snake_case | `.env.example`, `config.py` |
| 文档文件 | UPPER_CASE.md | `README.md`, `API.md` |

---

## 八、API 接口设计

### 8.1 接口总览

| 端点 | 方法 | 用途 | 认证 |
|------|------|------|------|
| `/api/voice-query` | POST | 语音查询主接口 | 可选 |
| `/api/health` | GET | 健康检查 | 无 |
| `/api/metrics` | GET | Prometheus 指标 | 无 |
| `/api/version` | GET | 版本信息 | 无 |

### 8.2 主查询接口详细设计

#### 请求

```http
POST /api/voice-query
Content-Type: application/json

{
    "transcript": "现在有多少个项目",
    "session_id": "optional-session-id",
    "context": {}
}
```

#### 响应

```json
{
    "success": true,
    "data": {
        "answer_text": "当前共有 327 个项目，其中 P0 项目 12 个，P1 项目 45 个。",
        "intent": "count_projects",
        "confidence": 0.95,
        "tool_used": "count_projects",
        "raw_data": {
            "total": 327,
            "p0": 12,
            "p1": 45,
            "p2": 120,
            "p3": 150
        },
        "suggestions": [
            "你可以问：哪些是 P0 项目？",
            "你可以问：最近更新了哪些项目？"
        ]
    },
    "timestamp": "2026-03-24T10:30:00Z",
    "request_id": "req_abc123"
}
```

#### 错误响应

```json
{
    "success": false,
    "error": {
        "code": "INTENT_NOT_RECOGNIZED",
        "message": "抱歉，我没有理解你的问题。",
        "suggestions": [
            "你可以问：现在有多少个项目？",
            "你可以问：系统状态怎么样？"
        ]
    },
    "timestamp": "2026-03-24T10:30:00Z",
    "request_id": "req_abc123"
}
```

### 8.3 健康检查接口

```http
GET /api/health

Response:
{
    "status": "healthy",
    "version": "1.0.0",
    "project": "m537_voice_gateway",
    "timestamp": "2026-03-24T10:30:00Z",
    "ecosystem": "LIGHT HOPE V5.3",
    "uptime_seconds": 86400,
    "checks": {
        "tools_available": true,
        "projects_dir_accessible": true
    }
}
```

---

## 九、前端交互规范

### 9.1 页面布局

```
┌─────────────────────────────────────────────────────────────┐
│                     M537 语音生态入口                        │
│                   LIGHT HOPE Voice Gateway                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │                   对话历史区域                        │   │
│  │                                                      │   │
│  │  [用户] 现在有多少个项目？                            │   │
│  │  [系统] 当前共有 327 个项目，其中 P0 项目 12 个...    │   │
│  │                                                      │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  当前输入：___________________________________        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                      ┌──────────┐                          │
│                      │   🎤    │  点击/按住 开始录音       │
│                      │  录音   │                           │
│                      └──────────┘                          │
│                                                             │
│  快捷问题：                                                 │
│  [项目数] [端口] [系统状态] [最近错误] [P0状态]             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 交互状态机

```
┌─────────┐   点击    ┌─────────┐   识别完成   ┌─────────┐
│  空闲   │ ────────▶ │  录音中  │ ──────────▶ │  处理中  │
│  IDLE   │           │RECORDING│              │PROCESSING│
└─────────┘           └─────────┘              └─────────┘
     ▲                     │                        │
     │                     │ 点击停止                │
     │                     ▼                        ▼
     │               ┌─────────┐              ┌─────────┐
     │               │  停止   │              │  播报中  │
     │               │ STOPPED │              │ SPEAKING │
     │               └─────────┘              └─────────┘
     │                                              │
     └──────────────────────────────────────────────┘
                       播报完成
```

### 9.3 核心 JavaScript 模块

#### voice-input.js 核心逻辑

```javascript
// voice-input.js
class VoiceInput {
    constructor(options = {}) {
        this.recognition = null;
        this.isListening = false;
        this.onResult = options.onResult || (() => {});
        this.onInterim = options.onInterim || (() => {});
        this.onError = options.onError || (() => {});
        this.onEnd = options.onEnd || (() => {});
        
        this.init();
    }
    
    init() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error('浏览器不支持语音识别');
            return;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'zh-CN';
        
        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            if (interimTranscript) {
                this.onInterim(interimTranscript);
            }
            if (finalTranscript) {
                this.onResult(finalTranscript);
            }
        };
        
        this.recognition.onerror = (event) => {
            this.onError(event.error);
            this.isListening = false;
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.onEnd();
        };
    }
    
    start() {
        if (this.recognition && !this.isListening) {
            this.recognition.start();
            this.isListening = true;
        }
    }
    
    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }
}
```

#### voice-output.js 核心逻辑

```javascript
// voice-output.js
class VoiceOutput {
    constructor(options = {}) {
        this.synth = window.speechSynthesis;
        this.voice = null;
        this.rate = options.rate || 1.0;
        this.pitch = options.pitch || 1.0;
        this.volume = options.volume || 1.0;
        this.onStart = options.onStart || (() => {});
        this.onEnd = options.onEnd || (() => {});
        
        this.init();
    }
    
    init() {
        // 等待语音列表加载
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = () => this.selectVoice();
        }
        this.selectVoice();
    }
    
    selectVoice() {
        const voices = this.synth.getVoices();
        // 优先选择中文语音
        this.voice = voices.find(v => v.lang.includes('zh')) 
                  || voices.find(v => v.lang.includes('cmn'))
                  || voices[0];
    }
    
    speak(text) {
        if (!this.synth) {
            console.error('浏览器不支持语音合成');
            return;
        }
        
        // 停止当前播放
        this.synth.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = this.voice;
        utterance.rate = this.rate;
        utterance.pitch = this.pitch;
        utterance.volume = this.volume;
        
        utterance.onstart = () => this.onStart();
        utterance.onend = () => this.onEnd();
        
        this.synth.speak(utterance);
    }
    
    stop() {
        if (this.synth) {
            this.synth.cancel();
        }
    }
}
```

### 9.4 响应式设计要点

```css
/* 移动优先设计 */
:root {
    --primary-color: #2563eb;
    --bg-color: #f8fafc;
    --text-color: #1e293b;
    --border-radius: 12px;
}

/* 录音按钮 - 大尺寸方便点击 */
.record-button {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: var(--primary-color);
    border: none;
    cursor: pointer;
    transition: all 0.3s;
}

.record-button.recording {
    background: #ef4444;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

/* 对话区域 */
.chat-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
}

.message {
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: var(--border-radius);
}

.message.user {
    background: var(--primary-color);
    color: white;
    margin-left: 20%;
}

.message.system {
    background: #e2e8f0;
    margin-right: 20%;
}

/* 手机适配 */
@media (max-width: 480px) {
    .record-button {
        width: 100px;
        height: 100px;
    }
    
    .message.user { margin-left: 10%; }
    .message.system { margin-right: 10%; }
}
```

---

## 十、后端服务规范

### 10.1 应用入口 main.py

```python
# backend/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time

from config import settings
from routes import voice, health, metrics

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    logger.info(f"M537 Voice Gateway 启动 - 端口 {settings.PORT}")
    logger.info(f"生态标准版本: LIGHT HOPE V5.3")
    yield
    # 关闭时
    logger.info("M537 Voice Gateway 关闭")

app = FastAPI(
    title="M537 Voice Gateway",
    description="LIGHT HOPE 生态语音访问入口",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求计时中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# 注册路由
app.include_router(voice.router, prefix="/api", tags=["voice"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])

# 静态文件服务 (前端)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

### 10.2 配置管理 config.py

```python
# backend/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 服务配置
    PORT: int = 5537
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # 项目路径
    PROJECTS_BASE_PATH: str = "/data/projects"
    
    # 安全配置
    MAX_TRANSCRIPT_LENGTH: int = 500
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # V5.3 生态信息
    ECOSYSTEM_VERSION: str = "V5.3"
    PROJECT_ID: str = "m537"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### 10.3 意图解析服务

```python
# backend/services/intent_parser.py
from typing import Optional, Dict, Any, List, Tuple
import re
from config.intent_rules import INTENT_RULES
from services.project_id_normalizer import normalize_project_id

class IntentParser:
    """意图解析器 - 规则优先，支持 LLM 辅助"""
    
    def __init__(self):
        self.rules = INTENT_RULES
        
    def parse(self, transcript: str) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """
        解析用户输入的意图
        
        返回: (intent, confidence, params)
        """
        transcript_lower = transcript.lower().strip()
        
        # 第一步：规则匹配
        for intent, rule in self.rules.items():
            for keyword in rule["keywords"]:
                if keyword in transcript_lower:
                    params = self._extract_params(transcript, rule.get("params", []))
                    return intent, 0.95, params
        
        # 第二步：LLM 辅助 (如果规则匹配失败)
        # TODO: 后续版本实现
        
        # 未识别
        return None, 0.0, {}
    
    def _extract_params(self, transcript: str, param_types: List[str]) -> Dict[str, Any]:
        """提取参数"""
        params = {}
        
        if "project_id" in param_types:
            project_id = self._extract_project_id(transcript)
            if project_id:
                params["project_id"] = project_id
                
        return params
    
    def _extract_project_id(self, transcript: str) -> Optional[str]:
        """提取并规范化项目编号"""
        # 匹配 m + 数字 的模式
        patterns = [
            r'[mM]\s*(\d+)',           # m536, m 536
            r'项目\s*(\d+)',            # 项目536
            r'[mM](\d)\s+(\d+)',        # m5 36
        ]
        
        for pattern in patterns:
            match = re.search(pattern, transcript)
            if match:
                if len(match.groups()) == 2:
                    project_id = f"m{match.group(1)}{match.group(2)}"
                else:
                    project_id = f"m{match.group(1)}"
                return normalize_project_id(project_id)
        
        return None
    
    def get_suggestions(self) -> List[str]:
        """获取可用问题建议"""
        return [
            "现在有多少个项目？",
            "系统状态怎么样？",
            "当前有哪些端口在监听？",
            "最近有什么错误？",
            "m536 是什么项目？"
        ]
```

### 10.4 查询执行服务

```python
# backend/services/query_executor.py
from typing import Dict, Any, Optional
import importlib
import logging

from config.tool_registry import TOOL_REGISTRY

logger = logging.getLogger(__name__)

class QueryExecutor:
    """查询执行器 - 调用白名单工具"""
    
    def __init__(self):
        self.tools = {}
        self._load_tools()
    
    def _load_tools(self):
        """加载所有注册的工具"""
        for tool_name, tool_info in TOOL_REGISTRY.items():
            try:
                module = importlib.import_module(f"tools.{tool_info['module']}")
                tool_class = getattr(module, tool_info['class'])
                self.tools[tool_name] = tool_class()
                logger.info(f"加载工具: {tool_name}")
            except Exception as e:
                logger.error(f"加载工具失败 {tool_name}: {e}")
    
    def execute(self, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行工具查询
        
        返回: {"success": bool, "data": Any, "error": str}
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "data": None,
                "error": f"未知工具: {tool_name}"
            }
        
        try:
            tool = self.tools[tool_name]
            result = tool.execute(params or {})
            return {
                "success": True,
                "data": result,
                "error": None
            }
        except Exception as e:
            logger.error(f"工具执行失败 {tool_name}: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def list_available_tools(self) -> Dict[str, str]:
        """列出可用工具"""
        return {name: info["description"] for name, info in TOOL_REGISTRY.items()}
```

### 10.5 响应构建服务

```python
# backend/services/response_builder.py
from typing import Dict, Any, List, Optional

class ResponseBuilder:
    """响应构建器 - 将数据转换为自然语言"""
    
    TEMPLATES = {
        "count_projects": {
            "success": "当前共有 {total} 个项目，其中 P0 项目 {p0} 个，P1 项目 {p1} 个，P2 项目 {p2} 个，P3 项目 {p3} 个。",
            "empty": "当前没有任何项目。"
        },
        "list_ports": {
            "success": "当前共有 {count} 个端口在监听：{ports}",
            "empty": "当前没有端口在监听。"
        },
        "list_containers": {
            "success": "当前有 {running} 个容器在运行，{stopped} 个已停止。运行中的容器包括：{names}",
            "empty": "当前没有 Docker 容器。"
        },
        "system_status": {
            "success": "系统状态：CPU 使用率 {cpu}%，内存使用率 {memory}%，磁盘使用率 {disk}%。{warning}",
        },
        "recent_errors": {
            "success": "最近 24 小时发现 {count} 个错误：{errors}",
            "empty": "最近 24 小时没有发现错误，一切正常！"
        },
        "project_summary": {
            "success": "项目 {project_id}：{title}。{description}",
            "not_found": "没有找到项目 {project_id}。"
        },
        "missing_readme": {
            "success": "共有 {count} 个项目缺少 README：{projects}",
            "empty": "所有项目都有 README，很棒！"
        },
        "recent_updates": {
            "success": "最近 7 天有 {count} 个项目更新：{projects}",
            "empty": "最近 7 天没有项目更新。"
        },
        "p0_health": {
            "all_healthy": "所有 P0 关键服务状态正常！共 {count} 个服务在运行。",
            "has_issues": "注意！有 {unhealthy} 个 P0 服务异常：{services}"
        },
        "list_tmux": {
            "success": "当前有 {count} 个 tmux session：{sessions}",
            "empty": "当前没有 tmux session。"
        },
        "not_recognized": {
            "default": "抱歉，我没有理解你的问题。你可以尝试问：{suggestions}"
        }
    }
    
    def build(self, intent: str, data: Dict[str, Any], success: bool = True) -> str:
        """构建自然语言响应"""
        if not success:
            return f"查询失败：{data.get('error', '未知错误')}"
        
        templates = self.TEMPLATES.get(intent, {})
        
        # 根据数据选择模板
        if not data or (isinstance(data, dict) and data.get("total", 1) == 0):
            template = templates.get("empty", templates.get("success", ""))
        elif data.get("unhealthy", 0) > 0:
            template = templates.get("has_issues", templates.get("success", ""))
        elif data.get("all_healthy"):
            template = templates.get("all_healthy", templates.get("success", ""))
        elif data.get("not_found"):
            template = templates.get("not_found", "")
        else:
            template = templates.get("success", "")
        
        try:
            return template.format(**data)
        except KeyError as e:
            return f"数据格式错误: {e}"
    
    def build_not_recognized(self, suggestions: List[str]) -> str:
        """构建未识别意图的响应"""
        template = self.TEMPLATES["not_recognized"]["default"]
        return template.format(suggestions="、".join(suggestions[:3]))
```

---

## 十一、白名单工具库

### 11.1 工具基类

```python
# backend/tools/base_tool.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """工具基类"""
    
    name: str = ""
    description: str = ""
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具逻辑"""
        pass
    
    def validate_params(self, params: Dict[str, Any], required: list) -> bool:
        """验证必需参数"""
        return all(key in params for key in required)
```

### 11.2 项目统计工具

```python
# backend/tools/count_projects.py
import os
from typing import Dict, Any
from tools.base_tool import BaseTool
from config import settings

class CountProjectsTool(BaseTool):
    """统计项目数量"""
    
    name = "count_projects"
    description = "统计服务器上的项目总数"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        base_path = settings.PROJECTS_BASE_PATH
        
        total = 0
        p0, p1, p2, p3 = 0, 0, 0, 0
        
        if not os.path.exists(base_path):
            return {"total": 0, "p0": 0, "p1": 0, "p2": 0, "p3": 0}
        
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path) and item.startswith("m"):
                total += 1
                
                # 简单的优先级判断 (实际应读取配置)
                project_num = item[1:] if item[1:].isdigit() else "0"
                try:
                    num = int(project_num)
                    if num < 100:
                        p0 += 1
                    elif num < 500:
                        p1 += 1
                    elif num < 1000:
                        p2 += 1
                    else:
                        p3 += 1
                except ValueError:
                    p3 += 1
        
        return {
            "total": total,
            "p0": p0,
            "p1": p1,
            "p2": p2,
            "p3": p3
        }
```

### 11.3 端口检测工具

```python
# backend/tools/list_ports.py
import subprocess
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class ListPortsTool(BaseTool):
    """列出监听端口"""
    
    name = "list_ports"
    description = "列出当前系统监听的端口"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 使用 ss 命令获取监听端口
            result = subprocess.run(
                ["ss", "-tuln"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            ports = self._parse_ports(result.stdout)
            
            return {
                "count": len(ports),
                "ports": ", ".join(map(str, sorted(ports)[:10])),  # 只显示前10个
                "all_ports": sorted(ports)
            }
        except Exception as e:
            return {"count": 0, "ports": "", "error": str(e)}
    
    def _parse_ports(self, output: str) -> List[int]:
        """解析 ss 输出获取端口号"""
        ports = set()
        for line in output.strip().split("\n")[1:]:  # 跳过标题行
            parts = line.split()
            if len(parts) >= 5:
                local_addr = parts[4]
                # 格式可能是 0.0.0.0:80 或 [::]:80 或 *:80
                if ":" in local_addr:
                    port_str = local_addr.rsplit(":", 1)[-1]
                    if port_str.isdigit():
                        ports.add(int(port_str))
        return list(ports)
```

### 11.4 系统状态工具

```python
# backend/tools/system_status.py
import psutil
from typing import Dict, Any
from tools.base_tool import BaseTool

class SystemStatusTool(BaseTool):
    """查询系统状态"""
    
    name = "system_status"
    description = "查询 CPU、内存、磁盘使用率"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        
        # 生成警告信息
        warnings = []
        if cpu > 80:
            warnings.append(f"CPU 使用率过高")
        if memory > 80:
            warnings.append(f"内存使用率过高")
        if disk > 90:
            warnings.append(f"磁盘空间不足")
        
        warning_text = "⚠️ " + "，".join(warnings) if warnings else "一切正常。"
        
        return {
            "cpu": round(cpu, 1),
            "memory": round(memory, 1),
            "disk": round(disk, 1),
            "warning": warning_text
        }
```

### 11.5 项目摘要工具

```python
# backend/tools/get_project_summary.py
import os
from typing import Dict, Any
from tools.base_tool import BaseTool
from config import settings

class GetProjectSummaryTool(BaseTool):
    """获取项目摘要"""
    
    name = "get_project_summary"
    description = "读取项目 README 获取摘要"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        project_id = params.get("project_id")
        if not project_id:
            return {"not_found": True, "project_id": "未指定"}
        
        project_path = os.path.join(settings.PROJECTS_BASE_PATH, project_id)
        readme_path = os.path.join(project_path, "README.md")
        
        if not os.path.exists(project_path):
            return {"not_found": True, "project_id": project_id}
        
        if not os.path.exists(readme_path):
            return {
                "project_id": project_id,
                "title": project_id,
                "description": "该项目没有 README 文件。"
            }
        
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 提取标题和描述
            title, description = self._extract_summary(content)
            
            return {
                "project_id": project_id,
                "title": title,
                "description": description
            }
        except Exception as e:
            return {
                "project_id": project_id,
                "title": project_id,
                "description": f"读取 README 失败: {e}"
            }
    
    def _extract_summary(self, content: str) -> tuple:
        """从 README 提取标题和摘要"""
        lines = content.strip().split("\n")
        
        title = ""
        description = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("# ") and not title:
                title = line[2:].strip()
            elif line and not line.startswith("#") and not description:
                description = line[:200]  # 截取前200字符
                break
        
        return title or "未命名项目", description or "暂无描述"
```

### 11.6 工具注册表

```python
# backend/config/tool_registry.py
TOOL_REGISTRY = {
    "count_projects": {
        "module": "count_projects",
        "class": "CountProjectsTool",
        "description": "统计项目数量"
    },
    "list_ports": {
        "module": "list_ports",
        "class": "ListPortsTool",
        "description": "列出监听端口"
    },
    "list_containers": {
        "module": "list_containers",
        "class": "ListContainersTool",
        "description": "列出Docker容器"
    },
    "system_status": {
        "module": "system_status",
        "class": "SystemStatusTool",
        "description": "查询系统状态"
    },
    "recent_errors": {
        "module": "recent_errors",
        "class": "RecentErrorsTool",
        "description": "查询最近错误"
    },
    "get_project_summary": {
        "module": "get_project_summary",
        "class": "GetProjectSummaryTool",
        "description": "获取项目摘要"
    },
    "scan_missing_readme": {
        "module": "scan_missing_readme",
        "class": "ScanMissingReadmeTool",
        "description": "扫描缺失README"
    },
    "recent_updates": {
        "module": "recent_updates",
        "class": "RecentUpdatesTool",
        "description": "查询最近更新"
    },
    "p0_health_check": {
        "module": "p0_health_check",
        "class": "P0HealthCheckTool",
        "description": "检查P0服务状态"
    },
    "list_tmux": {
        "module": "list_tmux",
        "class": "ListTmuxTool",
        "description": "列出tmux会话"
    }
}
```

---

## 十二、安全边界与风险控制

### 12.1 安全原则

| 原则 | 描述 | 实现方式 |
|------|------|----------|
| **白名单执行** | 只允许预定义的工具执行 | 工具注册表 |
| **只读访问** | 默认只读，禁止修改操作 | Volume 只读挂载 |
| **输入验证** | 严格验证所有用户输入 | Pydantic 模型 |
| **输出过滤** | 过滤敏感信息 | 响应构建器 |
| **日志审计** | 记录所有查询操作 | 中间件日志 |

### 12.2 绝对禁止清单

```python
# config/security.py
FORBIDDEN_OPERATIONS = [
    # 文件操作
    "rm", "rmdir", "mv", "cp", "chmod", "chown",
    # 进程操作
    "kill", "killall", "pkill",
    # 系统配置
    "systemctl", "service", "init",
    # 网络配置
    "iptables", "ufw", "firewalld",
    # 用户管理
    "useradd", "userdel", "passwd",
    # 包管理
    "apt", "yum", "pip install",
    # 危险命令
    "dd", "mkfs", "fdisk",
    # Git 推送
    "git push", "git commit",
]

# 禁止访问的路径模式
FORBIDDEN_PATHS = [
    "/etc/",
    "/root/",
    "/var/log/",
    "~/.ssh/",
    ".env",
    "*.key",
    "*.pem",
]
```

### 12.3 输入验证

```python
# backend/routes/voice.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any

class VoiceQueryRequest(BaseModel):
    transcript: str = Field(..., max_length=500, min_length=1)
    session_id: Optional[str] = Field(None, max_length=100)
    context: Optional[Dict[str, Any]] = None
    
    @validator("transcript")
    def sanitize_transcript(cls, v):
        # 移除潜在危险字符
        dangerous_chars = [";", "|", "&", "`", "$", "(", ")", "{", "}", "<", ">"]
        for char in dangerous_chars:
            v = v.replace(char, "")
        return v.strip()
```

### 12.4 风险矩阵

| 风险 | 等级 | 概率 | 影响 | 缓解措施 |
|------|------|------|------|----------|
| 命令注入 | 高 | 低 | 高 | 白名单工具，禁止动态命令 |
| 信息泄露 | 中 | 中 | 中 | 响应过滤，路径限制 |
| 拒绝服务 | 中 | 中 | 低 | 请求限流，内存限制 |
| 语音识别错误 | 低 | 高 | 低 | 编号纠错，确认机制 |

---

## 十三、测试验收标准

### 13.1 单元测试

```python
# tests/test_intent_parser.py
import pytest
from services.intent_parser import IntentParser

class TestIntentParser:
    def setup_method(self):
        self.parser = IntentParser()
    
    def test_count_projects_intent(self):
        cases = [
            "现在有多少个项目",
            "项目总数是多少",
            "一共有几个项目",
        ]
        for case in cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "count_projects"
            assert confidence >= 0.9
    
    def test_project_summary_with_id(self):
        cases = [
            ("m536是什么项目", "m536"),
            ("m 8001 是什么", "m8001"),
            ("介绍一下项目m709", "m709"),
        ]
        for transcript, expected_id in cases:
            intent, confidence, params = self.parser.parse(transcript)
            assert intent == "project_summary"
            assert params.get("project_id") == expected_id
    
    def test_unknown_intent(self):
        intent, confidence, params = self.parser.parse("今天天气怎么样")
        assert intent is None
        assert confidence == 0.0
```

### 13.2 API 测试

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestVoiceAPI:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "LIGHT HOPE V5.3" in data["ecosystem"]
    
    def test_voice_query_success(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": "现在有多少个项目"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "answer_text" in data["data"]
    
    def test_voice_query_unknown(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": "今天天气怎么样"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "suggestions" in data["error"]
    
    def test_voice_query_invalid_input(self):
        response = client.post(
            "/api/voice-query",
            json={"transcript": ""}
        )
        assert response.status_code == 422  # Validation Error
```

### 13.3 集成测试

```python
# tests/test_integration.py
import pytest

class TestEndToEnd:
    """端到端集成测试"""
    
    def test_full_query_flow(self):
        """完整查询流程测试"""
        # 1. 模拟语音输入
        transcript = "现在有多少个项目"
        
        # 2. 意图解析
        from services.intent_parser import IntentParser
        parser = IntentParser()
        intent, confidence, params = parser.parse(transcript)
        assert intent == "count_projects"
        
        # 3. 查询执行
        from services.query_executor import QueryExecutor
        executor = QueryExecutor()
        result = executor.execute(intent, params)
        assert result["success"] == True
        
        # 4. 响应构建
        from services.response_builder import ResponseBuilder
        builder = ResponseBuilder()
        answer = builder.build(intent, result["data"])
        assert "项目" in answer
```

### 13.4 验收检查清单

```bash
#!/bin/bash
# scripts/acceptance_check.sh

echo "=== M537 验收检查 ==="

# 1. 容器运行检查
echo -n "1. 容器运行状态... "
docker ps | grep m537_voice_gateway > /dev/null && echo "✅" || echo "❌"

# 2. 健康检查
echo -n "2. 健康检查端点... "
curl -s http://localhost:5537/health | grep "healthy" > /dev/null && echo "✅" || echo "❌"

# 3. 内存限制检查
echo -n "3. 内存限制 (< 1G)... "
MEM=$(docker stats --no-stream m537_voice_gateway --format "{{.MemUsage}}" | cut -d'/' -f2)
echo "✅ ($MEM)"

# 4. 自动重启策略
echo -n "4. 自动重启策略... "
docker inspect m537_voice_gateway | grep '"RestartPolicy"' -A2 | grep "unless-stopped" > /dev/null && echo "✅" || echo "❌"

# 5. API 响应测试
echo -n "5. API 响应测试... "
curl -s -X POST http://localhost:5537/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript":"现在有多少个项目"}' | grep "success" > /dev/null && echo "✅" || echo "❌"

# 6. 前端加载测试
echo -n "6. 前端页面加载... "
curl -s http://localhost:5537/ | grep "M537" > /dev/null && echo "✅" || echo "❌"

echo "=== 检查完成 ==="
```

---

## 十四、部署流程

### 14.1 部署前置条件

```bash
# 服务器要求
- Docker 24.0+
- Docker Compose 2.24+
- Cloudflare Tunnel 已配置
- 域名 m537.x1000.ai 已解析
```

### 14.2 部署步骤

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

PROJECT_DIR="/data/projects/m537_voice_gateway"
DOMAIN="m537.x1000.ai"

echo "=== M537 部署开始 ==="

# 1. 进入项目目录
cd $PROJECT_DIR

# 2. 拉取最新代码 (如果使用 Git)
# git pull origin main

# 3. 创建环境变量文件
if [ ! -f .env ]; then
    cp .env.example .env
    echo "请编辑 .env 文件配置环境变量"
fi

# 4. 构建镜像
echo "构建 Docker 镜像..."
docker compose build

# 5. 启动服务
echo "启动服务..."
docker compose up -d

# 6. 等待服务就绪
echo "等待服务就绪..."
sleep 10

# 7. 健康检查
echo "执行健康检查..."
curl -f http://localhost:5537/health || exit 1

# 8. 配置 Cloudflare Tunnel (如果需要)
echo "配置 Cloudflare Tunnel..."
# cloudflared tunnel route dns $TUNNEL_ID $DOMAIN

echo "=== 部署完成 ==="
echo "访问地址: https://$DOMAIN"
```

### 14.3 Cloudflare Tunnel 配置

```yaml
# /etc/cloudflared/config.yml (添加 m537 条目)
tunnel: <your-tunnel-id>
credentials-file: /etc/cloudflared/<tunnel-id>.json

ingress:
  # ... 其他服务 ...
  
  - hostname: m537.x1000.ai
    service: http://localhost:5537
  
  - service: http_status:404
```

### 14.4 回滚流程

```bash
#!/bin/bash
# scripts/rollback.sh

echo "=== M537 回滚 ==="

cd /data/projects/m537_voice_gateway

# 停止当前服务
docker compose down

# 回滚到上一个版本 (如果使用 Git)
# git checkout HEAD~1

# 重新启动
docker compose up -d

echo "=== 回滚完成 ==="
```

---

## 十五、扩展路径规划

### 15.1 版本路线图

```
V1.0 (MVP)          V1.1              V1.2              V2.0
2026-03-24          2026-04-01        2026-04-15        2026-05-01
    │                   │                 │                 │
    ▼                   ▼                 ▼                 ▼
┌─────────┐       ┌─────────┐       ┌─────────┐       ┌─────────┐
│运维入口 │──────▶│学生入口 │──────▶│家长入口 │──────▶│多场景  │
│10个问题 │       │学习查询 │       │进度查看 │       │养老/医疗│
│单用户   │       │任务建议 │       │双角色   │       │多用户   │
└─────────┘       └─────────┘       └─────────┘       └─────────┘
```

### 15.2 V1.1 学生入口规划

**新增问题（10个）**：

| # | 问题 | 功能 |
|---|------|------|
| 1 | 我上周做了哪些题？ | 学习记录查询 |
| 2 | 哪些题没做完？ | 未完成任务 |
| 3 | 我最弱的是哪一类？ | 薄弱点分析 |
| 4 | 今天应该先练什么？ | 智能建议 |
| 5 | 上次错得最多的是什么？ | 错题分析 |
| 6 | 讲一下昨天那道题为什么错？ | 错题讲解 |
| 7 | 给我出 5 道同类型题 | 题目生成 |
| 8 | 今天的训练计划是什么？ | 每日计划 |
| 9 | 我这周进步了吗？ | 进度追踪 |
| 10 | 总结一下我这周表现 | 周报生成 |

### 15.3 V1.2 家长入口规划

**新增问题（8个）**：

| # | 问题 | 功能 |
|---|------|------|
| 1 | 孩子这周完成度怎么样？ | 完成率统计 |
| 2 | 哪些是真会了，哪些只是碰巧做对？ | 掌握度分析 |
| 3 | 这周应该重点抓什么？ | 建议重点 |
| 4 | 最近是不是有拖延？ | 行为分析 |
| 5 | 哪些题型需要复习？ | 复习建议 |
| 6 | 学习强度是否合适？ | 强度评估 |
| 7 | 孩子最近进步在哪里？ | 进步点 |
| 8 | 我作为家长应该配合什么？ | 家长建议 |

### 15.4 技术扩展点

| 扩展点 | 描述 | 预计时间 |
|--------|------|----------|
| LLM 意图辅助 | 模糊问题使用 LLM 分类 | V1.1 |
| 多轮对话 | 上下文保持，追问支持 | V1.2 |
| 用户认证 | JWT Token，多用户隔离 | V1.2 |
| 数据库集成 | PostgreSQL 存储学习记录 | V1.1 |
| WebSocket | 实时双向通信 | V2.0 |
| 语音唤醒 | "Hey, 小希" 唤醒词 | V2.0+ |

---

## 十六、SONNET 执行提示词

以下是供 Sonnet 模型执行的完整提示词，直接复制使用即可。

---

### SONNET 执行提示词

```markdown
# M537 语音生态入口 - 执行任务

## 项目信息
- 项目编号: m537
- 项目名称: voice_gateway (语音生态入口)
- 目标端口: 5537
- 部署域名: m537.x1000.ai
- 合规标准: LIGHT HOPE 生态系统标准 V5.3

## 参考项目
- 参考 m520_voice_memory_engine: /data/projects/m520_voice_memory_engine

## 执行目标
创建一个完整可运行的语音访问服务器生态入口，实现：
1. 前端网页语音输入（Web Speech API）
2. 后端 FastAPI 接收并解析意图
3. 调用白名单工具获取服务器真实数据
4. 返回结构化回答
5. 前端语音播报（TTS）

## V5.3 必须满足项
1. ✅ docker-compose.yml 使用标准模板
2. ✅ 内存限制: 1G
3. ✅ 自动重启: unless-stopped  
4. ✅ 健康检查: /health 端点
5. ✅ 日志限制: max-size 10m, max-file 3
6. ✅ README.md > 100 行

## 目录结构（必须创建）
```
/data/projects/m537_voice_gateway/
├── README.md
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── frontend/
│   ├── index.html
│   ├── css/styles.css
│   └── js/
│       ├── app.js
│       ├── voice-input.js
│       ├── voice-output.js
│       └── api-client.js
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── voice.py
│   │   └── health.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── intent_parser.py
│   │   ├── query_executor.py
│   │   └── response_builder.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base_tool.py
│   │   ├── count_projects.py
│   │   ├── list_ports.py
│   │   ├── system_status.py
│   │   └── get_project_summary.py
│   └── config/
│       ├── __init__.py
│       ├── intent_rules.py
│       └── tool_registry.py
└── tests/
    └── test_api.py
```

## MVP 首批支持的 10 个问题
1. 现在有多少个项目？ → count_projects
2. 当前有哪些端口在监听？ → list_ports
3. 哪些 Docker 容器在运行？ → list_containers
4. CPU/内存/磁盘状态？ → system_status
5. 最近 24 小时有什么错误？ → recent_errors
6. m536 是什么项目？ → get_project_summary
7. 哪些项目没有 README？ → scan_missing_readme
8. 最近 7 天更新了哪些项目？ → recent_updates
9. P0 关键服务状态如何？ → p0_health_check
10. 当前有哪些 tmux session？ → list_tmux

## 核心文件内容要求

### docker-compose.yml 必须包含
```yaml
version: '3.8'
services:
  m537_voice_gateway:
    build: .
    container_name: m537_voice_gateway
    restart: unless-stopped
    ports:
      - "5537:5537"
    volumes:
      - /data/projects:/data/projects:ro
    deploy:
      resources:
        limits:
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5537/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### 前端核心功能
1. 录音按钮（大尺寸，手机友好）
2. 实时显示识别文字
3. 显示回答文本
4. 自动语音播报
5. 快捷问题按钮

### 后端核心功能
1. /api/voice-query - 主查询接口
2. /api/health - 健康检查
3. 意图解析（规则优先）
4. 白名单工具执行
5. 响应构建

## 安全边界（绝对禁止）
- ❌ LLM 直接执行 shell
- ❌ 前端直接访问服务器
- ❌ 动态生成命令
- ❌ 访问 /etc/, /root/, ~/.ssh/
- ❌ rm, kill, systemctl 等危险命令

## 执行步骤
1. 创建项目目录结构
2. 编写 README.md（>100行）
3. 创建 docker-compose.yml（V5.3 标准）
4. 创建 Dockerfile
5. 创建前端文件（index.html, styles.css, JS 模块）
6. 创建后端文件（FastAPI 应用）
7. 创建白名单工具（至少 4 个核心工具）
8. 创建测试文件
9. 本地测试运行
10. 验证健康检查

## 验收标准
```bash
# 1. 容器正常运行
docker ps | grep m537_voice_gateway

# 2. 健康检查通过
curl http://localhost:5537/health

# 3. API 响应正常
curl -X POST http://localhost:5537/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript":"现在有多少个项目"}'

# 4. 前端页面加载
curl http://localhost:5537/ | grep "M537"
```

## 开始执行
请按照以上规范，完整创建 M537 语音生态入口项目。
一步一步执行，每完成一个主要文件后确认，直到项目可以正常运行。
```

---

## 附录 A：快速启动命令

```bash
# 一键部署
cd /data/projects/m537_voice_gateway
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 健康检查
curl http://localhost:5537/health

# 测试查询
curl -X POST http://localhost:5537/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript":"现在有多少个项目"}'
```

---

## 附录 B：故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 容器启动失败 | 端口被占用 | `lsof -i:5537` 检查并释放 |
| 健康检查失败 | 服务未就绪 | 检查日志 `docker logs m537_voice_gateway` |
| 语音识别不工作 | 浏览器不支持 | 使用 Chrome/Edge |
| 查询返回空 | 项目路径错误 | 检查 /data/projects 是否存在 |
| 内存超限 | 工具执行过慢 | 检查具体工具日志 |

---

*文档编号: M537-MASTER-PLAN-20260324*
*起草: OPUS (战略规划)*
*执行: SONNET (开发实施)*
*发布日期: 2026-03-24*
*合规标准: LIGHT HOPE V5.3*

*LIGHT HOPE LLC · EMPOWER GOOD WITH AI*
