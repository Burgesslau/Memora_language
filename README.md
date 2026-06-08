# Smart Grammar System

输出驱动型自适应英语语法学习系统 — 围绕用户真实表达进行语法诊断、追踪与路径导航。

> **Agent / 开发者**：完整架构、API 契约与实施约束请参阅  
> [docs/SmartGrammar_System_Prompt.md](./docs/SmartGrammar_System_Prompt.md)  
> Bug 与变更记录见 [docs/debug_audit_log.md](./docs/debug_audit_log.md)

---

## 项目结构

```
Memora_language/
├── app/                    # FastAPI 后端（引擎 / 服务 / 模型）
├── frontend/               # Next.js 15 前端
├── docs/                   # 系统设计文档与审计日志
├── tests/                  # 后端 pytest 单元测试
└── requirements.txt        # Python 依赖
```

---

## 快速启动

### 1. 后端

```powershell
cd "e:\1_Code Project\3_self_project\Memora_language"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| 端点 | 地址 |
|------|------|
| 健康检查 | http://localhost:8000/health |
| API 文档 | http://localhost:8000/docs |
| 语音评价 | POST `/api/v1/speak` |
| 瓶颈诊断 | POST `/api/v1/diagnose` |

### 2. 前端

```powershell
cd frontend
npm install
npm run dev
```

默认地址：http://localhost:3000

开发环境 API 代理（`frontend/next.config.ts`）：

- `/api/v1/:path*` → `http://localhost:8000/api/v1/:path*`
- `/health` → `http://localhost:8000/health`

### 3. 全栈联调

```powershell
# 终端 A — 后端
uvicorn app.main:app --reload --port 8000

# 终端 B — 前端
cd frontend && npm run dev
```

---

## 测试

```powershell
# 后端
pytest tests/ -v

# 前端
cd frontend
npm run test -- --run
npm run build
```

---

## 前端页面

| 路由 | 说明 |
|------|------|
| `/dashboard` | 学习仪表盘 |
| `/dashboard/grammar` | 语法仪表盘 |
| `/practice/free` | 自由表达练习 |
| `/practice/exam` | 严谨应试练习 |
| `/practice/talk` | 口语练兵场 |
| `/graph` | 知识图谱 |
| `/notebook` | 错题本 |
| `/settings` | 设置 |

---

## 关键文件

| 文件 | 职责 |
|------|------|
| `app/models/schemas.py` | 后端 Pydantic 请求/响应模型 |
| `app/engine/dual_track_parser.py` | 双轨制语法解析引擎 |
| `app/engine/knowledge_graph.py` | 知识图谱（内存降级 / Neo4j） |
| `frontend/src/types/api.ts` | 与后端同步的 TypeScript 类型 |
| `frontend/src/services/api.ts` | 前端 API 统一入口 |
| `frontend/src/services/graph-data.ts` | 图谱静态数据（与后端内存图对齐） |

---

## 当前阶段

**Phase 1 ✅** — 双轨解析、瓶颈诊断、前端骨架、Debug 审计  
**Phase 2 ⏳** — PostgreSQL / Neo4j 持久化、BKT 落盘、图谱 API 统一

版本：**v0.2.3** | 更新：**2026-06-08**
