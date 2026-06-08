/**
 * 知识图谱静态数据（Phase 2 前使用内存数据，与后端 KnowledgeGraph 对齐）
 */

import type { GraphEdgeData, GraphNodeData } from "@/types/api";

export const GRAPH_NODES: GraphNodeData[] = [
  { id: "present_simple", label: "一般现在时", description: "主语 + 动词原形/第三人称单数", mastery_score: 85, node_type: "grammar" },
  { id: "past_simple", label: "一般过去时", description: "主语 + 动词过去式", mastery_score: 72, node_type: "grammar" },
  { id: "third_person_singular", label: "第三人称单数", description: "he/she/it 后动词加 -s", mastery_score: 55, node_type: "grammar" },
  { id: "auxiliary_have_be", label: "助动词 have/be", description: "助动词 have 与 be 的基本用法", mastery_score: 48, node_type: "concept" },
  { id: "present_continuous", label: "现在进行时", description: "be + V-ing 结构", mastery_score: 62, node_type: "grammar" },
  { id: "present_perfect", label: "现在完成时", description: "have/has + 过去分词", mastery_score: 38, node_type: "grammar" },
  { id: "past_participle", label: "过去分词", description: "规则/不规则动词过去分词形式", mastery_score: 45, node_type: "concept" },
  { id: "present_perfect_continuous", label: "现在完成进行时", description: "have/has been + V-ing", mastery_score: 28, node_type: "grammar" },
  { id: "indefinite_article", label: "不定冠词 a/an", description: "可数名词单数前的 a/an 选择", mastery_score: 78, node_type: "grammar" },
  { id: "passive_voice", label: "被动语态", description: "be + 过去分词", mastery_score: 52, node_type: "grammar" },
];

export const GRAPH_EDGES: GraphEdgeData[] = [
  { id: "e1", source: "present_simple", target: "past_simple", edge_type: "prerequisite" },
  { id: "e2", source: "present_simple", target: "third_person_singular", edge_type: "prerequisite" },
  { id: "e3", source: "present_simple", target: "auxiliary_have_be", edge_type: "prerequisite" },
  { id: "e4", source: "auxiliary_have_be", target: "present_continuous", edge_type: "prerequisite" },
  { id: "e5", source: "auxiliary_have_be", target: "present_perfect", edge_type: "prerequisite" },
  { id: "e6", source: "past_simple", target: "past_participle", edge_type: "prerequisite" },
  { id: "e7", source: "past_participle", target: "present_perfect", edge_type: "prerequisite" },
  { id: "e8", source: "present_perfect", target: "present_perfect_continuous", edge_type: "prerequisite" },
  { id: "e9", source: "present_continuous", target: "present_perfect_continuous", edge_type: "prerequisite" },
  { id: "e10", source: "present_simple", target: "passive_voice", edge_type: "related" },
  { id: "e11", source: "third_person_singular", target: "present_perfect_continuous", edge_type: "weakness" },
];

export function getNodeById(id: string): GraphNodeData | undefined {
  return GRAPH_NODES.find((n) => n.id === id);
}
