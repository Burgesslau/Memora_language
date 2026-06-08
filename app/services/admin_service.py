"""
管理员接口模块 — BKT 状态监控与系统诊断。

提供轻量级 REST 端点用于实时查看用户的语法掌握状态，
支持系统调试和学习效果分析。
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class BKTStatus(BaseModel):
    """Bayesian Knowledge Tracing 状态快照。"""

    user_id: str = Field(..., description="用户 ID")
    grammar_point: str = Field(..., description="语法点标识")
    mastery_probability: float = Field(
        ..., ge=0.0, le=1.0, description="掌握概率 P(L)"
    )
    guess_probability: float = Field(
        default=0.0, ge=0.0, le=1.0, description="蒙对概率 P(G)"
    )
    slip_probability: float = Field(
        default=0.1, ge=0.0, le=1.0, description="失误概率 P(S)"
    )
    learn_probability: float = Field(
        default=0.1, ge=0.0, le=1.0, description="学习概率 P(T)"
    )
    attempts: int = Field(default=0, ge=0, description="尝试次数")
    last_attempt_at: str | None = Field(default=None, description="最后尝试时间")


class BKTMatrixResponse(BaseModel):
    """BKT 掌握度矩阵。"""

    user_id: str = Field(..., description="用户 ID")
    timestamp: str = Field(..., description="查询时间戳")
    mastery_matrix: list[BKTStatus] = Field(
        default_factory=list, description="所有语法点的掌握概率"
    )
    overall_mastery: float = Field(
        default=0.0, ge=0.0, le=1.0, description="整体掌握度平均值"
    )
    bottleneck_points: list[str] = Field(
        default_factory=list,
        description="掌握度 < 0.5 的瓶颈语法点",
    )


async def get_bkt_status(user_id: str) -> BKTMatrixResponse:
    """
    获取用户的 BKT 掌握度矩阵（当前为骨架）。

    Args:
        user_id: 用户 ID。

    Returns:
        BKTMatrixResponse 包含所有语法点的掌握状态。

    Note:
        在 Phase 2/3 接入真实的 BKT 算法与 PostgreSQL 持久化。
    """
    from datetime import datetime

    logger.info("查询用户 BKT 状态 user_id=%s", user_id)

    # 骨架：返回示例数据
    statuses = [
        BKTStatus(
            user_id=user_id,
            grammar_point="present_simple",
            mastery_probability=0.85,
            attempts=8,
        ),
        BKTStatus(
            user_id=user_id,
            grammar_point="present_continuous",
            mastery_probability=0.72,
            attempts=5,
        ),
        BKTStatus(
            user_id=user_id,
            grammar_point="third_person_singular",
            mastery_probability=0.45,
            attempts=3,
        ),
    ]

    bottlenecks = [s.grammar_point for s in statuses if s.mastery_probability < 0.5]
    overall = sum(s.mastery_probability for s in statuses) / max(len(statuses), 1)

    return BKTMatrixResponse(
        user_id=user_id,
        timestamp=datetime.utcnow().isoformat(),
        mastery_matrix=statuses,
        overall_mastery=overall,
        bottleneck_points=bottlenecks,
    )
