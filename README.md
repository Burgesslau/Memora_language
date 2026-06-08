# Smart Grammar System

输出驱动型自适应英语语法学习系统。

## 项目结构

- `app/` - FastAPI 后端入口与引擎模块
- `frontend/` - Next.js 15 前端应用
- `docs/` - 项目设计与系统文档
- `requirements.txt` - 后端 Python 依赖

## 快速启动

### 1. 后端

```powershell
cd "e:\1_Code Project\3_self_project\Memora_language_2026_6_7"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动后：

- 健康检查：`http://localhost:8000/health`
- 语音评价：`http://localhost:8000/api/v1/speak`
- 瓶颈诊断：`http://localhost:8000/api/v1/diagnose`

### 2. 前端

```powershell
cd frontend
npm install
npm run dev
```

默认端口：`http://localhost:3000`

前端通过 `frontend/next.config.ts` 将以下路径代理到后端：

- `/api/v1/:path*` → `http://localhost:8000/api/v1/:path*`
- `/health` → `http://localhost:8000/health`

## 后端 API 规范

### POST /api/v1/speak

请求体：

```json
{
  "user_text": "I have been studying English.",
  "mode": "strict",
  "user_id": "user_001"
}
```

响应体：

```json
{
  "success": true,
  "data": {
    "passed": true,
    "mode": "strict",
    "user_text": "I have been studying English.",
    "core_structure": {
      "has_subject": true,
      "has_verb": true,
      "has_object": false,
      "is_semantically_fluent": true,
      "structure_score": 0.92
    },
    "silent_errors": [],
    "error_tags": [],
    "feedback": "Great job!"
  }
}
```

### POST /api/v1/diagnose

请求体：

```json
{
  "user_id": "user_001",
  "grammar_point": "present_perfect_continuous",
  "consecutive_failures": 3
}
```

响应体：

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
        "description": "现在完成时的基础用法",
        "depth": 1
      }
    ],
    "recommendation": "先复习现在完成时，再过渡到现在完成进行时。",
    "micro_drill_ids": ["drill_101"]
  }
}
```

### GET /health

响应体：

```json
{
  "status": "ok",
  "service": "smart-grammar-system"
}
```

## 前端关键页面

- `/dashboard` - 学习仪表盘
- `/dashboard/grammar` - 语法仪表盘
- `/practice/free` - 自由表达练习
- `/practice/exam` - 严谨应试练习
- `/practice/talk` - 口语练兵场
- `/graph` - 知识图谱
- `/notebook` - 错题本
- `/settings` - 设置

## 测试

前端测试：

```powershell
cd frontend
npm run test
```

## 说明

- `app/models/schemas.py` 定义后端请求/响应模型
- `frontend/src/services/api.ts` 封装前端与后端通信
- `frontend/next.config.ts` 负责开发环境 API 代理
