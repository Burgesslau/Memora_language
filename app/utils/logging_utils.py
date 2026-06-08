"""
日志与可视化模块。

使用 loguru 和 rich 提供彩色、结构化的日志输出。
支持依存句法树、语法检测结果的终端可视化。
"""

from __future__ import annotations

import logging
import sys
from typing import Any

try:
    from loguru import logger as loguru_logger
    HAS_LOGURU = True
except ImportError:
    HAS_LOGURU = False

try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.tree import Tree
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def setup_colored_logging() -> None:
    """
    初始化彩色日志系统（使用 loguru）。

    配置：
    - INFO/DEBUG: 绿色/蓝色
    - WARNING: 黄色
    - ERROR/CRITICAL: 红色
    """
    if not HAS_LOGURU:
        return

    # 移除默认 handler
    loguru_logger.remove()

    # 添加彩色输出
    loguru_logger.add(
        sys.stdout,
        format=(
            "<level>{time:HH:mm:ss}</level> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
            "<level>{message}</level>"
        ),
        level="DEBUG",
        colorize=True,
    )


def log_dependency_tree(doc: Any) -> None:
    """
    在日志中打印依存句法树（ASCII 可视化）。

    Args:
        doc: spaCy Doc 对象。
    """
    if not HAS_RICH:
        return

    from rich.console import Console
    console = Console()

    # 构建树状结构
    tree = Tree("📋 [bold cyan]Dependency Tree[/bold cyan]")
    for token in doc:
        if token.head == token:
            # ROOT
            subtree = tree.add(
                f"[bold green]ROOT[/bold green]: {token.text} ({token.pos_})"
            )
            for child in token.children:
                _add_tree_children(subtree, child)

    console.print(tree)


def _add_tree_children(parent_tree: Tree, token: Any) -> None:
    """递归添加依存树的子节点。"""
    subtree = parent_tree.add(
        f"{token.dep_}: {token.text} ({token.pos_})"
    )
    for child in token.children:
        _add_tree_children(subtree, child)


def log_grammar_issues_table(issues: list[dict]) -> None:
    """
    以表格形式打印检测到的语法问题。

    Args:
        issues: 语法问题列表（字典格式）。
    """
    if not HAS_RICH:
        return

    from rich.console import Console
    console = Console()

    table = Table(title="🔍 Grammar Issues Detected")
    table.add_column("Grammar Point", style="cyan")
    table.add_column("Error Type", style="magenta")
    table.add_column("Severity", style="red")
    table.add_column("Message", style="yellow")

    for issue in issues:
        table.add_row(
            issue.get("grammar_point", "?"),
            issue.get("error_type", "?"),
            issue.get("severity", "?"),
            issue.get("message", "?"),
        )

    console.print(table)


def get_loguru_logger():
    """获取 loguru logger 单例（若可用）。"""
    if HAS_LOGURU:
        return loguru_logger
    return None


# 初始化彩色日志
setup_colored_logging()
