# M537 Voice Gateway - 开发者指南

## 目录

- [项目结构](#项目结构)
- [开发环境](#开发环境)
- [添加新工具](#添加新工具)
- [添加新意图](#添加新意图)
- [测试指南](#测试指南)
- [API扩展](#api扩展)
- [贡献指南](#贡献指南)

---

## 项目结构

```
m537_voice_gateway/
├── backend/                  # 后端 Python 代码
│   ├── config/              # 配置文件
│   │   ├── intent_rules.py  # 意图规则定义
│   │   ├── tool_registry.py # 工具注册表
│   │   └── project_id_patterns.py
│   ├── middleware/          # 中间件
│   │   ├── rate_limiter.py  # 速率限制
│   │   └── security.py      # 安全中间件
│   ├── routes/              # API路由
│   │   ├── voice.py         # 语音查询API
│   │   ├── health.py        # 健康检查
│   │   ├── metrics.py       # Prometheus指标
│   │   └── websocket.py     # WebSocket
│   ├── services/            # 业务服务
│   │   ├── intent_parser.py # 意图解析
│   │   ├── query_executor.py # 查询执行
│   │   ├── response_builder.py # 响应构建
│   │   ├── cache.py         # 查询缓存
│   │   ├── session_manager.py # 会话管理
│   │   └── i18n.py          # 国际化
│   ├── tools/               # 查询工具
│   │   ├── base_tool.py     # 工具基类
│   │   ├── count_projects.py
│   │   ├── system_status.py
│   │   └── ...
│   ├── main.py              # 应用入口
│   └── settings.py          # 应用设置
├── frontend/                 # 前端代码
│   ├── js/                  # JavaScript
│   ├── css/                 # 样式
│   └── index.html           # 主页面
├── tests/                    # 测试代码
├── helm/                     # Kubernetes Helm Chart
├── cli/                      # 命令行客户端
├── docs/                     # 文档
└── monitoring/               # 监控配置
```

---

## 开发环境

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/lighthope-ai/m537-voice-gateway.git
cd m537-voice-gateway

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r backend/requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 4. 设置环境变量
export PYTHONPATH=$(pwd)/backend
export PROJECTS_BASE_PATH=/data/projects

# 5. 启动开发服务器
cd backend
uvicorn main:app --reload --port 5537
```

### Docker 开发

```bash
# 开发模式 (热重载)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# 生产模式
docker compose up --build
```

### 运行测试

```bash
# 全部测试
pytest tests/ -v

# 特定测试
pytest tests/test_intent_parser.py -v

# 覆盖率报告
pytest tests/ --cov=backend --cov-report=html
```

---

## 添加新工具

### 步骤 1: 创建工具类

在 `backend/tools/` 目录创建新文件：

```python
# backend/tools/my_new_tool.py
"""
M537 Voice Gateway - My New Tool
Description of what this tool does
"""
from typing import Dict, Any
from tools.base_tool import BaseTool


class MyNewTool(BaseTool):
    """
    Tool description.
    """

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            params: Optional parameters

        Returns:
            Dict with tool results
        """
        params = params or {}

        try:
            # 你的业务逻辑
            result = self._do_something()

            return {
                "success": True,
                "data": result,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    def _do_something(self):
        """Internal implementation"""
        pass
```

### 步骤 2: 注册工具

在 `backend/config/tool_registry.py` 添加：

```python
TOOL_REGISTRY = {
    # ... 现有工具
    "my_new_tool": {
        "module": "my_new_tool",
        "class": "MyNewTool",
        "description": "Description of the tool",
        "requires_params": ["param1"],  # 可选
        "optional_params": ["param2"]   # 可选
    }
}
```

### 步骤 3: 添加响应模板

在 `backend/services/response_builder.py` 的 `TEMPLATES` 中添加：

```python
"my_new_tool": {
    "success": "结果信息：{data}",
    "empty": "没有找到数据。"
}
```

---

## 添加新意图

### 步骤 1: 定义意图规则

在 `backend/config/intent_rules.py` 添加：

```python
INTENT_RULES = {
    # ... 现有意图
    "my_new_intent": {
        "keywords": ["关键词1", "关键词2"],
        "patterns": [
            r"正则表达式1",
            r"正则表达式2"
        ],
        "requires_project_id": False,
        "tool": "my_new_tool"
    }
}

# 添加到分类
INTENT_CATEGORIES = {
    "项目管理": [...],
    "我的分类": ["my_new_intent"]  # 新分类
}
```

### 步骤 2: 配置缓存 TTL

在 `backend/services/cache.py` 的 `TTL_CONFIG` 添加：

```python
TTL_CONFIG = {
    # ... 现有配置
    "my_new_intent": 60,  # 秒
}
```

### 步骤 3: 添加翻译

在 `backend/services/i18n.py` 添加：

```python
TRANSLATIONS = {
    "my_new_intent.success": {
        "zh-CN": "中文响应",
        "en-US": "English response",
        "ja-JP": "日本語の応答"
    }
}
```

---

## 测试指南

### 测试结构

```
tests/
├── conftest.py          # pytest fixtures
├── test_api.py          # API 集成测试
├── test_intent_parser.py # 意图解析测试
├── test_tools.py        # 工具测试
├── test_performance.py  # 性能测试
├── test_security.py     # 安全测试
└── test_i18n.py         # 国际化测试
```

### 编写测试

```python
# tests/test_my_new_tool.py
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from tools.my_new_tool import MyNewTool


class TestMyNewTool:
    """Tests for MyNewTool"""

    @pytest.fixture
    def tool(self):
        return MyNewTool()

    def test_execute_success(self, tool):
        """Test successful execution"""
        result = tool.execute()
        assert result["success"] is True
        assert result["data"] is not None

    def test_execute_with_params(self, tool):
        """Test with parameters"""
        result = tool.execute({"param1": "value"})
        assert result["success"] is True
```

### 测试命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定文件
pytest tests/test_my_new_tool.py -v

# 只运行标记的测试
pytest tests/ -m "not slow"

# 生成覆盖率
pytest tests/ --cov=backend --cov-report=term-missing
```

---

## API扩展

### 添加新端点

```python
# backend/routes/my_route.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/my-endpoint")
async def my_endpoint():
    return {"message": "Hello"}

@router.post("/api/my-endpoint")
async def create_something(data: dict):
    return {"created": data}
```

### 注册路由

在 `backend/main.py` 添加：

```python
from routes import my_route

app.include_router(my_route.router, tags=["my-feature"])
```

---

## 贡献指南

### 代码风格

- 使用 `black` 格式化代码
- 使用 `ruff` 进行 lint
- 使用 `mypy` 类型检查

```bash
# 格式化
black backend/

# Lint
ruff check backend/

# 类型检查
mypy backend/
```

### 提交规范

使用 Conventional Commits:

```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
test: 添加测试
refactor: 重构代码
perf: 性能优化
security: 安全修复
```

### Pull Request 流程

1. Fork 项目
2. 创建功能分支: `git checkout -b feat/my-feature`
3. 提交更改: `git commit -m "feat: add my feature"`
4. 推送分支: `git push origin feat/my-feature`
5. 创建 Pull Request

### 代码审查清单

- [ ] 所有测试通过
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 代码符合风格指南
- [ ] 没有安全漏洞

---

## 常见问题

### Q: 如何调试意图解析？

```python
from services.intent_parser import IntentParser

parser = IntentParser()
result = parser.parse("你的查询文本")
print(result)  # {'intent': '...', 'confidence': ..., 'params': {...}}
```

### Q: 如何测试API？

```bash
# 使用 curl
curl -X POST http://localhost:5537/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript": "系统状态"}'

# 使用 CLI
./cli/m537.py "系统状态"
./cli/m537.py -i  # 交互模式
```

### Q: 如何查看实时指标？

访问 http://localhost:5537/api/metrics/json

---

*文档版本: 1.0.0 | 最后更新: 2026-03-28*
