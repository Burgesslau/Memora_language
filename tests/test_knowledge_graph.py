"""
KnowledgeGraph 单元测试。

验证内存图与前端 graph-data.ts 节点元数据一致。
"""

from __future__ import annotations

from app.engine.knowledge_graph import KnowledgeGraph

# 与 frontend/src/services/graph-data.ts GRAPH_NODES 对齐（id / label / description）
FRONTEND_GRAPH_NODES: list[dict[str, str]] = [
    {
        "id": "present_simple",
        "label": "一般现在时",
        "description": "主语 + 动词原形/第三人称单数",
    },
    {
        "id": "past_simple",
        "label": "一般过去时",
        "description": "主语 + 动词过去式",
    },
    {
        "id": "third_person_singular",
        "label": "第三人称单数",
        "description": "he/she/it 后动词加 -s",
    },
    {
        "id": "auxiliary_have_be",
        "label": "助动词 have/be",
        "description": "助动词 have 与 be 的基本用法",
    },
    {
        "id": "present_continuous",
        "label": "现在进行时",
        "description": "be + V-ing 结构",
    },
    {
        "id": "present_perfect",
        "label": "现在完成时",
        "description": "have/has + 过去分词",
    },
    {
        "id": "past_participle",
        "label": "过去分词",
        "description": "规则/不规则动词过去分词形式",
    },
    {
        "id": "present_perfect_continuous",
        "label": "现在完成进行时",
        "description": "have/has been + V-ing",
    },
    {
        "id": "indefinite_article",
        "label": "不定冠词 a/an",
        "description": "可数名词单数前的 a/an 选择",
    },
    {
        "id": "passive_voice",
        "label": "被动语态",
        "description": "be + 过去分词",
    },
]


class TestKnowledgeGraphSync:
    """前后端图谱节点元数据一致性。"""

    def test_all_frontend_nodes_exist_in_backend(self) -> None:
        kg = KnowledgeGraph()
        for expected in FRONTEND_GRAPH_NODES:
            node = kg.get_node(expected["id"])
            assert node is not None, f"Missing backend node: {expected['id']}"
            assert node.label == expected["label"]
            assert node.description == expected["description"]

    def test_passive_voice_has_prerequisites(self) -> None:
        kg = KnowledgeGraph()
        node = kg.get_node("passive_voice")
        assert node is not None
        assert "auxiliary_have_be" in node.prerequisites
        assert "past_participle" in node.prerequisites

    def test_passive_voice_micro_drills(self) -> None:
        kg = KnowledgeGraph()
        drills = kg.get_micro_drills("passive_voice", limit=1)
        assert len(drills) == 1
        assert drills[0]["grammar_point"] == "passive_voice"

    def test_bottleneck_prerequisites_present_perfect_continuous(self) -> None:
        kg = KnowledgeGraph()
        prereqs = kg.get_prerequisites("present_perfect_continuous", max_depth=2)
        node_ids = {n.node_id for n, _ in prereqs}
        assert "present_perfect" in node_ids
        assert "present_continuous" in node_ids
