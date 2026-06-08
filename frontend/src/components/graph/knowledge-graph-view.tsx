"use client";

import { useCallback, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "@dagrejs/dagre";
import { GrammarNode } from "./grammar-node";
import { DetailPanel } from "./detail-panel";
import { GRAPH_NODES, GRAPH_EDGES } from "@/services/graph-data";
import type { GraphNodeData } from "@/types/api";
import { useGrammarEvaluation } from "@/hooks/useGrammarEvaluation";

const nodeTypes = { grammar: GrammarNode };

function layoutElements(nodes: Node[], edges: Edge[]) {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: "TB", nodesep: 60, ranksep: 80 });

  nodes.forEach((n) => g.setNode(n.id, { width: 80, height: 80 }));
  edges.forEach((e) => g.setEdge(e.source, e.target));

  dagre.layout(g);

  return nodes.map((n) => {
    const pos = g.node(n.id);
    return { ...n, position: { x: pos.x - 40, y: pos.y - 40 } };
  });
}

/** 知识图谱主视图 */
export function KnowledgeGraphView() {
  const [selectedNode, setSelectedNode] = useState<GraphNodeData | null>(null);
  const { diagnoseMutation } = useGrammarEvaluation();

  const initialNodes: Node[] = useMemo(
    () =>
      layoutElements(
        GRAPH_NODES.map((n) => ({
          id: n.id,
          type: "grammar",
          data: n,
          position: { x: 0, y: 0 },
        })),
        GRAPH_EDGES.map((e) => ({
          id: e.id,
          source: e.source,
          target: e.target,
        })),
      ),
    [],
  );

  const initialEdges: Edge[] = useMemo(
    () =>
      GRAPH_EDGES.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        animated: e.edge_type === "weakness",
        style: {
          stroke:
            e.edge_type === "weakness"
              ? "hsl(var(--error))"
              : e.edge_type === "related"
                ? "hsl(var(--muted))"
                : "hsl(var(--accent))",
          strokeDasharray: e.edge_type === "related" ? "6 4" : undefined,
        },
        markerEnd:
          e.edge_type === "prerequisite"
            ? { type: MarkerType.ArrowClosed, color: "hsl(var(--accent))" }
            : undefined,
      })),
    [],
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node.data as GraphNodeData);
  }, []);

  const handleDiagnose = () => {
    if (!selectedNode) return;
    diagnoseMutation.mutate(selectedNode.id);
  };

  return (
    <div className="relative h-[calc(100vh-140px)] w-full rounded-[var(--radius-xl)] border border-[hsl(var(--border))] bg-[hsl(var(--background))]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.4}
        maxZoom={1.5}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
      <DetailPanel
        node={selectedNode}
        diagnosis={diagnoseMutation.data?.data}
        onClose={() => setSelectedNode(null)}
        onDiagnose={handleDiagnose}
        diagnosing={diagnoseMutation.isPending}
      />
    </div>
  );
}
