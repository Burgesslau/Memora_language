"""
双轨制语法解析引擎。

实现 Free Mode（自由表达）与 Strict Mode（严谨应试）两套评价逻辑，
核心基于 NLP 依存分析与规则引擎，不使用大模型进行语法纠错。
"""

from __future__ import annotations

import logging
from typing import Literal

from app.engine.lexicon import LexiconEngine, get_lexicon_engine
from app.models.schemas import (
    CoreStructureResult,
    ErrorSeverity,
    ErrorTag,
    MicroDrill,
    ParseOutputResponse,
    SilentError,
)
from app.utils.nlp_utils import GrammarIssue, NLPUtils, get_nlp_utils

logger = logging.getLogger(__name__)


class DualTrackParser:
    """
    双轨制语法解析器。

    - **Free Mode**：主谓宾核心结构正确且语义通顺即 ``passed=True``，
      细微语法漏洞写入 ``silent_errors``，不打断用户。
    - **Strict Mode**：全量规则语法检查，任何错误均生成 ``error_tags``，
      存在 high/critical 级错误时 ``passed=False``。

    Attributes:
        nlp: NLP 工具实例。
        free_mode_structure_threshold: Free Mode 核心结构最低评分阈值。
    """

    def __init__(
        self,
        nlp_utils: NLPUtils | None = None,
        free_mode_structure_threshold: float = 0.6,
        lexicon: LexiconEngine | None = None,
    ) -> None:
        """
        初始化双轨解析器。

        Args:
            nlp_utils: 可选的 NLPUtils 实例，默认使用全局单例。
            free_mode_structure_threshold: Free Mode 通过所需的最低结构评分。
            lexicon: 可选的 LexiconEngine 实例，默认使用全局单例。
        """
        self.nlp = nlp_utils or get_nlp_utils()
        self.lexicon = lexicon or get_lexicon_engine()
        self.free_mode_structure_threshold = free_mode_structure_threshold

    def parse_output(
        self,
        user_text: str,
        mode: Literal["free", "strict"],
        user_id: str | None = None,
    ) -> ParseOutputResponse:
        """
        对用户输出执行双轨制语法解析。

        Args:
            user_text: 用户输入文本（通常为语音转写结果）。
            mode: 评价模式，``"free"`` 或 ``"strict"``。
            user_id: 可选用户 ID，供后续学习记录关联（当前骨架仅日志记录）。

        Returns:
            ParseOutputResponse 统一响应模型。
        """
        if user_id:
            logger.debug("解析用户输出 user_id=%s mode=%s", user_id, mode)

        cleaned_text = user_text.strip()
        structure = self.nlp.analyze_core_structure(cleaned_text)
        core_result = self._to_core_structure_result(structure)
        issues = self.nlp.detect_grammar_issues(cleaned_text)

        # 新增：词典查询以增强错误检测精度
        doc = self.nlp.parse(cleaned_text)
        tokens = (
            [token.lemma_ for token in doc]
            if doc is not None
            else cleaned_text.lower().split()
        )
        lexical_info = self.lexicon.lookup_tokens(tokens)

        if mode == "free":
            return self._parse_free_mode(
                cleaned_text, core_result, issues, lexical_info
            )
        return self._parse_strict_mode(
            cleaned_text, core_result, issues, lexical_info
        )

    def _parse_free_mode(
        self,
        user_text: str,
        core_result: CoreStructureResult,
        issues: list[GrammarIssue],
        lexical_info: list[dict] | None = None,
    ) -> ParseOutputResponse:
        """
        自由表达模式解析。

        通过条件：核心结构评分 >= 阈值 且语义通顺。
        所有检测到的语法问题均转为 silent_errors。
        
        Args:
            user_text: 用户输入文本
            core_result: 核心结构分析结果
            issues: 检测到的语法问题列表
            lexical_info: 词典信息列表（可选）
        """
        passed = (
            core_result.structure_score >= self.free_mode_structure_threshold
            and core_result.is_semantically_fluent
            and core_result.has_subject
            and core_result.has_verb
        )

        silent_errors = [
            SilentError(
                grammar_point=issue.grammar_point,
                error_type=issue.error_type,
                message=issue.message,
                confidence=issue.confidence,
            )
            for issue in issues
        ]

        if passed:
            feedback = "表达很棒！继续保持开口说英语的信心。"
            if silent_errors:
                feedback += "（系统已静默记录可改进细节，不影响本次通过。）"
            # 如果有词典信息，可添加小贴士
            if lexical_info:
                feedback = self._enhance_free_mode_feedback(
                    feedback, silent_errors, lexical_info
                )
        else:
            feedback = (
                "再试一次：确保句子有清晰的主语和谓语，意思表达完整即可。"
            )

        return ParseOutputResponse(
            passed=passed,
            mode="free",
            user_text=user_text,
            core_structure=core_result,
            silent_errors=silent_errors,
            error_tags=[],
            feedback=feedback,
        )

    def _parse_strict_mode(
        self,
        user_text: str,
        core_result: CoreStructureResult,
        issues: list[GrammarIssue],
        lexical_info: list[dict] | None = None,
    ) -> ParseOutputResponse:
        """
        严谨应试模式解析。

        全语法检查：所有问题生成 error_tags。
        存在 high 或 critical 级错误，或核心结构不完整时判定不通过。
        
        Args:
            user_text: 用户输入文本
            core_result: 核心结构分析结果
            issues: 检测到的语法问题列表
            lexical_info: 词典信息列表（可选），用于增强错误检测
        """
        error_tags = [self._issue_to_error_tag(issue) for issue in issues]
        micro_drills = []

        # 核心结构缺失也作为错误标签
        if not core_result.has_subject:
            error_tags.append(
                ErrorTag(
                    grammar_point="sentence_structure",
                    message="缺少主语",
                    severity=ErrorSeverity.HIGH,
                    star_level=1,
                    error_type="structure",
                )
            )
        if not core_result.has_verb:
            error_tags.append(
                ErrorTag(
                    grammar_point="sentence_structure",
                    message="缺少谓语动词",
                    severity=ErrorSeverity.HIGH,
                    star_level=1,
                    error_type="structure",
                )
            )

        blocking_severities = {ErrorSeverity.HIGH, ErrorSeverity.CRITICAL}
        has_blocking_error = any(tag.severity in blocking_severities for tag in error_tags)
        passed = not has_blocking_error and core_result.is_semantically_fluent

        # 出错时内联微操练：从第一条错误的语法点取微操练
        if not passed and error_tags:
            primary_error = error_tags[0]
            from app.engine.knowledge_graph import KnowledgeGraph
            kg = KnowledgeGraph()
            drill_data = kg.get_micro_drills(primary_error.grammar_point, limit=1)
            micro_drills = [
                MicroDrill(**drill) for drill in drill_data
            ] if drill_data else []

        if passed:
            feedback = "语法正确，做得很好！"
        elif error_tags:
            primary = error_tags[0]
            feedback = (
                f"发现 {len(error_tags)} 处语法问题。"
                f"首要问题：{primary.message}"
            )
            # 使用词典信息增强反馈
            if lexical_info:
                feedback = self._enhance_strict_mode_feedback(
                    feedback, primary, lexical_info, user_text
                )
        else:
            feedback = "请检查句子结构是否完整。"

        return ParseOutputResponse(
            passed=passed,
            mode="strict",
            user_text=user_text,
            core_structure=core_result,
            silent_errors=[],
            error_tags=error_tags,
            feedback=feedback,
            micro_drills=micro_drills,
        )

    @staticmethod
    def _to_core_structure_result(structure: object) -> CoreStructureResult:
        """将内部 StructureAnalysis 转为 Pydantic 模型。"""
        return CoreStructureResult(
            has_subject=structure.has_subject,
            has_verb=structure.has_verb,
            has_object=structure.has_object,
            is_semantically_fluent=structure.is_semantically_fluent,
            structure_score=structure.structure_score,
        )

    def _enhance_free_mode_feedback(
        self,
        base_feedback: str,
        silent_errors: list[SilentError],
        lexical_info: list[dict],
    ) -> str:
        """
        使用词典信息增强 Free Mode 的反馈。

        Args:
            base_feedback: 基础反馈字符串
            silent_errors: 静默错误列表
            lexical_info: 词典信息列表

        Returns:
            增强后的反馈字符串
        """
        if not silent_errors or not lexical_info:
            return base_feedback

        # 查找词典条目，提供小贴士
        tips = []
        for error in silent_errors:
            # 尝试找到相关的词和其搭配
            for lex in lexical_info:
                if lex.get("entry") and "decide" in error.grammar_point.lower():
                    entry = lex["entry"]
                    if entry.common_collocations:
                        tip = (
                            f"💡 小贴士：{entry.lemma} "
                            f"常接 {', '.join(entry.common_collocations[:2])}"
                        )
                        tips.append(tip)
                        break

        if tips:
            return base_feedback + "\n" + "\n".join(tips)
        return base_feedback

    def _enhance_strict_mode_feedback(
        self,
        base_feedback: str,
        primary_error: ErrorTag,
        lexical_info: list[dict],
        user_text: str,
    ) -> str:
        """
        使用词典信息增强 Strict Mode 的反馈。

        Args:
            base_feedback: 基础反馈字符串
            primary_error: 主要错误标签
            lexical_info: 词典信息列表
            user_text: 用户输入的文本

        Returns:
            增强后的反馈字符串
        """
        enhancement = ""

        # 如果是时态相关错误，查找相关动词的形态变化
        if "tense" in primary_error.error_type.lower():
            for lex in lexical_info:
                if lex.get("entry"):
                    entry = lex["entry"]
                    if entry.irregular and entry.inflections:
                        lemma = entry.lemma
                        forms = entry.inflections
                        enhancement = (
                            f"\n📚 解析：{lemma} 是不规则动词。\n"
                            f"其形式有：" + ", ".join(
                                [f"{k}: {v}" for k, v in list(forms.items())[:3]]
                            )
                        )
                        break

        # 如果是搭配相关错误，提供常见搭配建议
        elif "collocation" in primary_error.error_type.lower():
            for lex in lexical_info:
                if lex.get("entry") and lex["entry"].common_collocations:
                    entry = lex["entry"]
                    collocations = entry.common_collocations
                    enhancement = (
                        f"\n📚 常见搭配：{entry.lemma} 后常接 "
                        f"{', '.join(collocations[:2])}"
                    )
                    break

        return base_feedback + enhancement if enhancement else base_feedback

    @staticmethod
    def _issue_to_error_tag(issue: GrammarIssue) -> ErrorTag:
        """将内部 GrammarIssue 转为 ErrorTag 响应模型。"""
        from app.models.schemas import TokenSpan
        
        severity_map = {
            "low": ErrorSeverity.LOW,
            "medium": ErrorSeverity.MEDIUM,
            "high": ErrorSeverity.HIGH,
            "critical": ErrorSeverity.CRITICAL,
        }
        
        span = None
        if issue.char_span:
            span = TokenSpan(
                start_char=issue.char_span[0],
                end_char=issue.char_span[1],
                text=issue.error_text or "",
                token_index=issue.token_index,
            )
        
        return ErrorTag(
            grammar_point=issue.grammar_point,
            message=issue.message,
            severity=severity_map.get(issue.severity, ErrorSeverity.MEDIUM),
            star_level=issue.star_level,
            error_type=issue.error_type,
            span=span,
            suggestion=issue.suggestion,
        )


# ---------------------------------------------------------------------------
# 代码检查清单
# ---------------------------------------------------------------------------
# [x] DualTrackParser 类已实现
# [x] parse_output(user_text, mode, user_id) 方法已实现
# [x] Free Mode: 核心结构正确 -> passed=True, silent_errors 记录细节
# [x] Strict Mode: 全语法检查 -> error_tags 含 grammar_point, severity, star_level
# [x] 返回格式统一使用 ParseOutputResponse Pydantic 模型
# [x] 完整类型提示、中文注释与 Google-style docstring
