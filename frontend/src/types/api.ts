/** 与后端 app/models/schemas.py 对齐的 TypeScript 类型 */

export type EvaluationMode = "free" | "strict";
export type ErrorSeverity = "low" | "medium" | "high" | "critical";

/** 错误位置精确定位（字符 + Token 双维） */
export interface TokenSpan {
  start_char: number;
  end_char: number;
  text: string;
  token_index: number | null;
}

export interface ErrorTag {
  grammar_point: string;
  message: string;
  severity: ErrorSeverity;
  star_level: number;
  error_type: string;
  /** 后端标准字段 */
  span: TokenSpan | null;
  /** @deprecated 旧版兼容字段，优先使用 span */
  token_span?: [number, number] | null;
  suggestion: string | null;
}

export interface SilentError {
  grammar_point: string;
  error_type: string;
  message: string;
  confidence: number;
}

export interface CoreStructureResult {
  has_subject: boolean;
  has_verb: boolean;
  has_object: boolean;
  is_semantically_fluent: boolean;
  structure_score: number;
}

export interface MicroDrill {
  drill_id: string;
  grammar_point: string;
  question: string;
  example_sentence: string;
  correct_answer: string;
  options: string[];
  explanation: string;
  difficulty: number;
}

export interface ParseOutputResponse {
  passed: boolean;
  mode: EvaluationMode;
  user_text: string;
  core_structure: CoreStructureResult;
  silent_errors: SilentError[];
  error_tags: ErrorTag[];
  feedback: string;
  micro_drills: MicroDrill[];
}

export interface SpeakRequest {
  user_text: string;
  mode: EvaluationMode;
  user_id?: string | null;
}

export interface SpeakResponse {
  success: boolean;
  data: ParseOutputResponse;
}

export interface DiagnoseRequest {
  user_id: string;
  grammar_point: string;
  consecutive_failures: number;
}

export interface PrerequisiteNode {
  node_id: string;
  label: string;
  description: string;
  depth: number;
}

export interface BottleneckDiagnosis {
  is_bottleneck: boolean;
  grammar_point: string;
  consecutive_failures: number;
  failure_threshold: number;
  prerequisite_nodes: PrerequisiteNode[];
  recommendation: string;
  micro_drill_ids: string[];
  micro_drills: MicroDrill[];
}

export interface DiagnoseResponse {
  success: boolean;
  data: BottleneckDiagnosis;
}

export interface HealthResponse {
  status: string;
  service: string;
}

export interface BKTStatus {
  user_id: string;
  grammar_point: string;
  mastery_probability: number;
  guess_probability: number;
  slip_probability: number;
  learn_probability: number;
  attempts: number;
  last_attempt_at: string | null;
}

export interface BKTMatrixResponse {
  user_id: string;
  timestamp: string;
  mastery_matrix: BKTStatus[];
  overall_mastery: number;
  bottleneck_points: string[];
}

/** 前端本地扩展：图谱节点 */
export interface GraphNodeData extends Record<string, unknown> {
  id: string;
  label: string;
  description: string;
  mastery_score: number;
  node_type: "grammar" | "concept";
}

export interface GraphEdgeData {
  id: string;
  source: string;
  target: string;
  edge_type: "prerequisite" | "related" | "weakness";
}

/** 前端本地扩展：错题记录 */
export interface ErrorNotebookItem {
  id: string;
  grammar_point: string;
  label: string;
  error_type: string;
  message: string;
  mode: EvaluationMode;
  occurred_at: string;
  count: number;
}
