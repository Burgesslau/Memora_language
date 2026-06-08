"""
NLP 工具模块。

基于 spaCy 提供句法依赖分析、核心结构检测与规则化语法检查。
禁止使用大模型进行语法纠错，所有判断均来自符号规则与依存分析。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# spaCy 模型名称，可通过环境变量覆盖
DEFAULT_SPACY_MODEL = "en_core_web_sm"


@dataclass
class GrammarIssue:
    """规则引擎检测到的单条语法问题（内部数据结构）。"""

    grammar_point: str
    error_type: str
    message: str
    severity: str  # low | medium | high | critical
    star_level: int
    char_span: tuple[int, int] | None = None  # (start_char, end_char)
    token_index: int | None = None  # Token 序列号
    error_text: str | None = None  # 错误词/短语的实际文本
    suggestion: str | None = None
    confidence: float = 0.85


@dataclass
class StructureAnalysis:
    """句法核心结构分析结果（内部数据结构）。"""

    has_subject: bool = False
    has_verb: bool = False
    has_object: bool = False
    is_semantically_fluent: bool = True
    structure_score: float = 0.0
    root_verb: str | None = None
    subject_text: str | None = None


class NLPUtils:
    """
    基于 spaCy 的 NLP 工具类。

    封装模型加载、依存分析、核心结构判定与规则化语法检查。
    若 spaCy 模型未安装，将降级为基于正则的轻量检测（仅用于开发骨架）。
    """

    def __init__(self, model_name: str = DEFAULT_SPACY_MODEL) -> None:
        """
        初始化 NLP 工具。

        Args:
            model_name: spaCy 英文模型名称，如 ``en_core_web_sm``。
        """
        self._model_name = model_name
        self._nlp: Any | None = None
        self._load_model()

    def _load_model(self) -> None:
        """尝试加载 spaCy 模型，失败时记录警告并启用降级模式。"""
        try:
            import spacy

            self._nlp = spacy.load(self._model_name)
            logger.info("spaCy 模型已加载: %s", self._model_name)
        except (ImportError, OSError) as exc:
            logger.warning(
                "spaCy 模型加载失败 (%s)，将使用降级规则检测。请执行: "
                "python -m spacy download %s",
                exc,
                self._model_name,
            )
            self._nlp = None

    def parse(self, text: str) -> Any | None:
        """
        对文本执行 spaCy 依存分析。

        Args:
            text: 待分析英文句子。

        Returns:
            spaCy Doc 对象；降级模式下返回 ``None``。
        """
        if self._nlp is None:
            return None
        return self._nlp(text.strip())

    def analyze_core_structure(self, text: str) -> StructureAnalysis:
        """
        分析句子主谓宾核心结构及语义通顺性。

        Free Mode 通过判定的核心依据：
        - 存在主语（nsubj / nsubjpass）
        - 存在谓语动词（ROOT 为 VERB / AUX）
        - 语义通顺（非空、非纯符号、长度合理）

        Args:
            text: 用户输入句子。

        Returns:
            StructureAnalysis 结构分析结果。
        """
        cleaned = text.strip()
        result = StructureAnalysis()

        if not cleaned or len(cleaned) < 2:
            result.is_semantically_fluent = False
            return result

        # 降级模式：简单启发式
        if self._nlp is None:
            return self._analyze_core_structure_fallback(cleaned)

        doc = self._nlp(cleaned)
        has_subj = False
        has_verb = False
        has_obj = False
        root_verb: str | None = None
        subject_text: str | None = None

        for token in doc:
            if token.dep_ in ("nsubj", "nsubjpass", "csubj"):
                has_subj = True
                subject_text = token.text
            if token.dep_ == "ROOT" and token.pos_ in ("VERB", "AUX"):
                has_verb = True
                root_verb = token.lemma_
            if token.dep_ in ("dobj", "pobj", "attr", "oprd"):
                has_obj = True

        # 祈使句等无主语但 ROOT 为动词的情况
        if not has_subj and has_verb:
            has_subj = True  # 祈使句视为主语省略，结构仍完整

        result.has_subject = has_subj
        result.has_verb = has_verb
        result.has_object = has_obj
        result.root_verb = root_verb
        result.subject_text = subject_text
        result.is_semantically_fluent = self._check_fluency(doc)
        result.structure_score = self._compute_structure_score(result)
        return result

    def _analyze_core_structure_fallback(self, text: str) -> StructureAnalysis:
        """spaCy 不可用时的降级核心结构检测。"""
        result = StructureAnalysis()
        words = text.split()
        if len(words) < 2:
            result.is_semantically_fluent = len(words) == 1 and words[0].isalpha()
            return result

        # 粗略判断：首词可能是主语，含常见动词形式
        common_verbs = re.compile(
            r"\b(am|is|are|was|were|have|has|had|do|does|did|"
            r"will|would|can|could|go|goes|went|eat|eats|ate|"
            r"like|likes|liked|want|wants|wanted|be|been|being)\b",
            re.IGNORECASE,
        )
        result.has_subject = words[0][0].isalpha()
        result.has_verb = bool(common_verbs.search(text))
        result.has_object = len(words) >= 3
        result.is_semantically_fluent = True
        result.structure_score = (
            0.4 * result.has_subject
            + 0.4 * result.has_verb
            + 0.2 * result.has_object
        )
        return result

    def _check_fluency(self, doc: Any) -> bool:
        """基于 spaCy Doc 判断语义是否基本通顺。"""
        if len(doc) < 1:
            return False
        alpha_ratio = sum(1 for t in doc if t.is_alpha) / max(len(doc), 1)
        return alpha_ratio >= 0.5

    def _compute_structure_score(self, analysis: StructureAnalysis) -> float:
        """计算核心结构完整度评分。"""
        score = 0.0
        if analysis.has_subject:
            score += 0.4
        if analysis.has_verb:
            score += 0.4
        if analysis.has_object:
            score += 0.2
        return min(score, 1.0)

    def detect_grammar_issues(self, text: str) -> list[GrammarIssue]:
        """
        基于规则引擎检测语法问题（Strict Mode 及 Free Mode 静默记录共用）。

        检测项包括但不限于：
        - 第三人称单数（he/she/it + 动词原形）
        - 冠词缺失（可数名单数前无 a/an/the）
        - 常见时态不一致（简化规则）

        Args:
            text: 用户输入句子。

        Returns:
            检测到的语法问题列表。
        """
        issues: list[GrammarIssue] = []

        if self._nlp is not None:
            issues.extend(self._detect_issues_spacy(text))
        issues.extend(self._detect_issues_regex(text))

        # 去重：同一 grammar_point + error_type 只保留一条
        seen: set[tuple[str, str]] = set()
        unique: list[GrammarIssue] = []
        for issue in issues:
            key = (issue.grammar_point, issue.error_type)
            if key not in seen:
                seen.add(key)
                unique.append(issue)
        return unique

    def _detect_issues_spacy(self, text: str) -> list[GrammarIssue]:
        """基于 spaCy 依存与词性的规则检测。"""
        issues: list[GrammarIssue] = []
        doc = self._nlp(text)
        if doc is None:
            return issues

        for token in doc:
            # 第三人称单数：he/she/it 后主语链 + 动词原形（非第三人称形式）
            if token.dep_ == "nsubj" and token.text.lower() in ("he", "she", "it"):
                for child in token.head.children:
                    if child.dep_ == "aux" and child.tag_ == "VB":
                        issues.append(
                            GrammarIssue(
                                grammar_point="third_person_singular",
                                error_type="subject_verb_agreement",
                                message=f"第三人称单数主语 '{token.text}' 后的助动词应使用 does/is",
                                severity="high",
                                star_level=2,
                                char_span=(child.idx, child.idx + len(child.text)),
                                token_index=child.i,
                                error_text=child.text,
                                suggestion=f"Consider: {token.text} doesn't / {token.text} isn't",
                            )
                        )
        return issues

    def _detect_issues_regex(self, text: str) -> list[GrammarIssue]:
        """基于正则表达式的补充规则检测。"""
        issues: list[GrammarIssue] = []

        # he/she/it + 动词原形（无 s）
        pattern_3sg = re.compile(
            r"\b(He|She|It)\s+(go|eat|like|want|have|do|play|run|work)\b",
            re.IGNORECASE,
        )
        match = pattern_3sg.search(text)
        if match:
            issues.append(
                GrammarIssue(
                    grammar_point="third_person_singular",
                    error_type="subject_verb_agreement",
                    message="第三人称单数主语后动词需加 -s",
                    severity="high",
                    star_level=2,
                    char_span=(match.start(2), match.end(2)),
                    error_text=match.group(2),
                    suggestion=match.group(2) + "s",
                )
            )

        # 可数单数名词前缺冠词（极简启发式）
        pattern_article = re.compile(
            r"\b(I have|I want|I need|I bought)\s+([a-z]+)\b", re.IGNORECASE
        )
        for m in pattern_article.finditer(text):
            noun = m.group(2).lower()
            if noun not in ("a", "an", "the", "some", "many") and noun.endswith(
                ("ion", "ment", "ness", "ity")
            ):
                issues.append(
                    GrammarIssue(
                        grammar_point="indefinite_article",
                        error_type="article",
                        message=f"可数名词 '{m.group(2)}' 前可能缺少冠词 a/an",
                        severity="medium",
                        star_level=1,
                        char_span=(m.start(2), m.end(2)),
                        error_text=m.group(2),
                        suggestion=f"a {m.group(2)}",
                        confidence=0.7,
                    )
                )

        return issues


@lru_cache(maxsize=1)
def get_nlp_utils(model_name: str = DEFAULT_SPACY_MODEL) -> NLPUtils:
    """
    获取 NLPUtils 单例（按模型名缓存）。

    Args:
        model_name: spaCy 模型名称。

    Returns:
        NLPUtils 实例。
    """
    return NLPUtils(model_name=model_name)


# ---------------------------------------------------------------------------
# 代码检查清单
# ---------------------------------------------------------------------------
# [x] 基于 spaCy 的依存分析封装，含降级模式
# [x] analyze_core_structure 检测主谓宾核心结构
# [x] detect_grammar_issues 规则化语法检测（禁止 LLM）
# [x] GrammarIssue / StructureAnalysis 内部数据结构
# [x] get_nlp_utils 单例工厂
# [x] 完整类型提示与 Google-style docstring
