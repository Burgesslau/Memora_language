"""
双语词典与形态学引擎（Bilingual Lexicon & Morphology Engine）。

为语法解析提供词形变化、双语多义项、中英搭配映射与中式英语直译阻断，
提升 Strict Mode 的确定性检测精度。禁止 LLM 判定。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class BilingualSense(BaseModel):
    """双语词条义项模型。"""

    model_config = ConfigDict(from_attributes=True)

    sense_id: str
    chinese_definition: str
    english_definition: str
    valid_structures: List[str] = Field(default_factory=list)
    forbidden_translations: Dict[str, str] = Field(default_factory=dict)
    example_pair: Dict[str, str] = Field(default_factory=dict)


class LexicalEntry(BaseModel):
    """完整的双语形态学词条。"""

    model_config = ConfigDict(from_attributes=True)

    lemma: str
    pos: str
    inflections: Dict[str, str] = Field(default_factory=dict)
    irregular: bool = False
    grammatical_features: Dict[str, bool] = Field(default_factory=dict)
    common_collocations: List[str] = Field(default_factory=list)
    word_family: List[str] = Field(default_factory=list)
    grammar_point_ids: List[str] = Field(default_factory=list)
    senses: List[BilingualSense] = Field(default_factory=list)


@dataclass
class ChinglishMatch:
    """中式英语阻断匹配结果（内部数据结构）。"""

    lemma: str
    sense_id: str
    matched_text: str
    char_span: tuple[int, int]
    message: str
    chinese_definition: str
    suggestion: str
    forbidden_pattern: str


class LexiconEngine:
    """
    双语词典与形态学引擎。

    管理词条库、词形反查、搭配检索与中式英语阻断。
    现阶段内存预埋高频易错词，Phase 2 可持久化至 PostgreSQL。
    """

    def __init__(self, dictionary_path: Optional[str] = None) -> None:
        """
        初始化词典引擎。

        Args:
            dictionary_path: 可选外部 JSON 词典路径。
        """
        self.dictionary: Dict[str, LexicalEntry] = {}
        self.collocations_index: Dict[str, List[str]] = {}

        if dictionary_path and Path(dictionary_path).exists():
            self.load_from_file(dictionary_path)
        else:
            self.dictionary = self._load_bilingual_data()

        logger.info("词典引擎初始化完成，已加载 %d 个词条", len(self.dictionary))

    def _load_bilingual_data(self) -> Dict[str, LexicalEntry]:
        """加载内置双语词典（含形态学与中英阻断规则）。"""
        entries: Dict[str, LexicalEntry] = {}

        entries["marry"] = LexicalEntry(
            lemma="marry",
            pos="VERB",
            irregular=False,
            inflections={
                "past": "married",
                "past_participle": "married",
                "gerund": "marrying",
                "third_person_singular": "marries",
            },
            grammatical_features={"transitive": True},
            common_collocations=["marry sb", "get married to sb"],
            word_family=["marry", "marriage", "married", "marries"],
            grammar_point_ids=["verb_collocation", "transitive_verb"],
            senses=[
                BilingualSense(
                    sense_id="marry_v_1",
                    chinese_definition="和…结婚",
                    english_definition=(
                        "To become the legally accepted partner of someone."
                    ),
                    valid_structures=["marry sb", "get married to sb"],
                    forbidden_translations={
                        "marry with": (
                            "marry 是及物动词，后面直接加人，不能加 with"
                        ),
                    },
                    example_pair={
                        "en": "He married her.",
                        "zh": "他娶了她。",
                    },
                ),
            ],
        )

        entries["decide"] = LexicalEntry(
            lemma="decide",
            pos="VERB",
            irregular=False,
            inflections={
                "past": "decided",
                "past_participle": "decided",
                "gerund": "deciding",
                "third_person_singular": "decides",
            },
            grammatical_features={"transitive": True},
            common_collocations=["decide on", "decide to", "decide against"],
            word_family=["decides", "deciding", "decided", "decision", "indecisive"],
            grammar_point_ids=["verb_collocation", "present_simple", "past_simple"],
            senses=[
                BilingualSense(
                    sense_id="decide_v_1",
                    chinese_definition="决定",
                    english_definition="To make a choice about something.",
                    valid_structures=["decide on sth", "decide to do sth"],
                    forbidden_translations={
                        "decide sth without on": (
                            "decide 后接 on/upon/to，不能直接接宾语"
                        ),
                    },
                    example_pair={
                        "en": "We decided on the date.",
                        "zh": "我们决定了日期。",
                    },
                ),
            ],
        )

        entries["go"] = LexicalEntry(
            lemma="go",
            pos="VERB",
            irregular=True,
            inflections={
                "past": "went",
                "past_participle": "gone",
                "gerund": "going",
                "third_person_singular": "goes",
            },
            grammatical_features={"transitive": False},
            common_collocations=["go to", "go with", "go on", "go back"],
            word_family=["goes", "going", "gone", "went"],
            grammar_point_ids=["present_simple", "past_simple", "present_perfect"],
        )

        entries["come"] = LexicalEntry(
            lemma="come",
            pos="VERB",
            irregular=True,
            inflections={
                "past": "came",
                "past_participle": "come",
                "gerund": "coming",
                "third_person_singular": "comes",
            },
            grammatical_features={"transitive": False},
            common_collocations=["come back", "come across", "come up"],
            word_family=["comes", "coming", "came"],
            grammar_point_ids=["present_simple", "past_simple"],
        )

        entries["have"] = LexicalEntry(
            lemma="have",
            pos="VERB",
            irregular=True,
            inflections={
                "past": "had",
                "past_participle": "had",
                "gerund": "having",
                "third_person_singular": "has",
            },
            grammatical_features={"transitive": True},
            common_collocations=["have to", "have got", "have breakfast"],
            word_family=["has", "having", "had"],
            grammar_point_ids=[
                "present_perfect",
                "past_perfect",
                "present_continuous",
            ],
            senses=[
                BilingualSense(
                    sense_id="have_v_perfect",
                    chinese_definition="有；完成体助动词",
                    english_definition="Auxiliary for perfect tenses.",
                    valid_structures=["have + past participle"],
                    forbidden_translations={
                        "have went": "完成时用 have + 过去分词，不能用 went",
                        "have went to": "完成时用 have gone，不能用 went",
                    },
                    example_pair={
                        "en": "I have gone to school.",
                        "zh": "我已经去学校了。",
                    },
                ),
            ],
        )

        entries["do"] = LexicalEntry(
            lemma="do",
            pos="VERB",
            irregular=True,
            inflections={
                "past": "did",
                "past_participle": "done",
                "gerund": "doing",
                "third_person_singular": "does",
            },
            grammatical_features={"transitive": True},
            common_collocations=["do homework", "do work", "do business"],
            word_family=["does", "doing", "done", "did"],
            grammar_point_ids=["present_simple", "past_simple", "question_formation"],
        )

        entries["be"] = LexicalEntry(
            lemma="be",
            pos="VERB",
            irregular=True,
            inflections={
                "past": "was/were",
                "past_participle": "been",
                "gerund": "being",
                "present_first_person": "am",
                "present_second_person": "are",
                "present_third_person": "is",
            },
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

        entries["make"] = LexicalEntry(
            lemma="make",
            pos="VERB",
            irregular=True,
            inflections={
                "past": "made",
                "past_participle": "made",
                "gerund": "making",
                "third_person_singular": "makes",
            },
            grammatical_features={"transitive": True},
            common_collocations=[
                "make a decision",
                "make progress",
                "make a mistake",
            ],
            word_family=["makes", "making", "made"],
            grammar_point_ids=["present_simple", "past_simple"],
            senses=[
                BilingualSense(
                    sense_id="make_v_collocation",
                    chinese_definition="做；使",
                    english_definition="To create or cause.",
                    valid_structures=["make a decision", "make progress"],
                    forbidden_translations={
                        "do a decision": "decision 与 make 搭配，不能说 do a decision",
                        "do decision": "decision 与 make 搭配，不能说 do decision",
                    },
                    example_pair={
                        "en": "make a decision",
                        "zh": "做决定",
                    },
                ),
            ],
        )

        entries["run"] = LexicalEntry(
            lemma="run",
            pos="VERB",
            irregular=True,
            inflections={
                "past": "ran",
                "past_participle": "run",
                "gerund": "running",
                "third_person_singular": "runs",
            },
            grammatical_features={"transitive": False},
            common_collocations=["run away", "run into", "run out"],
            word_family=["runs", "running", "ran"],
            grammar_point_ids=["present_simple", "past_simple"],
        )

        entries["child"] = LexicalEntry(
            lemma="child",
            pos="NOUN",
            irregular=True,
            inflections={"plural": "children"},
            grammatical_features={"countable": True, "requires_article": True},
            common_collocations=["child development", "child care"],
            word_family=["children", "childhood", "childish"],
            grammar_point_ids=["noun_plural"],
        )

        entries["person"] = LexicalEntry(
            lemma="person",
            pos="NOUN",
            irregular=True,
            inflections={"plural": "people"},
            grammatical_features={"countable": True, "requires_article": True},
            common_collocations=["person in charge", "elderly person"],
            word_family=["people", "person", "personal", "personality"],
            grammar_point_ids=["noun_plural"],
        )

        entries["book"] = LexicalEntry(
            lemma="book",
            pos="NOUN",
            irregular=False,
            inflections={"plural": "books"},
            grammatical_features={"countable": True, "requires_article": True},
            common_collocations=["read a book", "write a book"],
            word_family=["books", "bookshelf", "bookworm"],
            grammar_point_ids=["noun_plural"],
        )

        entries["school"] = LexicalEntry(
            lemma="school",
            pos="NOUN",
            irregular=False,
            inflections={"plural": "schools"},
            grammatical_features={"countable": True, "requires_article": True},
            common_collocations=["go to school", "at school"],
            word_family=["schools", "schooling", "scholar"],
            grammar_point_ids=["noun_plural"],
        )

        entries["happy"] = LexicalEntry(
            lemma="happy",
            pos="ADJ",
            irregular=False,
            inflections={"comparative": "happier", "superlative": "happiest"},
            common_collocations=["be happy", "happy ending"],
            word_family=["happier", "happiest", "happiness", "happily"],
            grammar_point_ids=["adjective_comparative"],
        )

        return entries

    def load_from_file(self, file_path: str) -> None:
        """从 JSON 文件加载词典。"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for lemma, entry_data in data.items():
                    self.dictionary[lemma] = LexicalEntry(**entry_data)
            logger.info("从文件加载词典成功：%s", file_path)
        except Exception as exc:
            logger.error("加载词典文件失败：%s，使用内置词典", exc)
            self.dictionary = self._load_bilingual_data()

    def lookup(self, word: str) -> Optional[LexicalEntry]:
        """按词根查找词条（大小写不敏感）。"""
        return self.dictionary.get(word.lower())

    def lookup_token_form(self, text: str) -> Optional[LexicalEntry]:
        """
        逆向词形反查词条（如 ``married`` → ``marry``）。

        Args:
            text: 词形或词根。

        Returns:
            LexicalEntry 或 ``None``。
        """
        text_lower = text.lower()
        direct = self.lookup(text_lower)
        if direct is not None:
            return direct

        for entry in self.dictionary.values():
            if text_lower in {v.lower() for v in entry.inflections.values()}:
                return entry
            if text_lower in {w.lower() for w in entry.word_family}:
                return entry
        return None

    def lookup_tokens(self, tokens: List[str]) -> List[Dict]:
        """批量查找词条。"""
        return [
            {"token": token, "entry": self.lookup_token_form(token)}
            for token in tokens
        ]

    def detect_chinglish(self, text: str) -> List[ChinglishMatch]:
        """
        扫描文本中的中式英语直译模式（确定性子串匹配）。

        Args:
            text: 用户输入句子。

        Returns:
            匹配到的 ChinglishMatch 列表（去重）。
        """
        lowered = text.lower()
        matches: List[ChinglishMatch] = []
        seen_spans: set[tuple[int, int]] = set()

        for entry in self.dictionary.values():
            for sense in entry.senses:
                for pattern, tip in sense.forbidden_translations.items():
                    for variant in self._expand_forbidden_pattern(entry, pattern):
                        idx = lowered.find(variant)
                        if idx == -1:
                            continue
                        span = (idx, idx + len(variant))
                        if span in seen_spans:
                            continue
                        seen_spans.add(span)
                        matched_text = text[idx : idx + len(variant)]
                        valid_hint = (
                            sense.valid_structures[0]
                            if sense.valid_structures
                            else ""
                        )
                        message = (
                            f"中式英语搭配错误：{tip}。"
                            f"【{sense.chinese_definition}】"
                            f"正确用法：{valid_hint or '请参考标准结构'}"
                        )
                        matches.append(
                            ChinglishMatch(
                                lemma=entry.lemma,
                                sense_id=sense.sense_id,
                                matched_text=matched_text,
                                char_span=span,
                                message=message,
                                chinese_definition=sense.chinese_definition,
                                suggestion=valid_hint,
                                forbidden_pattern=pattern,
                            )
                        )

        matches.sort(key=lambda m: m.char_span[0])
        return matches

    @staticmethod
    def _expand_forbidden_pattern(
        entry: LexicalEntry, pattern: str
    ) -> List[str]:
        """将禁止模式扩展为含词形变体的匹配串列表。"""
        pattern_lower = pattern.lower()
        variants = {pattern_lower}
        lemma = entry.lemma.lower()

        inflected_forms = {lemma}
        for form in entry.inflections.values():
            for part in form.lower().split("/"):
                inflected_forms.add(part.strip())

        for form in inflected_forms:
            if lemma in pattern_lower:
                variants.add(pattern_lower.replace(lemma, form))
            first_word = pattern_lower.split()[0] if pattern_lower.split() else ""
            if first_word and first_word == lemma:
                rest = pattern_lower[len(first_word) :]
                variants.add(form + rest)

        return sorted(variants, key=len, reverse=True)

    def get_word_family(self, lemma: str) -> List[str]:
        """获取词族。"""
        entry = self.lookup(lemma)
        return entry.word_family if entry else []

    def get_inflection(self, lemma: str, form: str) -> Optional[str]:
        """获取特定形态变化。"""
        entry = self.lookup(lemma)
        if entry:
            return entry.inflections.get(form)
        return None

    def is_irregular(self, lemma: str) -> bool:
        """判断是否不规则变化。"""
        entry = self.lookup(lemma)
        return entry.irregular if entry else False

    def get_grammatical_features(self, word: str) -> Dict[str, bool]:
        """获取语法属性。"""
        entry = self.lookup_token_form(word)
        return entry.grammatical_features if entry else {}

    def get_common_collocations(self, word: str) -> List[str]:
        """获取常见搭配。"""
        entry = self.lookup_token_form(word)
        return entry.common_collocations if entry else []

    def get_grammar_point_ids(self, word: str) -> List[str]:
        """获取关联语法点 ID。"""
        entry = self.lookup_token_form(word)
        return entry.grammar_point_ids if entry else []

    def check_collocation(self, verb: str, preposition: str) -> bool:
        """检查动词+介词是否为常见搭配。"""
        entry = self.lookup_token_form(verb)
        if not entry:
            return True

        collocation = f"{entry.lemma} {preposition}"
        return any(
            collocation in col or preposition in col
            for col in entry.common_collocations
        )

    def export_to_json(self, output_path: str) -> None:
        """将词典导出为 JSON 文件。"""
        output_data = {
            lemma: entry.model_dump()
            for lemma, entry in self.dictionary.items()
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        logger.info("词典已导出到 %s", output_path)

    def get_stats(self) -> Dict:
        """获取词典统计信息。"""
        return {
            "total_entries": len(self.dictionary),
            "irregular_count": sum(
                1 for entry in self.dictionary.values() if entry.irregular
            ),
            "bilingual_senses": sum(
                len(entry.senses) for entry in self.dictionary.values()
            ),
            "pos_distribution": self._count_pos(),
        }

    def _count_pos(self) -> Dict[str, int]:
        """统计词性分布。"""
        pos_count: Dict[str, int] = {}
        for entry in self.dictionary.values():
            pos_count[entry.pos] = pos_count.get(entry.pos, 0) + 1
        return pos_count


_lexicon_engine: Optional[LexiconEngine] = None


def get_lexicon_engine(
    dictionary_path: Optional[str] = None,
) -> LexiconEngine:
    """获取全局词典引擎单例。"""
    global _lexicon_engine
    if _lexicon_engine is None:
        _lexicon_engine = LexiconEngine(dictionary_path)
    return _lexicon_engine


# ---------------------------------------------------------------------------
# 代码检查清单
# ---------------------------------------------------------------------------
# [x] BilingualSense / LexicalEntry Pydantic v2 模型
# [x] 双语多义项与中英搭配映射
# [x] 中式英语 forbidden_translations 阻断（detect_chinglish）
# [x] lookup_token_form 词形反查
# [x] model_dump 替代 dict()，消除 Pydantic v1 弃用警告
# [x] 禁止 LLM 判定
