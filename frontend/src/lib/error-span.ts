import type { ErrorTag } from "@/types/api";

/** 从 ErrorTag 提取字符区间（兼容 span / token_span） */
export function getErrorCharRange(tag: ErrorTag): [number, number] | null {
  if (tag.span) {
    return [tag.span.start_char, tag.span.end_char];
  }
  if (tag.token_span) {
    return tag.token_span;
  }
  return null;
}
