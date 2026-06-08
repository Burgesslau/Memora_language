"""
LexiconEngine 单元测试。

覆盖词条查询、形态变化、搭配检查与批量 lookup。
"""

from __future__ import annotations

import pytest

from app.engine.lexicon import LexiconEngine, LexicalEntry, get_lexicon_engine


@pytest.fixture
def lexicon() -> LexiconEngine:
    """独立词典引擎（内置默认词典）。"""
    return LexiconEngine()


class TestLookup:
    """词条查询。"""

    def test_lookup_irregular_verb_go(self, lexicon: LexiconEngine) -> None:
        entry = lexicon.lookup("go")
        assert entry is not None
        assert entry.lemma == "go"
        assert entry.irregular is True
        assert entry.inflections["past"] == "went"
        assert entry.inflections["past_participle"] == "gone"

    def test_lookup_case_insensitive(self, lexicon: LexiconEngine) -> None:
        assert lexicon.lookup("GO") is not None
        assert lexicon.lookup("Go") is not None

    def test_lookup_unknown_returns_none(self, lexicon: LexiconEngine) -> None:
        assert lexicon.lookup("xyznonexistent") is None

    def test_lookup_tokens_batch(self, lexicon: LexiconEngine) -> None:
        results = lexicon.lookup_tokens(["he", "go", "school"])
        assert len(results) == 3
        go_entry = next(r for r in results if r["token"] == "go")
        assert go_entry["entry"] is not None
        assert isinstance(go_entry["entry"], LexicalEntry)


class TestInflectionAndFamily:
    """形态变化与词族。"""

    def test_get_inflection_past(self, lexicon: LexiconEngine) -> None:
        assert lexicon.get_inflection("go", "past") == "went"

    def test_get_inflection_missing_form(self, lexicon: LexiconEngine) -> None:
        assert lexicon.get_inflection("go", "future") is None

    def test_is_irregular(self, lexicon: LexiconEngine) -> None:
        assert lexicon.is_irregular("go") is True
        assert lexicon.is_irregular("decide") is False

    def test_get_word_family(self, lexicon: LexiconEngine) -> None:
        family = lexicon.get_word_family("decide")
        assert "decision" in family


class TestCollocationAndFeatures:
    """搭配与语法属性。"""

    def test_common_collocations(self, lexicon: LexiconEngine) -> None:
        collocations = lexicon.get_common_collocations("make")
        assert "make a decision" in collocations

    def test_check_collocation_valid(self, lexicon: LexiconEngine) -> None:
        assert lexicon.check_collocation("decide", "on") is True

    def test_grammatical_features_countable_noun(self, lexicon: LexiconEngine) -> None:
        features = lexicon.get_grammatical_features("child")
        assert features.get("countable") is True

    def test_get_stats(self, lexicon: LexiconEngine) -> None:
        stats = lexicon.get_stats()
        assert stats["total_entries"] >= 10
        assert stats["irregular_count"] >= 1


class TestChinglishDetection:
    """中式英语阻断。"""

    def test_detect_marry_with(self, lexicon: LexiconEngine) -> None:
        matches = lexicon.detect_chinglish("I married with her")
        assert len(matches) >= 1
        assert matches[0].lemma == "marry"
        assert "with" in matches[0].matched_text.lower()

    def test_detect_marry_with_no_false_positive(self, lexicon: LexiconEngine) -> None:
        matches = lexicon.detect_chinglish("He married her yesterday.")
        assert matches == []


class TestBilingualLookup:
    """双语词形反查。"""

    def test_lookup_token_form_inflected(self, lexicon: LexiconEngine) -> None:
        entry = lexicon.lookup_token_form("married")
        assert entry is not None
        assert entry.lemma == "marry"

    def test_marry_has_bilingual_sense(self, lexicon: LexiconEngine) -> None:
        entry = lexicon.lookup("marry")
        assert entry is not None
        assert len(entry.senses) >= 1
        assert entry.senses[0].chinese_definition == "和…结婚"


class TestSingleton:
    """全局单例工厂。"""

    def test_get_lexicon_engine_returns_instance(self) -> None:
        engine = get_lexicon_engine()
        assert isinstance(engine, LexiconEngine)
        assert engine.lookup("be") is not None
