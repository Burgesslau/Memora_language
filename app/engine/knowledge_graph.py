"""
语法知识图谱模块。

封装 Neo4j 图数据库访问，提供语法点节点查询、前置依赖逆向追溯等功能。
当前为可扩展骨架，内置内存降级图用于开发与单元测试。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """知识图谱中的语法点节点。"""

    node_id: str
    label: str
    description: str = ""
    prerequisites: list[str] = field(default_factory=list)


class KnowledgeGraph:
    """
    语法知识图谱访问层。

    生产环境连接 Neo4j；开发/测试环境使用内置内存图。
    节点间 ``PREREQUISITE_OF`` 边表示「A 是 B 的前置依赖」。

    Example:
        >>> kg = KnowledgeGraph()
        >>> kg.get_prerequisites("present_perfect_continuous", max_depth=2)
    """

    # 内置降级图：语法点 -> 前置依赖列表
    _FALLBACK_GRAPH: dict[str, GraphNode] = {
        "present_perfect_continuous": GraphNode(
            node_id="present_perfect_continuous",
            label="现在完成进行时",
            description="have/has been + V-ing",
            prerequisites=["present_perfect", "present_continuous", "auxiliary_have_be"],
        ),
        "present_perfect": GraphNode(
            node_id="present_perfect",
            label="现在完成时",
            description="have/has + 过去分词",
            prerequisites=["past_participle", "auxiliary_have_be"],
        ),
        "present_continuous": GraphNode(
            node_id="present_continuous",
            label="现在进行时",
            description="be + V-ing 结构",
            prerequisites=["auxiliary_have_be", "present_simple"],
        ),
        "auxiliary_have_be": GraphNode(
            node_id="auxiliary_have_be",
            label="助动词 have/be",
            description="助动词 have 与 be 的基本用法",
            prerequisites=["present_simple"],
        ),
        "past_participle": GraphNode(
            node_id="past_participle",
            label="过去分词",
            description="规则/不规则动词过去分词形式",
            prerequisites=["past_simple"],
        ),
        "present_simple": GraphNode(
            node_id="present_simple",
            label="一般现在时",
            description="主语 + 动词原形/第三人称单数",
            prerequisites=[],
        ),
        "past_simple": GraphNode(
            node_id="past_simple",
            label="一般过去时",
            description="主语 + 动词过去式",
            prerequisites=["present_simple"],
        ),
        "third_person_singular": GraphNode(
            node_id="third_person_singular",
            label="第三人称单数",
            description="he/she/it 后动词加 -s",
            prerequisites=["present_simple"],
        ),
        "indefinite_article": GraphNode(
            node_id="indefinite_article",
            label="不定冠词 a/an",
            description="可数名词单数前的 a/an 选择",
            prerequisites=[],
        ),
        "passive_voice": GraphNode(
            node_id="passive_voice",
            label="被动语态",
            description="be + 过去分词",
            prerequisites=["auxiliary_have_be", "past_participle"],
        ),
    }

    def __init__(
        self,
        neo4j_uri: str | None = None,
        neo4j_user: str | None = None,
        neo4j_password: str | None = None,
    ) -> None:
        """
        初始化知识图谱连接。

        Args:
            neo4j_uri: Neo4j Bolt URI，如 ``bolt://localhost:7687``。
            neo4j_user: Neo4j 用户名。
            neo4j_password: Neo4j 密码。
        """
        self._driver: Any | None = None
        if neo4j_uri and neo4j_user and neo4j_password:
            self._connect_neo4j(neo4j_uri, neo4j_user, neo4j_password)
        else:
            logger.info("未配置 Neo4j，使用内置内存知识图谱")

    def _connect_neo4j(self, uri: str, user: str, password: str) -> None:
        """建立 Neo4j 驱动连接。"""
        try:
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info("Neo4j 连接已建立: %s", uri)
        except ImportError:
            logger.warning("neo4j 驱动未安装，回退至内存图谱")
            self._driver = None

    def close(self) -> None:
        """关闭 Neo4j 驱动连接。"""
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def get_node(self, node_id: str) -> GraphNode | None:
        """
        按 ID 获取语法点节点。

        Args:
            node_id: 语法点标识。

        Returns:
            GraphNode 或 ``None``。
        """
        if self._driver is not None:
            return self._get_node_neo4j(node_id)
        return self._FALLBACK_GRAPH.get(node_id)

    def get_prerequisites(
        self,
        node_id: str,
        max_depth: int = 3,
    ) -> list[tuple[GraphNode, int]]:
        """
        逆向追溯前置依赖节点（BFS）。

        Args:
            node_id: 目标语法点 ID。
            max_depth: 最大追溯深度。

        Returns:
            ``(GraphNode, depth)`` 列表，按深度升序排列。
        """
        if self._driver is not None:
            return self._get_prerequisites_neo4j(node_id, max_depth)
        return self._get_prerequisites_fallback(node_id, max_depth)

    def _get_prerequisites_fallback(
        self,
        node_id: str,
        max_depth: int,
    ) -> list[tuple[GraphNode, int]]:
        """内存图 BFS 逆向追溯。"""
        results: list[tuple[GraphNode, int]] = []
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(node_id, 0)]

        while queue:
            current_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            node = self._FALLBACK_GRAPH.get(current_id)
            if node is None:
                continue
            for prereq_id in node.prerequisites:
                if prereq_id in visited:
                    continue
                visited.add(prereq_id)
                prereq_node = self._FALLBACK_GRAPH.get(prereq_id)
                if prereq_node is None:
                    continue
                results.append((prereq_node, depth + 1))
                queue.append((prereq_id, depth + 1))

        results.sort(key=lambda x: x[1])
        return results

    def _get_node_neo4j(self, node_id: str) -> GraphNode | None:
        """从 Neo4j 查询单个节点（骨架实现）。"""
        query = """
        MATCH (n:GrammarPoint {node_id: $node_id})
        OPTIONAL MATCH (pre)-[:PREREQUISITE_OF]->(n)
        RETURN n.node_id AS node_id, n.label AS label,
               n.description AS description,
               collect(pre.node_id) AS prerequisites
        """
        with self._driver.session() as session:
            record = session.run(query, node_id=node_id).single()
            if record is None:
                return None
            return GraphNode(
                node_id=record["node_id"],
                label=record["label"],
                description=record.get("description", ""),
                prerequisites=record["prerequisites"] or [],
            )

    def _get_prerequisites_neo4j(
        self,
        node_id: str,
        max_depth: int,
    ) -> list[tuple[GraphNode, int]]:
        """从 Neo4j 逆向追溯前置依赖（骨架实现）。"""
        query = """
        MATCH path = (pre:GrammarPoint)-[:PREREQUISITE_OF*1..$max_depth]->(target:GrammarPoint {node_id: $node_id})
        UNWIND range(0, length(path)-1) AS idx
        WITH nodes(path)[idx] AS node, idx AS depth
        RETURN DISTINCT node.node_id AS node_id, node.label AS label,
               node.description AS description, depth
        ORDER BY depth
        """
        results: list[tuple[GraphNode, int]] = []
        with self._driver.session() as session:
            for record in session.run(query, node_id=node_id, max_depth=max_depth):
                results.append(
                    (
                        GraphNode(
                            node_id=record["node_id"],
                            label=record["label"],
                            description=record.get("description", ""),
                        ),
                        record["depth"],
                    )
                )
        return results

    def get_micro_drill_ids(self, node_id: str) -> list[str]:
        """
        获取指定语法点关联的微操练 ID 列表。

        Args:
            node_id: 语法点 ID。

        Returns:
            微操练 ID 列表。
        """
        # 骨架：按节点 ID 生成占位操练 ID
        return [f"drill_{node_id}_01", f"drill_{node_id}_02"]

    def get_micro_drills(self, node_id: str, limit: int = 2) -> list[dict]:
        """
        获取指定语法点关联的微操练题目（内联返回）。

        Args:
            node_id: 语法点 ID。
            limit: 返回数量限制。

        Returns:
            微操练题目列表（字典格式）。
        """
        node = self.get_node(node_id)
        if node is None:
            return []

        # 骨架：生成示例微操练题目
        drills = []
        for i in range(1, limit + 1):
            drills.append({
                "drill_id": f"drill_{node_id}_{i:02d}",
                "grammar_point": node_id,
                "question": f"{node.label} 练习题 {i}",
                "example_sentence": f"Example: {node.description}",
                "correct_answer": "答案占位",
                "options": ["选项 A", "选项 B", "选项 C"],
                "explanation": f"这道题考查的是 {node.label} 的用法。",
                "difficulty": 2,
            })
        return drills


# ---------------------------------------------------------------------------
# 代码检查清单
# ---------------------------------------------------------------------------
# [x] GraphNode 数据结构
# [x] KnowledgeGraph 支持 Neo4j 与内存降级双模式
# [x] get_prerequisites 逆向 BFS 追溯前置依赖
# [x] get_micro_drill_ids 微操练 ID 查询（可扩展）
# [x] 完整类型提示与中文注释
