# Smart Grammar System — Debug 审计日志

> **用途**：记录代码审查、Bug 修复与架构变更，供 Agent 与开发者追溯。  
> **版本**：v0.2.4 | **最后更新**：2026-06-08  
> **关联文档**：[SmartGrammar_System_Prompt.md](./SmartGrammar_System_Prompt.md)

---

## 审计摘要（2026-06-08）

| 类别 | 数量 |
|------|------|
| 已修复 | 9 |
| 待处理（Phase 2+） | 1 |
| 文档债务（已清理） | 2 |

---

## 1. 2026-06-08 全项目审查（6 项核心问题）

### 1.1 已修复

| ID | 严重度 | 问题 | 位置 | 修复说明 | 状态 |
|----|--------|------|------|----------|------|
| BUG-002 | P1 | 瓶颈诊断 `failureCounts` Stale Closure，连续失败次数永远慢一拍 | `frontend/src/hooks/useGrammarEvaluation.ts` | `diagnoseMutation` 改用 `useUserStore.getState().failureCounts` 读取即时状态 | ✅ 2026-06-08 |
| BUG-003 | P2 | 答题通过后失败计数不重置，正常用户误触发瓶颈诊断 | `frontend/src/stores/useUserStore.ts` | `recordResult` 在 `passed` 时调用 `resetFailure` | ✅ 2026-06-08 |
| WARN-003 | P2 | Sidebar `/dashboard` 与 `/dashboard/grammar` 双高亮 | `frontend/src/components/layout/sidebar.tsx` | `/dashboard` 改为 `pathname === href` 精确匹配 | ✅ 2026-06-08 |
| DRIFT-004 | P2 | 前端 `passive_voice` 节点在后端内存图缺失 | `app/engine/knowledge_graph.py` | 补齐节点并与 `graph-data.ts` 对齐 | ✅ 2026-06-08 |
| DOC-001 | P2 | `debug_audit_log.md` 缺失，README 引用 404 | `docs/` | 创建本文件 | ✅ 2026-06-08 |
| DOC-002 | P2 | 根目录 README 与 docs 职责倒置 | `README.md`, `docs/` | 长文档移至 `SmartGrammar_System_Prompt.md`，README 精简为快速启动 | ✅ 2026-06-08 |
| WARN-007 | P2 | `LexiconEngine` 使用 Pydantic v1 弃用 API | `app/engine/lexicon.py` | 迁移至 Pydantic v2 `ConfigDict` + `model_dump()` | ✅ 2026-06-08 |
| FEAT-001 | — | 双语词典引擎与中英阻断 | `app/engine/lexicon.py`, `dual_track_parser.py` | `BilingualSense` + `detect_chinglish` 织入 Strict Mode | ✅ 2026-06-08 |

### 1.2 待后续迭代

| ID | 严重度 | 问题 | 位置 | 计划阶段 |
|----|--------|------|------|----------|
| WARN-008 | P2 | Exam 页瓶颈诊断使用 `prompt.grammar_point`，与 API 返回的 `error_tags[0]` 可能不一致 | `frontend/src/app/practice/exam/page.tsx` | Phase 2 前端优化 |

---

## 2. 历史审计（2026-06-07）

| ID | 严重度 | 问题 | 状态 |
|----|--------|------|------|
| BUG-001 | P0 | `dual_track_parser.py` 调用 `self.nlp.nlp()` 导致 API 崩溃 | ✅ 已修复 |
| DRIFT-001 | P1 | 前端 `token_span` vs 后端 `span` 字段不一致 | ✅ 已同步 |
| DRIFT-002 | P1 | 前端缺少 `micro_drills` 类型定义 | ✅ 已同步 |
| DRIFT-003 | P1 | 前端缺少 `getBktStatus()` API 封装 | ✅ 已补充 |
| WARN-001 | P2 | InlineHighlight `<p>` 嵌套 hydration 警告 | ✅ 已修复 |

---

## 3. 已知技术债（Phase 2+）

| ID | 说明 | 计划阶段 |
|----|------|----------|
| WARN-004 | 错题本仅 Zustand 本地持久化，无后端同步 | Phase 2 |
| WARN-005 | 图谱数据前后端静态内存，未统一 API | Phase 2 |
| WARN-006 | spaCy 未安装时降级启发式，生产需 `en_core_web_sm` | 部署规范 |
| — | `logging_utils.py` 存在但未接入 `main.py` | Phase 2 |
| — | `micro_drills` 后端已返回，前端 UI 未展示 | Phase 2 |

---

## 4. 验证命令速查

```bash
# 后端冒烟（解析器）
python -c "from app.engine.dual_track_parser import DualTrackParser; p=DualTrackParser(); print(p.parse_output('He go', 'strict').error_tags[0].span)"

# 后端冒烟（中式英语阻断）
python -c "from app.engine.dual_track_parser import DualTrackParser; p=DualTrackParser(); print(p.parse_output('I married with her', 'strict').error_tags[0].message)"

# 后端单元测试
pytest tests/ -v

# 前端测试 + 构建
cd frontend && npm run test -- --run && npm run build
```

---

*重大 Bug 修复或架构变更须同步更新本文件与 [SmartGrammar_System_Prompt.md](./SmartGrammar_System_Prompt.md) 第 7 节。*
