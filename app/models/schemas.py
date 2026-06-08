"""
Pydantic 数据模型定义模块。

本模块集中定义 Smart Grammar System 所有 API 请求/响应及引擎内部
传递的数据结构，确保类型安全与序列化一致性。
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 枚举类型
# ---------------------------------------------------------------------------


class EvaluationMode(str, Enum):
    """双轨制评价模式枚举。"""

    FREE = "free"
    STRICT = "strict"


class ErrorSeverity(str, Enum):
    """语法错误严重等级。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# 语法错误与解析结果
# ---------------------------------------------------------------------------


class TokenSpan(BaseModel):
    """
    错误位置的精确定位（同时支持字符与Token维度）。

    用于前端精确渲染高亮与 Popover，避免复杂的二次计算。

    Attributes:
        start_char: 错误开始的字符绝对位置（0-indexed）。
        end_char: 错误结束的字符绝对位置（0-indexed，不含此位置）。
        text: 错误词/短语的原始文本（用于验证）。
        token_index: Token 序列号（spaCy 中的索引），用于 NLP 后续处理。
    """

    start_char: int = Field(..., ge=0, description="错误开始字符位置")
    end_char: int = Field(..., ge=0, description="错误结束字符位置")
    text: str = Field(..., description="错误词/短语文本")
    token_index: int | None = Field(default=None, ge=0, description="Token 序列号（可选）")


class ErrorTag(BaseModel):
    """
    严谨模式下的语法错误标签。

    Attributes:
        grammar_point: 语法点标识，如 ``present_perfect_continuous``。
        message: 面向用户的错误描述。
        severity: 错误严重等级。
        star_level: 难度星级，1-5 星。
        error_type: 题型分类，如 ``tense``、``article``、``subject_verb_agreement``。
        span: 错误位置的精确定位（字符 + Token 双维）。
        suggestion: 修正建议，可选。
    """

    grammar_point: str = Field(..., description="语法点标识")
    message: str = Field(..., description="错误描述")
    severity: ErrorSeverity = Field(..., description="严重等级")
    star_level: int = Field(..., ge=1, le=5, description="难度星级 1-5")
    error_type: str = Field(..., description="题型分类标签")
    span: TokenSpan | None = Field(
        default=None, description="错误位置的精确定位"
    )
    suggestion: str | None = Field(default=None, description="修正建议")


class SilentError(BaseModel):
    """
    自由模式下静默记录的细微语法漏洞。

    不打断用户表达，仅供后台知识追踪与复习调度使用。

    Attributes:
        grammar_point: 语法点标识。
        error_type: 错误类型标签。
        message: 内部记录用描述。
        confidence: 检测置信度，0.0-1.0。
    """

    grammar_point: str
    error_type: str
    message: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class CoreStructureResult(BaseModel):
    """主谓宾核心结构分析结果。"""

    has_subject: bool = Field(..., description="是否检测到主语")
    has_verb: bool = Field(..., description="是否检测到谓语")
    has_object: bool = Field(default=False, description="是否检测到宾语（及物结构）")
    is_semantically_fluent: bool = Field(..., description="语义是否通顺")
    structure_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="核心结构完整度评分"
    )


class ParseOutputResponse(BaseModel):
    """
    DualTrackParser 统一返回模型。

    Attributes:
        passed: 当前模式下是否判定通过。
        mode: 评价模式。
        user_text: 用户原始输入。
        core_structure: 核心结构分析详情。
        silent_errors: 自由模式下静默记录的错误列表。
        error_tags: 严谨模式下的高亮错误标签列表。
        feedback: 面向用户的简要反馈文案。
        micro_drills: 微操练题目（用户在 Strict Mode 犯错时内联返回）。
    """

    passed: bool
    mode: Literal["free", "strict"]
    user_text: str
    core_structure: CoreStructureResult
    silent_errors: list[SilentError] = Field(default_factory=list)
    error_tags: list[ErrorTag] = Field(default_factory=list)
    feedback: str = ""
    micro_drills: list[MicroDrill] = Field(
        default_factory=list, description="内联微操练（Strict Mode 错误时返回）"
    )


# ---------------------------------------------------------------------------
# API 请求 / 响应
# ---------------------------------------------------------------------------


class SpeakRequest(BaseModel):
    """``POST /api/v1/speak`` 请求体。"""

    user_text: str = Field(
        ...,
        min_length=1,
        description="用户语音转文字后的句子",
        examples=["I go to school", "He go to school yesterday"],
    )
    mode: Literal["free", "strict"] = Field(
        default="free",
        description="评价模式：free 或 strict",
        examples=["free", "strict"],
    )
    user_id: str | None = Field(
        default=None,
        description="用户 ID，用于学习记录关联",
        examples=["user_001"],
    )


class SpeakResponse(BaseModel):
    """``POST /api/v1/speak`` 响应体。"""

    success: bool = True
    data: ParseOutputResponse


class DiagnoseRequest(BaseModel):
    """``POST /api/v1/diagnose`` 请求体。"""

    user_id: str = Field(..., description="用户 ID")
    grammar_point: str = Field(..., description="当前卡住的语法点标识")
    consecutive_failures: int = Field(
        default=0, ge=0, description="该语法点连续失败次数"
    )


class PrerequisiteNode(BaseModel):
    """知识图谱中的前置依赖节点。"""

    node_id: str
    label: str
    description: str
    depth: int = Field(..., ge=0, description="距目标节点的逆向追溯深度")


class MicroDrill(BaseModel):
    """
    微操练题目（内联返回）。

    用于当用户犯错或触发瓶颈时，前端无需额外请求即可立即展示。

    Attributes:
        drill_id: 题目唯一标识。
        grammar_point: 关联的语法点。
        question: 题目文本（可含占位符 {blank}）。
        example_sentence: 完整例句。
        correct_answer: 正确答案或填空。
        options: 多选题选项（如适用）。
        explanation: 中英双语解释。
        difficulty: 难度等级 1-5。
    """

    drill_id: str = Field(..., description="微操练唯一 ID")
    grammar_point: str = Field(..., description="关联的语法点")
    question: str = Field(..., description="题目描述")
    example_sentence: str = Field(..., description="完整例句")
    correct_answer: str = Field(..., description="正确答案")
    options: list[str] = Field(default_factory=list, description="多选题选项")
    explanation: str = Field(..., description="解释文本（支持 HTML）")
    difficulty: int = Field(default=2, ge=1, le=5, description="难度 1-5")


class BottleneckDiagnosis(BaseModel):
    """瓶颈逆向诊断结果。"""

    is_bottleneck: bool = Field(..., description="是否触发瓶颈诊断")
    grammar_point: str
    consecutive_failures: int
    failure_threshold: int
    prerequisite_nodes: list[PrerequisiteNode] = Field(default_factory=list)
    recommendation: str = ""
    micro_drill_ids: list[str] = Field(
        default_factory=list, description="推荐的前置微操练 ID 列表"
    )
    micro_drills: list[MicroDrill] = Field(
        default_factory=list, description="内联微操练题目（无需额外请求）"
    )


class DiagnoseResponse(BaseModel):
    """``POST /api/v1/diagnose`` 响应体。"""

    success: bool = True
    data: BottleneckDiagnosis


# ---------------------------------------------------------------------------
# 代码检查清单
# ---------------------------------------------------------------------------
# [x] 定义 EvaluationMode / ErrorSeverity 枚举
# [x] ErrorTag 含 grammar_point, severity, star_level, error_type
# [x] SilentError 用于自由模式静默记录
# [x] ParseOutputResponse 作为 DualTrackParser 统一返回模型
# [x] Speak / Diagnose 请求响应模型完整
# [x] 全部字段含类型提示与 Field 约束
