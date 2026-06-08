"""
瓶颈逆向诊断导航器。

当用户在某一语法点连续失败达到阈值时，通过知识图谱逆向追溯前置依赖，
生成针对性复习路径与微操练推荐。
"""

from __future__ import annotations

import logging

from app.engine.knowledge_graph import KnowledgeGraph
from app.models.schemas import BottleneckDiagnosis, MicroDrill, PrerequisiteNode

logger = logging.getLogger(__name__)


class BottleneckNavigator:
    """
    瓶颈逆向诊断导航器。

    结合知识图谱与连续失败计数，判断用户是否陷入语法瓶颈，
    并返回前置依赖节点与微操练建议。

    Attributes:
        knowledge_graph: 语法知识图谱访问层。
        failure_threshold: 触发瓶颈诊断的连续失败次数阈值。
        max_prerequisite_depth: 逆向追溯的最大深度。
    """

    DEFAULT_FAILURE_THRESHOLD = 3
    DEFAULT_MAX_DEPTH = 3

    def __init__(
        self,
        knowledge_graph: KnowledgeGraph | None = None,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        max_prerequisite_depth: int = DEFAULT_MAX_DEPTH,
    ) -> None:
        """
        初始化瓶颈导航器。

        Args:
            knowledge_graph: 知识图谱实例，默认新建内存图。
            failure_threshold: 连续失败触发阈值。
            max_prerequisite_depth: 前置依赖最大追溯深度。
        """
        self.knowledge_graph = knowledge_graph or KnowledgeGraph()
        self.failure_threshold = failure_threshold
        self.max_prerequisite_depth = max_prerequisite_depth

    def check_bottleneck(
        self,
        user_id: str,
        grammar_point: str,
        consecutive_failures: int,
    ) -> BottleneckDiagnosis:
        """
        检查用户是否在指定语法点陷入瓶颈，并生成逆向诊断结果。

        当 ``consecutive_failures >= failure_threshold`` 时触发瓶颈诊断：
        1. 通过知识图谱逆向追溯前置依赖节点
        2. 生成复习建议与微操练 ID 列表

        Args:
            user_id: 用户唯一标识。
            grammar_point: 当前卡住的语法点 ID。
            consecutive_failures: 该语法点连续失败次数。

        Returns:
            BottleneckDiagnosis 诊断结果。
        """
        logger.info(
            "瓶颈检查 user_id=%s grammar_point=%s failures=%d",
            user_id,
            grammar_point,
            consecutive_failures,
        )

        is_bottleneck = consecutive_failures >= self.failure_threshold

        if not is_bottleneck:
            return BottleneckDiagnosis(
                is_bottleneck=False,
                grammar_point=grammar_point,
                consecutive_failures=consecutive_failures,
                failure_threshold=self.failure_threshold,
                prerequisite_nodes=[],
                recommendation="继续当前语法点练习，尚未触发瓶颈诊断。",
                micro_drill_ids=[],
            )

        prerequisites = self.knowledge_graph.get_prerequisites(
            grammar_point,
            max_depth=self.max_prerequisite_depth,
        )

        prerequisite_nodes = [
            PrerequisiteNode(
                node_id=node.node_id,
                label=node.label,
                description=node.description,
                depth=depth,
            )
            for node, depth in prerequisites
        ]

        # 优先推荐深度最浅（最直接）的前置节点微操练
        target_nodes = (
            [n for n in prerequisite_nodes if n.depth == 1]
            if prerequisite_nodes
            else []
        )
        micro_drill_ids: list[str] = []
        micro_drills: list[dict] = []
        
        for node in target_nodes:
            micro_drill_ids.extend(
                self.knowledge_graph.get_micro_drill_ids(node.node_id)
            )
            # 添加内联微操练题目
            micro_drills.extend(
                self.knowledge_graph.get_micro_drills(node.node_id, limit=1)
            )

        recommendation = self._build_recommendation(
            grammar_point, prerequisite_nodes, target_nodes
        )

        return BottleneckDiagnosis(
            is_bottleneck=True,
            grammar_point=grammar_point,
            consecutive_failures=consecutive_failures,
            failure_threshold=self.failure_threshold,
            prerequisite_nodes=prerequisite_nodes,
            recommendation=recommendation,
            micro_drill_ids=micro_drill_ids,
            micro_drills=[
                MicroDrill(**drill) for drill in micro_drills
            ] if micro_drills else [],
        )

    def _build_recommendation(
        self,
        grammar_point: str,
        all_prerequisites: list[PrerequisiteNode],
        direct_prerequisites: list[PrerequisiteNode],
    ) -> str:
        """
        生成面向用户的瓶颈诊断建议文案。

        Args:
            grammar_point: 目标语法点。
            all_prerequisites: 全部追溯到的前置节点。
            direct_prerequisites: 直接前置依赖（depth=1）。

        Returns:
            中文建议字符串。
        """
        target_node = self.knowledge_graph.get_node(grammar_point)
        label = target_node.label if target_node else grammar_point

        if not direct_prerequisites:
            return (
                f"你在「{label}」已连续多次出错。"
                f"建议回顾该语法点的基础规则与例句，完成推荐微操练后再回来挑战。"
            )

        prereq_labels = "、".join(n.label for n in direct_prerequisites)
        return (
            f"你在「{label}」已连续 {self.failure_threshold} 次以上出错，"
            f"可能存在前置知识薄弱。建议先巩固：{prereq_labels}，"
            f"完成 {len(direct_prerequisites)} 组前置微操练后，再返回本语法点。"
        )


# ---------------------------------------------------------------------------
# 代码检查清单
# ---------------------------------------------------------------------------
# [x] BottleneckNavigator 类已实现
# [x] check_bottleneck(user_id, grammar_point, consecutive_failures) 已实现
# [x] 连续失败 >= 阈值时触发逆向追溯
# [x] 返回 BottleneckDiagnosis 含 prerequisite_nodes 与 micro_drill_ids
# [x] 完整类型提示、中文注释与 Google-style docstring
