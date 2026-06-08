"""
词典与形态学引擎（Lexicon & Morphology Engine）。

为语法解析提供词形变化、词根词缀、不规则形式、常见搭配等确定性支持，
提升双轨解析器的精度。

核心功能：
- 词形还原与形态分析（Lemmatization & Inflection）
- 词性与语法属性标注（POS + Grammatical Features）
- 常见搭配与用法库（Collocations）
- 词根词缀家族（Word Family）
- 与知识图谱联动
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LexicalEntry(BaseModel):
    """
    词典条目数据模型。

    Attributes:
        lemma: 词根（标准形式）
        pos: 词性 (VERB, NOUN, ADJ, ADV, etc.)
        inflections: 形态变化 {"past": "went", "past_participle": "gone", ...}
        irregular: 是否不规则变化
        grammatical_features: 语法属性 {"countable": True, "requires_article": True, ...}
        common_collocations: 常见搭配列表
        word_family: 派生词列表 (e.g., ["decide", "decision", "indecisive"])
        grammar_point_ids: 关联的语法点 ID (e.g., ["present_perfect", "past_simple"])
    """

    lemma: str
    pos: str
    inflections: Dict[str, str] = {}
    irregular: bool = False
    grammatical_features: Dict[str, bool] = {}
    common_collocations: List[str] = []
    word_family: List[str] = []
    grammar_point_ids: List[str] = []

    class Config:
        """Pydantic 配置。"""
        frozen = False


class LexiconEngine:
    """
    词典与形态学引擎。

    管理词条库、提供词形查询、搭配检索、词族扩展等功能。
    初始版本采用内置 JSON 词典，后期可扩展为数据库。

    Attributes:
        dictionary: 词条库 {lemma: LexicalEntry}
        collocations_index: 搭配索引 {collocation: [grammar_points]}
    """

    def __init__(self, dictionary_path: Optional[str] = None):
        """
        初始化词典引擎。

        Args:
            dictionary_path: 可选的外部字典文件路径（JSON 格式）。
                            如果不指定，使用内置默认字典。
        """
        self.dictionary: Dict[str, LexicalEntry] = {}
        self.collocations_index: Dict[str, List[str]] = {}

        if dictionary_path and Path(dictionary_path).exists():
            self.load_from_file(dictionary_path)
        else:
            self.load_default_dictionary()

        logger.info(
            "词典引擎初始化完成，已加载 %d 个词条", len(self.dictionary)
        )

    def load_default_dictionary(self) -> None:
        """加载内置高频英语词典（包含不规则动词与常见搭配）。"""
        # 不规则动词
        self.dictionary["go"] = LexicalEntry(
            lemma="go",
            pos="VERB",
            inflections={
                "past": "went",
                "past_participle": "gone",
                "gerund": "going",
                "third_person_singular": "goes",
            },
            irregular=True,
            grammatical_features={"transitive": False},
            common_collocations=["go to", "go with", "go on", "go back"],
            word_family=["goes", "going", "gone", "went"],
            grammar_point_ids=["present_simple", "past_simple", "present_perfect"],
        )

        self.dictionary["come"] = LexicalEntry(
            lemma="come",
            pos="VERB",
            inflections={
                "past": "came",
                "past_participle": "come",
                "gerund": "coming",
                "third_person_singular": "comes",
            },
            irregular=True,
            grammatical_features={"transitive": False},
            common_collocations=["come back", "come across", "come up"],
            word_family=["comes", "coming", "came"],
            grammar_point_ids=["present_simple", "past_simple"],
        )

        self.dictionary["have"] = LexicalEntry(
            lemma="have",
            pos="VERB",
            inflections={
                "past": "had",
                "past_participle": "had",
                "gerund": "having",
                "third_person_singular": "has",
            },
            irregular=True,
            grammatical_features={"transitive": True},
            common_collocations=["have to", "have got", "have breakfast"],
            word_family=["has", "having", "had"],
            grammar_point_ids=[
                "present_perfect",
                "past_perfect",
                "present_continuous",
            ],
        )

        self.dictionary["do"] = LexicalEntry(
            lemma="do",
            pos="VERB",
            inflections={
                "past": "did",
                "past_participle": "done",
                "gerund": "doing",
                "third_person_singular": "does",
            },
            irregular=True,
            grammatical_features={"transitive": True},
            common_collocations=["do homework", "do work", "do business"],
            word_family=["does", "doing", "done", "did"],
            grammar_point_ids=["present_simple", "past_simple", "question_formation"],
        )

        self.dictionary["be"] = LexicalEntry(
            lemma="be",
            pos="VERB",
            inflections={
                "past": "was/were",
                "past_participle": "been",
                "gerund": "being",
                "present_first_person": "am",
                "present_second_person": "are",
                "present_third_person": "is",
            },
            irregular=True,
            grammatical_features={"transitive": False},
            common_collocations=["be happy", "be at", "be about"],
            word_family=["am", "is", "are", "was", "were", "being", "been"],
            grammar_point_ids=[
                "present_simple",
                "past_simple",
                "present_continuous",
                "passive_voice",
            ],
        )

        self.dictionary["make"] = LexicalEntry(
            lemma="make",
            pos="VERB",
            inflections={
                "past": "made",
                "past_participle": "made",
                "gerund": "making",
                "third_person_singular": "makes",
            },
            irregular=True,
            grammatical_features={"transitive": True},
            common_collocations=[
                "make a decision",
                "make progress",
                "make a mistake",
            ],
            word_family=["makes", "making", "made"],
            grammar_point_ids=["present_simple", "past_simple"],
        )

        self.dictionary["decide"] = LexicalEntry(
            lemma="decide",
            pos="VERB",
            inflections={
                "past": "decided",
                "past_participle": "decided",
                "gerund": "deciding",
                "third_person_singular": "decides",
            },
            irregular=False,
            grammatical_features={"transitive": True},
            common_collocations=["decide on", "decide to", "decide against"],
            word_family=["decides", "deciding", "decided", "decision", "indecisive"],
            grammar_point_ids=["present_simple", "past_simple", "present_perfect"],
        )

        self.dictionary["run"] = LexicalEntry(
            lemma="run",
            pos="VERB",
            inflections={
                "past": "ran",
                "past_participle": "run",
                "gerund": "running",
                "third_person_singular": "runs",
            },
            irregular=True,
            grammatical_features={"transitive": False},
            common_collocations=["run away", "run into", "run out"],
            word_family=["runs", "running", "ran"],
            grammar_point_ids=["present_simple", "past_simple"],
        )

        self.dictionary["child"] = LexicalEntry(
            lemma="child",
            pos="NOUN",
            inflections={"plural": "children"},
            irregular=True,
            grammatical_features={"countable": True, "requires_article": True},
            common_collocations=["child development", "child care"],
            word_family=["children", "childhood", "childish"],
            grammar_point_ids=["noun_plural"],
        )

        self.dictionary["person"] = LexicalEntry(
            lemma="person",
            pos="NOUN",
            inflections={"plural": "people"},
            irregular=True,
            grammatical_features={"countable": True, "requires_article": True},
            common_collocations=["person in charge", "elderly person"],
            word_family=["people", "person", "personal", "personality"],
            grammar_point_ids=["noun_plural"],
        )

        # 规则名词示例
        self.dictionary["book"] = LexicalEntry(
            lemma="book",
            pos="NOUN",
            inflections={"plural": "books"},
            irregular=False,
            grammatical_features={"countable": True, "requires_article": True},
            common_collocations=["read a book", "write a book"],
            word_family=["books", "bookshelf", "bookworm"],
            grammar_point_ids=["noun_plural"],
        )

        self.dictionary["school"] = LexicalEntry(
            lemma="school",
            pos="NOUN",
            inflections={"plural": "schools"},
            irregular=False,
            grammatical_features={"countable": True, "requires_article": True},
            common_collocations=["go to school", "at school"],
            word_family=["schools", "schooling", "scholar"],
            grammar_point_ids=["noun_plural"],
        )

        # 形容词示例
        self.dictionary["happy"] = LexicalEntry(
            lemma="happy",
            pos="ADJ",
            inflections={"comparative": "happier", "superlative": "happiest"},
            irregular=False,
            grammatical_features={},
            common_collocations=["be happy", "happy ending"],
            word_family=["happier", "happiest", "happiness", "happily"],
            grammar_point_ids=["adjective_comparative"],
        )

        logger.debug("内置词典加载完成，共 %d 个词条", len(self.dictionary))

    def load_from_file(self, file_path: str) -> None:
        """
        从 JSON 文件加载词典（格式与 load_default_dictionary 一致）。

        Args:
            file_path: 词典文件路径
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for lemma, entry_data in data.items():
                    self.dictionary[lemma] = LexicalEntry(**entry_data)
            logger.info("从文件加载词典成功：%s", file_path)
        except Exception as e:
            logger.error("加载词典文件失败：%s，使用默认词典", e)

    def lookup(self, word: str) -> Optional[LexicalEntry]:
        """
        查找词条（支持大小写不敏感）。

        Args:
            word: 查询词

        Returns:
            LexicalEntry 或 None
        """
        return self.dictionary.get(word.lower())

    def lookup_tokens(self, tokens: List[str]) -> List[Dict]:
        """
        批量查找词条。

        Args:
            tokens: 词列表

        Returns:
            [{"token": str, "entry": Optional[LexicalEntry]}]
        """
        return [
            {
                "token": token,
                "entry": self.lookup(token),
            }
            for token in tokens
        ]

    def get_word_family(self, lemma: str) -> List[str]:
        """
        获取词族（派生词）。

        Args:
            lemma: 词根

        Returns:
            派生词列表
        """
        entry = self.lookup(lemma)
        return entry.word_family if entry else []

    def get_inflection(self, lemma: str, form: str) -> Optional[str]:
        """
        获取特定形式的变化。

        Args:
            lemma: 词根
            form: 形式标签 (e.g., "past", "plural", "comparative")

        Returns:
            变化后的形式或 None
        """
        entry = self.lookup(lemma)
        if entry:
            return entry.inflections.get(form)
        return None

    def is_irregular(self, lemma: str) -> bool:
        """
        判断词是否为不规则变化。

        Args:
            lemma: 词根

        Returns:
            bool
        """
        entry = self.lookup(lemma)
        return entry.irregular if entry else False

    def get_grammatical_features(self, word: str) -> Dict[str, bool]:
        """
        获取词的语法属性。

        Args:
            word: 词

        Returns:
            语法属性字典
        """
        entry = self.lookup(word)
        return entry.grammatical_features if entry else {}

    def get_common_collocations(self, word: str) -> List[str]:
        """
        获取常见搭配。

        Args:
            word: 词

        Returns:
            搭配列表
        """
        entry = self.lookup(word)
        return entry.common_collocations if entry else []

    def get_grammar_point_ids(self, word: str) -> List[str]:
        """
        获取与词关联的语法点 ID。

        Args:
            word: 词

        Returns:
            语法点 ID 列表
        """
        entry = self.lookup(word)
        return entry.grammar_point_ids if entry else []

    def check_collocation(self, verb: str, preposition: str) -> bool:
        """
        检查搭配是否常见（例如 decide on vs. decide to）。

        Args:
            verb: 动词
            preposition: 介词/虚词

        Returns:
            是否为常见搭配
        """
        entry = self.lookup(verb)
        if not entry:
            return True  # 词不在字典中，不进行检查

        collocation = f"{verb} {preposition}"
        return any(
            collocation in col or preposition in col
            for col in entry.common_collocations
        )

    def export_to_json(self, output_path: str) -> None:
        """
        将词典导出为 JSON 文件。

        Args:
            output_path: 输出路径
        """
        output_data = {
            lemma: entry.dict()
            for lemma, entry in self.dictionary.items()
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        logger.info("词典已导出到 %s", output_path)

    def get_stats(self) -> Dict:
        """
        获取词典统计信息。

        Returns:
            统计信息字典
        """
        return {
            "total_entries": len(self.dictionary),
            "irregular_count": sum(
                1 for entry in self.dictionary.values() if entry.irregular
            ),
            "pos_distribution": self._count_pos(),
        }

    def _count_pos(self) -> Dict[str, int]:
        """统计词性分布。"""
        pos_count = {}
        for entry in self.dictionary.values():
            pos_count[entry.pos] = pos_count.get(entry.pos, 0) + 1
        return pos_count


# 全局单例实例
_lexicon_engine: Optional[LexiconEngine] = None


def get_lexicon_engine(
    dictionary_path: Optional[str] = None,
) -> LexiconEngine:
    """
    获取全局词典引擎单例。

    Args:
        dictionary_path: 可选的外部字典文件路径

    Returns:
        LexiconEngine 实例
    """
    global _lexicon_engine
    if _lexicon_engine is None:
        _lexicon_engine = LexiconEngine(dictionary_path)
    return _lexicon_engine
