"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { masteryToColor, masteryToScale, masteryToStatus } from "@/lib/utils";
import type { GraphNodeData } from "@/types/api";
import { Badge } from "@/components/ui/badge";

/** React Flow 自定义语法节点 */
export function GrammarNode({ data, selected }: NodeProps) {
  const nodeData = data as GraphNodeData;
  const status = masteryToStatus(nodeData.mastery_score);
  const scale = masteryToScale(nodeData.mastery_score);
  const size = 56 * scale;

  return (
    <div
      className="relative flex flex-col items-center"
      style={{ width: size, height: size }}
    >
      <Handle type="target" position={Position.Top} className="!bg-transparent !border-0" />
      <div
        className="flex items-center justify-center rounded-full border-2 text-center transition-all"
        style={{
          width: size,
          height: size,
          borderColor: masteryToColor(nodeData.mastery_score),
          backgroundColor: `${masteryToColor(nodeData.mastery_score).replace(")", " / 0.15)")}`,
          boxShadow: selected
            ? `0 0 20px ${masteryToColor(nodeData.mastery_score).replace(")", " / 0.5)")}`
            : status === "critical"
              ? "0 0 12px hsl(var(--error) / 0.4)"
              : undefined,
        }}
      >
        <span className="px-1 text-[10px] font-medium leading-tight">{nodeData.label}</span>
      </div>
      {status === "mastered" && (
        <Badge variant="success" className="absolute -bottom-5 text-[10px]">精通</Badge>
      )}
      <Handle type="source" position={Position.Bottom} className="!bg-transparent !border-0" />
    </div>
  );
}
