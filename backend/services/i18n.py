"""
M537 Voice Gateway - Internationalization (i18n) Service
Multi-language support for response messages
"""
from typing import Dict, Any, Optional
import re


class TranslationService:
    """
    Translation service supporting multiple languages.
    Default language is Chinese (zh-CN).
    """

    SUPPORTED_LANGUAGES = ["zh-CN", "en-US", "ja-JP"]
    DEFAULT_LANGUAGE = "zh-CN"

    # Translation dictionaries
    TRANSLATIONS = {
        # ========== 项目相关 ==========
        "count_projects.success": {
            "zh-CN": "当前共有 {total} 个项目，其中 P0 项目 {p0} 个，P1 项目 {p1} 个，P2 项目 {p2} 个，P3 项目 {p3} 个。",
            "en-US": "Currently there are {total} projects in total. P0: {p0}, P1: {p1}, P2: {p2}, P3: {p3}.",
            "ja-JP": "現在 {total} 件のプロジェクトがあります。P0: {p0}件、P1: {p1}件、P2: {p2}件、P3: {p3}件。"
        },
        "count_projects.empty": {
            "zh-CN": "当前没有任何项目。",
            "en-US": "No projects found.",
            "ja-JP": "プロジェクトがありません。"
        },

        "project_summary.success": {
            "zh-CN": "项目 {project_id}：{title}。{description}",
            "en-US": "Project {project_id}: {title}. {description}",
            "ja-JP": "プロジェクト {project_id}：{title}。{description}"
        },
        "project_summary.not_found": {
            "zh-CN": "没有找到项目 {project_id}。",
            "en-US": "Project {project_id} not found.",
            "ja-JP": "プロジェクト {project_id} が見つかりません。"
        },

        "missing_readme.success": {
            "zh-CN": "共有 {count} 个项目缺少 README：{projects}",
            "en-US": "{count} projects are missing README: {projects}",
            "ja-JP": "{count} 件のプロジェクトにREADMEがありません：{projects}"
        },
        "missing_readme.empty": {
            "zh-CN": "所有项目都有 README，很棒！",
            "en-US": "All projects have README files. Great!",
            "ja-JP": "すべてのプロジェクトにREADMEがあります。素晴らしい！"
        },

        "recent_updates.success": {
            "zh-CN": "最近 {days} 天有 {count} 个项目更新：{projects}",
            "en-US": "{count} projects updated in the last {days} days: {projects}",
            "ja-JP": "過去 {days} 日間に {count} 件のプロジェクトが更新されました：{projects}"
        },
        "recent_updates.empty": {
            "zh-CN": "最近 {days} 天没有项目更新。",
            "en-US": "No projects updated in the last {days} days.",
            "ja-JP": "過去 {days} 日間に更新されたプロジェクトはありません。"
        },

        # ========== 系统相关 ==========
        "system_status.success": {
            "zh-CN": "系统状态：CPU 使用率 {cpu}%，内存使用率 {memory}%，磁盘使用率 {disk}%。{warning}",
            "en-US": "System status: CPU {cpu}%, Memory {memory}%, Disk {disk}%. {warning}",
            "ja-JP": "システム状態：CPU {cpu}%、メモリ {memory}%、ディスク {disk}%。{warning}"
        },

        "disk_usage.success": {
            "zh-CN": "磁盘使用情况：共 {partition_count} 个分区。{partition_info}总容量 {total_size}，已使用 {total_used}，可用 {total_available}。",
            "en-US": "Disk usage: {partition_count} partitions. {partition_info}Total: {total_size}, Used: {total_used}, Available: {total_available}.",
            "ja-JP": "ディスク使用状況：{partition_count} 個のパーティション。{partition_info}合計 {total_size}、使用済み {total_used}、空き {total_available}。"
        },

        "uptime_info.success": {
            "zh-CN": "系统已运行 {uptime}。负载状态：{load_status}（1分钟负载 {load_1}，5分钟负载 {load_5}，15分钟负载 {load_15}）。{cpu_count} 核心，{logged_in_users} 个用户在线。",
            "en-US": "System uptime: {uptime}. Load: {load_status} (1min: {load_1}, 5min: {load_5}, 15min: {load_15}). {cpu_count} cores, {logged_in_users} users online.",
            "ja-JP": "システム稼働時間：{uptime}。負荷状態：{load_status}（1分 {load_1}、5分 {load_5}、15分 {load_15}）。{cpu_count} コア、{logged_in_users} ユーザーがオンライン。"
        },

        "process_list.success": {
            "zh-CN": "当前共有 {total_processes} 个进程运行。CPU 占用最高：{top_cpu_info}。内存占用最高：{top_mem_info}。",
            "en-US": "{total_processes} processes running. Top CPU: {top_cpu_info}. Top Memory: {top_mem_info}.",
            "ja-JP": "現在 {total_processes} 個のプロセスが実行中。CPU使用率最高：{top_cpu_info}。メモリ使用率最高：{top_mem_info}。"
        },

        # ========== 网络相关 ==========
        "list_ports.success": {
            "zh-CN": "当前有 {count} 个端口在监听：{ports}",
            "en-US": "{count} ports are listening: {ports}",
            "ja-JP": "現在 {count} 個のポートがリッスンしています：{ports}"
        },
        "list_ports.empty": {
            "zh-CN": "当前没有端口在监听。",
            "en-US": "No ports are currently listening.",
            "ja-JP": "現在リッスンしているポートはありません。"
        },

        "network_info.success": {
            "zh-CN": "网络状态：共 {interface_count} 个接口活跃。{interface_info}当前有 {connection_count} 个活跃连接。",
            "en-US": "Network status: {interface_count} active interfaces. {interface_info}{connection_count} active connections.",
            "ja-JP": "ネットワーク状態：{interface_count} 個のインターフェースがアクティブ。{interface_info}現在 {connection_count} 個のアクティブな接続。"
        },

        # ========== 容器服务 ==========
        "list_containers.success": {
            "zh-CN": "当前有 {running} 个容器运行中，共 {total} 个容器：{containers}",
            "en-US": "{running} containers running out of {total} total: {containers}",
            "ja-JP": "現在 {running} 個のコンテナが実行中（合計 {total} 個）：{containers}"
        },
        "list_containers.empty": {
            "zh-CN": "当前没有 Docker 容器。",
            "en-US": "No Docker containers found.",
            "ja-JP": "Dockerコンテナがありません。"
        },

        "p0_health.success": {
            "zh-CN": "P0 服务状态：共 {total} 个关键服务，{healthy} 个健康，{unhealthy} 个异常。{details}",
            "en-US": "P0 service status: {total} critical services, {healthy} healthy, {unhealthy} unhealthy. {details}",
            "ja-JP": "P0サービス状態：{total} 個の重要サービス、{healthy} 個が正常、{unhealthy} 個が異常。{details}"
        },

        "list_tmux.success": {
            "zh-CN": "当前有 {count} 个 tmux 会话：{sessions}",
            "en-US": "{count} tmux sessions found: {sessions}",
            "ja-JP": "現在 {count} 個のtmuxセッションがあります：{sessions}"
        },
        "list_tmux.empty": {
            "zh-CN": "当前没有 tmux 会话。",
            "en-US": "No tmux sessions found.",
            "ja-JP": "tmuxセッションがありません。"
        },

        # ========== 日志分析 ==========
        "recent_errors.success": {
            "zh-CN": "最近 {hours} 小时内有 {count} 个错误：{errors}",
            "en-US": "{count} errors in the last {hours} hours: {errors}",
            "ja-JP": "過去 {hours} 時間に {count} 件のエラー：{errors}"
        },
        "recent_errors.empty": {
            "zh-CN": "最近 {hours} 小时内没有发现错误，系统运行正常。",
            "en-US": "No errors in the last {hours} hours. System is running normally.",
            "ja-JP": "過去 {hours} 時間にエラーはありません。システムは正常に動作しています。"
        },

        "service_logs.success": {
            "zh-CN": "服务 {service} 的最近日志：\n{logs}",
            "en-US": "Recent logs for {service}:\n{logs}",
            "ja-JP": "{service} の最新ログ：\n{logs}"
        },

        # ========== 任务调度 ==========
        "cron_jobs.success": {
            "zh-CN": "共有 {count} 个定时任务：{jobs}",
            "en-US": "{count} scheduled jobs found: {jobs}",
            "ja-JP": "{count} 件のスケジュールジョブがあります：{jobs}"
        },
        "cron_jobs.empty": {
            "zh-CN": "当前没有定时任务。",
            "en-US": "No scheduled jobs found.",
            "ja-JP": "スケジュールジョブがありません。"
        },

        # ========== Git状态 ==========
        "git_status.success": {
            "zh-CN": "项目 {project_id} 的 Git 状态：分支 {branch}，{modified_count} 个文件已修改，{untracked_count} 个未跟踪文件。{last_commit_info}",
            "en-US": "Git status for {project_id}: Branch {branch}, {modified_count} modified files, {untracked_count} untracked. {last_commit_info}",
            "ja-JP": "{project_id} のGit状態：ブランチ {branch}、{modified_count} 件の変更ファイル、{untracked_count} 件の未追跡ファイル。{last_commit_info}"
        },
        "git_status.clean": {
            "zh-CN": "项目 {project_id} 的 Git 仓库状态干净，没有待提交的更改。当前分支：{branch}",
            "en-US": "Git repository for {project_id} is clean. Current branch: {branch}",
            "ja-JP": "{project_id} のGitリポジトリはクリーンです。現在のブランチ：{branch}"
        },

        # ========== 通用错误 ==========
        "error.intent_not_recognized": {
            "zh-CN": "抱歉，我没有理解你的问题。请尝试以下查询方式：",
            "en-US": "Sorry, I didn't understand your question. Please try one of these:",
            "ja-JP": "申し訳ありません、ご質問を理解できませんでした。以下のようにお試しください："
        },
        "error.execution_failed": {
            "zh-CN": "执行失败：{error}",
            "en-US": "Execution failed: {error}",
            "ja-JP": "実行に失敗しました：{error}"
        },
        "error.validation_error": {
            "zh-CN": "参数验证失败：{detail}",
            "en-US": "Validation error: {detail}",
            "ja-JP": "バリデーションエラー：{detail}"
        },

        # ========== UI 文本 ==========
        "ui.quick_questions": {
            "zh-CN": "快捷问题：",
            "en-US": "Quick Questions:",
            "ja-JP": "クイック質問："
        },
        "ui.system_status": {
            "zh-CN": "系统状态",
            "en-US": "System Status",
            "ja-JP": "システム状態"
        },
        "ui.connected": {
            "zh-CN": "已连接",
            "en-US": "Connected",
            "ja-JP": "接続済み"
        },
        "ui.disconnected": {
            "zh-CN": "连接断开",
            "en-US": "Disconnected",
            "ja-JP": "切断"
        },
    }

    def __init__(self, default_language: str = None):
        self.default_language = default_language or self.DEFAULT_LANGUAGE

    def translate(
        self,
        key: str,
        language: str = None,
        **kwargs
    ) -> str:
        """
        Translate a key to the specified language.

        Args:
            key: Translation key (e.g., 'count_projects.success')
            language: Target language code (e.g., 'en-US')
            **kwargs: Format parameters

        Returns:
            Translated and formatted string
        """
        lang = language or self.default_language

        # Get translation dictionary for key
        translations = self.TRANSLATIONS.get(key)
        if not translations:
            return key  # Return key if not found

        # Get translation for language, fallback to default
        template = translations.get(lang)
        if not template:
            template = translations.get(self.DEFAULT_LANGUAGE, key)

        # Format with parameters
        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    def get_language_from_header(self, accept_language: str) -> str:
        """
        Parse Accept-Language header and return best matching language.

        Args:
            accept_language: Accept-Language header value

        Returns:
            Best matching language code
        """
        if not accept_language:
            return self.default_language

        # Parse Accept-Language header
        # Format: en-US,en;q=0.9,zh-CN;q=0.8
        languages = []
        for item in accept_language.split(","):
            parts = item.strip().split(";")
            lang = parts[0].strip()
            q = 1.0
            if len(parts) > 1:
                q_match = re.search(r"q=([0-9.]+)", parts[1])
                if q_match:
                    q = float(q_match.group(1))
            languages.append((lang, q))

        # Sort by quality
        languages.sort(key=lambda x: x[1], reverse=True)

        # Find best matching supported language
        for lang, _ in languages:
            # Exact match
            if lang in self.SUPPORTED_LANGUAGES:
                return lang

            # Language family match (e.g., 'en' matches 'en-US')
            lang_base = lang.split("-")[0]
            for supported in self.SUPPORTED_LANGUAGES:
                if supported.startswith(lang_base):
                    return supported

        return self.default_language

    def get_supported_languages(self) -> list:
        """Return list of supported language codes"""
        return self.SUPPORTED_LANGUAGES.copy()


# Global instance
translator = TranslationService()


def t(key: str, language: str = None, **kwargs) -> str:
    """
    Shorthand translation function.

    Usage:
        t('count_projects.success', total=100, p0=10, p1=20)
        t('error.intent_not_recognized', language='en-US')
    """
    return translator.translate(key, language, **kwargs)


def detect_language(request_headers: dict) -> str:
    """
    Detect language from request headers.

    Args:
        request_headers: Dictionary of request headers

    Returns:
        Detected language code
    """
    accept_language = request_headers.get("accept-language", "")
    return translator.get_language_from_header(accept_language)
