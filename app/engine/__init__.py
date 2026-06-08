"""
Smart Grammar System 核心引擎包。

导出双轨解析器、瓶颈导航器、知识图谱访问层与词典引擎。
"""

from app.engine.bottleneck_navigator import BottleneckNavigator
from app.engine.dual_track_parser import DualTrackParser
from app.engine.knowledge_graph import KnowledgeGraph
from app.engine.lexicon import LexiconEngine, get_lexicon_engine

__all__ = [
    "BottleneckNavigator",
    "DualTrackParser",
    "KnowledgeGraph",
    "LexiconEngine",
    "get_lexicon_engine",
]
