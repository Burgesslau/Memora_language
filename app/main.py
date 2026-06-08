"""
Smart Grammar System — FastAPI 应用入口。

提供口语评价与瓶颈诊断 REST API。
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    DiagnoseRequest,
    DiagnoseResponse,
    SpeakRequest,
    SpeakResponse,
)
from app.services.admin_service import BKTMatrixResponse, get_bkt_status
from app.services.learning_service import LearningService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    应用生命周期管理。

    启动时初始化学习服务单例，关闭时释放资源。
    """
    app.state.learning_service = LearningService()
    logger.info("Smart Grammar System 已启动")
    yield
    logger.info("Smart Grammar System 已关闭")


app = FastAPI(
    title="Smart Grammar System",
    description="输出驱动型自适应英语语法学习系统 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_learning_service() -> LearningService:
    """从应用状态获取学习服务实例。"""
    return app.state.learning_service


@app.get("/health", tags=["系统"])
async def health_check() -> dict[str, str]:
    """健康检查端点。"""
    return {"status": "ok", "service": "smart-grammar-system"}


@app.post(
    "/api/v1/speak",
    response_model=SpeakResponse,
    tags=["Evaluation Engine (双轨解析)"],
    summary="双轨制口语语法评价",
    description="对用户语音转写或文字输入执行实时双轨制语法评价。\n\n"
    "- **free 模式**：保护开口自信，核心结构正确即通过，细微错误静默记录\n"
    "- **strict 模式**：高精度语法检查，所有错误高亮并标注星级与题型",
)
async def speak(request: SpeakRequest) -> SpeakResponse:
    """
    对用户语音转写文本进行双轨制语法评价。

    **Free Mode**
    - 通过条件：主谓宾核心结构正确 + 语义通顺
    - 处理：细微错误写入 silent_errors，不打断用户
    - 适用：日常口语练习、自信建立

    **Strict Mode**
    - 检查范围：时态、冠词、介词、第三人称单数等全量规则
    - 每条错误含 grammar_point、star_level、error_type 与修正建议
    - 通过条件：无 high/critical 级错误 + 语义通顺
    - 适用：应试训练、写作纠错

    **Request Example (Free Mode)**
    ```json
    {
      "user_text": "I go to school every day",
      "mode": "free",
      "user_id": "user_001"
    }
    ```

    **Request Example (Strict Mode)**
    ```json
    {
      "user_text": "He go to school yesterday",
      "mode": "strict",
      "user_id": "user_001"
    }
    ```

    **Response (Free Mode - Passed)**
    ```json
    {
      "success": true,
      "data": {
        "passed": true,
        "mode": "free",
        "user_text": "I go to school every day",
        "core_structure": {
          "has_subject": true,
          "has_verb": true,
          "has_object": false,
          "is_semantically_fluent": true,
          "structure_score": 0.8
        },
        "silent_errors": [],
        "error_tags": [],
        "feedback": "表达很棒！继续保持开口说英语的信心。",
        "micro_drills": []
      }
    }
    ```

    **Response (Strict Mode - Failed)**
    ```json
    {
      "success": true,
      "data": {
        "passed": false,
        "mode": "strict",
        "user_text": "He go to school yesterday",
        "core_structure": {
          "has_subject": true,
          "has_verb": true,
          "has_object": false,
          "is_semantically_fluent": true,
          "structure_score": 0.8
        },
        "silent_errors": [],
        "error_tags": [
          {
            "grammar_point": "third_person_singular",
            "message": "第三人称单数主语后动词需加 -s",
            "severity": "high",
            "star_level": 2,
            "error_type": "subject_verb_agreement",
            "span": {
              "start_char": 3,
              "end_char": 5,
              "text": "go",
              "token_index": 1
            },
            "suggestion": "goes"
          }
        ],
        "feedback": "发现 1 处语法问题。首要问题：第三人称单数主语后动词需加 -s",
        "micro_drills": [
          {
            "drill_id": "drill_third_person_singular_01",
            "grammar_point": "third_person_singular",
            "question": "填空：He ___ to school every day.",
            "example_sentence": "He goes to school every day.",
            "correct_answer": "goes",
            "options": ["go", "goes", "going", "gone"],
            "explanation": "当主语是第三人称单数（he, she, it）时，一般现在时的动词要加 -s 或 -es。",
            "difficulty": 2
          }
        ]
      }
    }
    ```
    """
    if not request.user_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_text 不能为空",
        )

    service = _get_learning_service()
    result = await service.evaluate_speech(
        user_text=request.user_text,
        mode=request.mode,
        user_id=request.user_id,
    )
    return SpeakResponse(data=result)


@app.post(
    "/api/v1/diagnose",
    response_model=DiagnoseResponse,
    tags=["Diagnostic & Navigation (瓶颈导航)"],
    summary="语法瓶颈逆向诊断",
    description="检查用户是否在指定语法点陷入瓶颈。\n\n"
    "当连续失败次数达到阈值（默认 3 次）时，通过知识图谱逆向追溯前置依赖，"
    "返回针对性的复习路径与微操练题目（无需前端额外请求）。",
)
async def diagnose(request: DiagnoseRequest) -> DiagnoseResponse:
    """
    执行语法瓶颈逆向诊断。

    **工作流程**
    1. 判断连续失败次数是否达到阈值（默认 3 次）
    2. 如达到阈值，通过知识图谱逆向追溯前置依赖
    3. 返回推荐的复习路径与对应的微操练题目

    **Request Example**
    ```json
    {
      "user_id": "user_001",
      "grammar_point": "present_perfect_continuous",
      "consecutive_failures": 3
    }
    ```

    **Response (Bottleneck Triggered)**
    ```json
    {
      "success": true,
      "data": {
        "is_bottleneck": true,
        "grammar_point": "present_perfect_continuous",
        "consecutive_failures": 3,
        "failure_threshold": 3,
        "prerequisite_nodes": [
          {
            "node_id": "present_perfect",
            "label": "现在完成时",
            "description": "have/has + 过去分词",
            "depth": 1
          },
          {
            "node_id": "present_continuous",
            "label": "现在进行时",
            "description": "be + V-ing 结构",
            "depth": 1
          },
          {
            "node_id": "auxiliary_have_be",
            "label": "助动词 have/be",
            "description": "助动词 have 与 be 的基本用法",
            "depth": 2
          }
        ],
        "recommendation": "你在「现在完成进行时」已连续 3 次以上出错，可能存在前置知识薄弱。建议先巩固：现在完成时、现在进行时，完成 2 组前置微操练后，再返回本语法点。",
        "micro_drill_ids": [
          "drill_present_perfect_01",
          "drill_present_continuous_01"
        ],
        "micro_drills": [
          {
            "drill_id": "drill_present_perfect_01",
            "grammar_point": "present_perfect",
            "question": "现在完成时题：I ___ my homework.",
            "example_sentence": "I have finished my homework.",
            "correct_answer": "have finished",
            "options": ["finish", "have finished", "finished", "am finishing"],
            "explanation": "现在完成时用 have/has + 过去分词表示过去发生但对现在有影响的动作。",
            "difficulty": 2
          }
        ]
      }
    }
    ```

    **Response (No Bottleneck)**
    ```json
    {
      "success": true,
      "data": {
        "is_bottleneck": false,
        "grammar_point": "present_perfect_continuous",
        "consecutive_failures": 1,
        "failure_threshold": 3,
        "prerequisite_nodes": [],
        "recommendation": "继续当前语法点练习，尚未触发瓶颈诊断。",
        "micro_drill_ids": [],
        "micro_drills": []
      }
    }
    ```
    """
    service = _get_learning_service()
    diagnosis = await service.diagnose_bottleneck(
        user_id=request.user_id,
        grammar_point=request.grammar_point,
        consecutive_failures=request.consecutive_failures,
    )
    return DiagnoseResponse(data=diagnosis)


@app.get(
    "/api/v1/admin/bkt-status/{user_id}",
    response_model=BKTMatrixResponse,
    tags=["Admin (管理后台)"],
    summary="用户 BKT 掌握度矩阵",
    description="查看指定用户对所有语法点的掌握概率矩阵。\n\n"
    "用于系统调试和学习效果分析。（仅限开发环境，生产环境需鉴权）",
)
async def get_user_bkt_status(user_id: str) -> BKTMatrixResponse:
    """
    获取用户的 Bayesian Knowledge Tracing 掌握度矩阵。

    **功能**
    - 显示用户对每个语法点的掌握概率 P(L)
    - 识别掌握度 < 0.5 的瓶颈语法点
    - 计算整体掌握度平均值

    **Response Example**
    ```json
    {
      "user_id": "user_001",
      "timestamp": "2026-06-08T00:27:49.918+08:00",
      "mastery_matrix": [
        {
          "user_id": "user_001",
          "grammar_point": "present_simple",
          "mastery_probability": 0.85,
          "guess_probability": 0.0,
          "slip_probability": 0.1,
          "learn_probability": 0.1,
          "attempts": 8,
          "last_attempt_at": null
        }
      ],
      "overall_mastery": 0.67,
      "bottleneck_points": [
        "third_person_singular",
        "indefinite_article"
      ]
    }
    ```

    Args:
        user_id: 用户唯一标识。

    Returns:
        BKTMatrixResponse 包含掌握度矩阵与瓶颈分析。

    Note:
        当前为骨架实现，Phase 2/3 将接入真实 BKT 算法与 PostgreSQL。
    """
    return await get_bkt_status(user_id)


# ---------------------------------------------------------------------------
# 代码检查清单
# ---------------------------------------------------------------------------
# [x] FastAPI 应用入口已创建
# [x] POST /api/v1/speak 路由已实现
# [x] POST /api/v1/diagnose 路由已实现
# [x] 使用 Pydantic 请求/响应模型
# [x] lifespan 管理 LearningService 单例
# [x] /health 健康检查端点
