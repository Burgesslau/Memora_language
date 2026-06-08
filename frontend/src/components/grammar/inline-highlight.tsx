"use client";

import type { ErrorTag } from "@/types/api";
import { getErrorCharRange } from "@/lib/error-span";
import { Badge } from "@/components/ui/badge";

interface InlineHighlightProps {
  text: string;
  errorTags: ErrorTag[];
}

/** 严谨模式：行内语法错误高亮 */
export function InlineHighlight({ text, errorTags }: InlineHighlightProps) {
  if (errorTags.length === 0) {
    return <p className="text-base leading-relaxed">{text}</p>;
  }

  const spans = errorTags
    .map((e) => ({ err: e, range: getErrorCharRange(e) }))
    .filter((item): item is { err: ErrorTag; range: [number, number] } => item.range !== null)
    .sort((a, b) => a.range[0] - b.range[0]);

  const parts: React.ReactNode[] = [];
  let cursor = 0;

  spans.forEach(({ err, range }, i) => {
    const [start, end] = range;
    if (start > cursor) parts.push(text.slice(cursor, start));
    parts.push(
      <span
        key={`err-${i}`}
        className="group relative cursor-help border-b-2 border-[hsl(var(--error))] bg-[hsl(var(--error)/0.1)] text-[hsl(var(--error))]"
        title={err.message}
      >
        {text.slice(start, end)}
        <span className="pointer-events-none absolute bottom-full left-0 z-10 mb-2 hidden w-56 rounded-[var(--radius-md)] bg-[hsl(var(--card))] p-2 text-xs shadow-floating group-hover:block">
          <Badge variant="error" className="mb-1">{err.error_type}</Badge>
          <span className="block">{err.message}</span>
          {err.suggestion && (
            <span className="mt-1 block text-[hsl(var(--success))]">建议: {err.suggestion}</span>
          )}
        </span>
      </span>,
    );
    cursor = end;
  });

  if (cursor < text.length) parts.push(text.slice(cursor));

  return <p className="text-base leading-relaxed">{parts}</p>;
}
