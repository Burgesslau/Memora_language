"use client";

import { Header } from "@/components/layout/header";
import { KnowledgeGraphView } from "@/components/graph/knowledge-graph-view";

export default function GraphPage() {
  return (
    <>
      <Header
        title="知识图谱"
        subtitle="我为什么卡住？我下一步学什么？"
      />
      <div className="flex-1 p-6">
        <KnowledgeGraphView />
      </div>
    </>
  );
}
