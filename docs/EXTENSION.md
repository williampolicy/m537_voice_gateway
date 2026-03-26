# M537 Voice Gateway - 扩展指南

> 版本: 1.0.0 | 标准: LIGHT HOPE V5.3

## 扩展概述

M537 采用模块化设计，支持以下扩展方式：

1. **添加新的查询意图** - 扩展关键词和工具映射
2. **添加新的白名单工具** - 创建新的数据查询工具
3. **定制响应模板** - 修改自然语言回复格式
4. **集成外部服务** - 连接数据库或 API

---

## 添加新的查询意图

### 1. 定义意图规则

编辑 `backend/config/intent_rules.py`：

```python
INTENT_RULES = {
    # ... 现有规则 ...

    # 新增意图
    "new_intent": {
        "keywords": ["关键词1", "关键词2", "关键词3"],
        "tool": "new_tool",
        "params": [],  # 可选参数
        "description": "新意图描述"
    }
}
```

### 2. 注册工具

编辑 `backend/config/tool_registry.py`：

```python
TOOL_REGISTRY = {
    # ... 现有工具 ...

    "new_tool": {
        "module": "new_tool",
        "class": "NewTool",
        "description": "新工具描述"
    }
}
```

### 3. 添加响应模板

编辑 `backend/services/response_builder.py`：

```python
TEMPLATES = {
    # ... 现有模板 ...

    "new_intent": {
        "success": "查询结果：{result}",
        "empty": "没有找到相关数据。"
    }
}
```

---

## 添加新的白名单工具

### 1. 创建工具文件

在 `backend/tools/` 目录创建 `new_tool.py`：

```python
from typing import Dict, Any
from tools.base_tool import BaseTool
from settings import settings

class NewTool(BaseTool):
    """工具描述"""

    name = "new_tool"
    description = "工具用途说明"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具逻辑

        Args:
            params: 参数字典

        Returns:
            结果字典
        """
        # 实现查询逻辑
        result = self._query_data(params)

        return {
            "data": result,
            "count": len(result),
            # 其他返回字段
        }

    def _query_data(self, params: Dict[str, Any]):
        """内部查询方法"""
        # 实现具体逻辑
        pass
```

### 2. 安全原则

- 只读操作，不修改系统状态
- 不执行动态命令
- 限制访问路径
- 验证所有输入参数

---

## 版本路线图

### V1.1 - 学生入口

新增问题：
- 我上周做了哪些题？
- 哪些题没做完？
- 我最弱的是哪一类？
- 今天应该先练什么？
- 上次错得最多的是什么？

```python
# 需要添加的工具
- student_learning_history.py
- student_weak_points.py
- student_daily_plan.py
```

### V1.2 - 家长入口

新增问题：
- 孩子这周完成度怎么样？
- 哪些是真会了？
- 这周应该重点抓什么？

### V2.0 - 多场景扩展

- 养老健康入口
- 医疗问诊入口
- 多用户系统

---

## 技术扩展点

### LLM 意图辅助 (V1.1)

```python
# backend/services/intent_parser.py

async def parse_with_llm(self, transcript: str):
    """使用 LLM 辅助意图识别"""
    # 规则匹配失败时调用
    prompt = f"""
    用户问题: {transcript}
    可用意图: {list(self.rules.keys())}
    请返回最匹配的意图名称。
    """
    # 调用 LLM API
    ...
```

### 多轮对话 (V1.2)

```python
# backend/services/context_manager.py

class ContextManager:
    """会话上下文管理"""

    def __init__(self):
        self.sessions = {}

    def get_context(self, session_id: str) -> dict:
        return self.sessions.get(session_id, {})

    def update_context(self, session_id: str, data: dict):
        self.sessions[session_id] = {
            **self.sessions.get(session_id, {}),
            **data
        }
```

### WebSocket 实时通信 (V2.0)

```python
# backend/routes/ws.py

from fastapi import WebSocket

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = await process_query(data)
        await websocket.send_json(response)
```

---

## 最佳实践

1. **保持简单** - 每个工具只做一件事
2. **安全优先** - 始终验证输入，限制权限
3. **测试覆盖** - 为新功能编写单元测试
4. **文档同步** - 更新 API 文档和 README

---

*LIGHT HOPE V5.3 Compliant*
