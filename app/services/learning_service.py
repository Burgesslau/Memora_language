"""
学习服务层。

编排双轨解析、瓶颈诊断与学习记录等业务逻辑，
作为 API 层与引擎层之间的中间协调者。
"""

from __future__ import annotations

import logging
from typing import Literal

from app.engine.bottleneck_navigator import BottleneckNavigator
from app.engine.dual_track_parser import DualTrackParser
from app.models.schemas import (
    BottleneckDiagnosis,
    ParseOutputResponse,
)

logger = logging.getLogger(__name__)


class LearningService:
    """
    学习业务服务。

    封装引擎调用与学习侧效应（记录静默错误、更新知识追踪等），
    当前骨架仅完成引擎编排，持久化逻辑留待后续阶段实现。

    Attributes:
        parser: 双轨制语法解析器。
        navigator: 瓶颈逆向诊断导航器。
    """

    def __init__(
        self,
        parser: DualTrackParser | None = None,
        navigator: BottleneckNavigator | None = None,
    ) -> None:
        """
        初始化学习服务。

        Args:
            parser: 可选 DualTrackParser 实例。
            navigator: 可选 BottleneckNavigator 实例。
        """
        self.parser = parser or DualTrackParser()
        self.navigator = navigator or BottleneckNavigator()

    async def evaluate_speech(
        self,
        user_text: str,
        mode: Literal["free", "strict"],
        user_id: str | None = None,
    ) -> ParseOutputResponse:
        """
        评价用户口语输出（双轨制）。

        Args:
            user_text: 语音转写文本。
            mode: ``"free"`` 或 ``"strict"``。
            user_id: 可选用户 ID。

        Returns:
            ParseOutputResponse 解析结果。
        """
        result = self.parser.parse_output(
            user_text=user_text,
            mode=mode,
            user_id=user_id,
        )

        # 后续阶段：异步写入 PostgreSQL 学习记录、更新 BKT 状态
        if user_id:
            await self._record_learning_event(user_id, result)

        return result

    async def diagnose_bottleneck(
        self,
        user_id: str,
        grammar_point: str,
        consecutive_failures: int,
    ) -> BottleneckDiagnosis:
        """
        执行瓶颈逆向诊断。

        Args:
            user_id: 用户 ID。
            grammar_point: 语法点标识。
            consecutive_failures: 连续失败次数。

        Returns:
            BottleneckDiagnosis 诊断结果。
        """
        diagnosis = self.navigator.check_bottleneck(
            user_id=user_id,
            grammar_point=grammar_point,
            consecutive_failures=consecutive_failures,
        )

        if diagnosis.is_bottleneck:
            logger.info(
                "用户 %s 在 %s 触发瓶颈，推荐 %d 个前置节点",
                user_id,
                grammar_point,
                len(diagnosis.prerequisite_nodes),
            )

        return diagnosis

    async def _record_learning_event(
        self,
        user_id: str,
        result: ParseOutputResponse,
    ) -> None:
        """
        记录学习事件（骨架占位，后续接入 PostgreSQL）。

        Args:
            user_id: 用户 ID。
            result: 解析结果。
        """
        logger.debug(
            "学习事件记录占位 user_id=%s mode=%s passed=%s silent_errors=%d error_tags=%d",
            user_id,
            result.mode,
            result.passed,
            len(result.silent_errors),
            len(result.error_tags),
        )


# ---------------------------------------------------------------------------
# 代码检查清单
# ---------------------------------------------------------------------------
# [x] LearningService 编排 DualTrackParser 与 BottleneckNavigator
# [x] evaluate_speech / diagnose_bottleneck 异步接口
# [x] _record_learning_event 持久化占位（可扩展）
# [x] 完整类型提示与中文注释
