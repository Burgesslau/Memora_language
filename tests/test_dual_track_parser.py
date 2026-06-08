"""
DualTrackParser 单元测试。

覆盖 Free / Strict 双模式、错误标签与微操练内联返回。
不依赖 spaCy 模型（降级规则引擎仍可检测第三人称单数错误）。
"""

from __future__ import annotations

import pytest

from app.engine.dual_track_parser import DualTrackParser
from app.models.schemas import ErrorSeverity


@pytest.fixture
def parser() -> DualTrackParser:
    """每个测试使用独立解析器实例。"""
    return DualTrackParser()


class TestFreeMode:
    """自由表达模式。"""

    def test_passes_with_valid_sentence(self, parser: DualTrackParser) -> None:
        result = parser.parse_output("I go to school every day", "free")
        assert result.mode == "free"
        assert result.passed is True
        assert result.error_tags == []

    def test_records_silent_errors_without_blocking(self, parser: DualTrackParser) -> None:
        result = parser.parse_output("He go to school", "free")
        assert result.mode == "free"
        # Free Mode：细微错误写入 silent_errors，不一定判定不通过
        assert isinstance(result.silent_errors, list)


class TestStrictMode:
    """严谨应试模式。"""

    def test_fails_third_person_singular(self, parser: DualTrackParser) -> None:
        result = parser.parse_output("He go to school", "strict")
        assert result.mode == "strict"
        assert result.passed is False
        assert len(result.error_tags) >= 1
        primary = result.error_tags[0]
        assert primary.grammar_point == "third_person_singular"
        assert primary.severity in (ErrorSeverity.HIGH, ErrorSeverity.CRITICAL)

    def test_error_tag_has_span(self, parser: DualTrackParser) -> None:
        result = parser.parse_output("He go to school", "strict")
        tag = result.error_tags[0]
        assert tag.span is not None
        assert tag.span.start_char >= 0
        assert tag.span.end_char > tag.span.start_char
        assert tag.span.text

    def test_returns_micro_drills_on_failure(self, parser: DualTrackParser) -> None:
        result = parser.parse_output("He go to school", "strict")
        assert result.passed is False
        assert len(result.micro_drills) >= 1
        drill = result.micro_drills[0]
        assert drill.drill_id
        assert drill.grammar_point == "third_person_singular"

    def test_passes_correct_sentence(self, parser: DualTrackParser) -> None:
        result = parser.parse_output("He goes to school every day", "strict")
        assert result.passed is True
        assert result.error_tags == []
        assert result.micro_drills == []

    def test_detects_chinglish_marry_with(self, parser: DualTrackParser) -> None:
        result = parser.parse_output("I married with her", "strict")
        assert result.passed is False
        assert len(result.error_tags) >= 1
        chinglish = [
            t for t in result.error_tags if t.error_type == "chinglish"
        ]
        assert len(chinglish) >= 1
        assert "marry" in chinglish[0].message.lower() or "及物动词" in chinglish[0].message
        assert chinglish[0].span is not None
        assert "with" in chinglish[0].span.text.lower()


class TestParseOutputShape:
    """统一响应模型结构。"""

    def test_response_fields(self, parser: DualTrackParser) -> None:
        result = parser.parse_output("Hello world", "free")
        assert hasattr(result, "passed")
        assert hasattr(result, "core_structure")
        assert hasattr(result, "feedback")
        assert result.user_text == "Hello world"
