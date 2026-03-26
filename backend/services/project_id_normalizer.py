"""
M537 Voice Gateway - Project ID Normalizer
处理语音识别中项目编号的纠错和规范化
"""
import re
from typing import Optional


# 中文数字映射
CHINESE_NUMBERS = {
    "零": "0", "一": "1", "二": "2", "三": "3", "四": "4",
    "五": "5", "六": "6", "七": "7", "八": "8", "九": "9",
    "〇": "0", "两": "2"
}

# 常见语音识别错误映射
COMMON_MISTAKES = {
    # 字母发音错误
    "em": "m", "am": "m", "im": "m", "um": "m",
    "and": "m", "n": "m",
    # 数字发音错误
    "八千": "8000", "五千": "5000", "一千": "1000",
}


def normalize_project_id(raw_id: str) -> Optional[str]:
    """
    规范化项目编号

    处理常见的语音识别错误：
    - "m 536" -> "m536"
    - "m五三六" -> "m536"
    - "em536" -> "m536"
    - "项目536" -> "m536"

    Args:
        raw_id: 原始项目编号字符串

    Returns:
        规范化后的项目编号，如 "m536"
    """
    if not raw_id:
        return None

    # 转小写并去除空格
    normalized = raw_id.lower().strip()

    # 替换常见错误
    for mistake, correction in COMMON_MISTAKES.items():
        normalized = normalized.replace(mistake, correction)

    # 替换中文数字
    for chinese, digit in CHINESE_NUMBERS.items():
        normalized = normalized.replace(chinese, digit)

    # 移除所有空格
    normalized = re.sub(r"\s+", "", normalized)

    # 尝试提取 m + 数字 格式
    patterns = [
        r"^m(\d+)$",           # m536
        r"^m_(\d+)$",          # m_536
        r"^项目(\d+)$",        # 项目536
        r"(\d{3,5})$",         # 纯数字
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            number = match.group(1)
            return f"m{number}"

    # 如果已经是正确格式
    if re.match(r"^m\d+", normalized):
        # 提取数字部分
        numbers = re.findall(r"\d+", normalized)
        if numbers:
            return f"m{numbers[0]}"

    return None


def extract_project_id_from_text(text: str) -> Optional[str]:
    """
    从自然语言文本中提取项目编号

    示例：
    - "m536是什么项目" -> "m536"
    - "介绍一下536项目" -> "m536"
    - "项目 537 的情况" -> "m537"

    Args:
        text: 用户输入文本

    Returns:
        提取并规范化的项目编号
    """
    if not text:
        return None

    text_lower = text.lower()

    # 尝试匹配多种模式
    patterns = [
        r"m\s*(\d+)",           # m536, m 536
        r"[mM]_?(\d+)",         # M536, m_536
        r"项目\s*(\d+)",        # 项目536
        r"(\d{3,5})\s*项目",    # 536项目
        r"(\d{3,5})\s*是什么",  # 536是什么
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            number = match.group(1)
            # 验证数字范围 (合理的项目编号)
            if 1 <= int(number) <= 99999:
                return f"m{number}"

    return None


def fuzzy_match_project(query: str, project_list: list) -> Optional[str]:
    """
    模糊匹配项目名称

    Args:
        query: 查询字符串
        project_list: 可用项目列表

    Returns:
        最匹配的项目名称
    """
    if not query or not project_list:
        return None

    query_lower = query.lower()

    # 精确匹配
    for project in project_list:
        if project.lower() == query_lower:
            return project

    # 前缀匹配
    for project in project_list:
        if project.lower().startswith(query_lower):
            return project

    # 包含匹配
    for project in project_list:
        if query_lower in project.lower():
            return project

    return None
