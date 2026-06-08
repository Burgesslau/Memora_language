"use client";

import { useAudioStore } from "@/stores/useAudioStore";

/** 实时字幕层（低对比度流式展示） */
export function LiveTranscript() {
  const { transcript, interimTranscript } = useAudioStore();
  const text = transcript + interimTranscript;

  if (!text) return null;

  return (
    <div className="max-w-xl text-center">
      <p className="text-lg leading-relaxed text-[hsl(var(--muted)/0.7)]">
        {transcript}
        <span className="opacity-50">{interimTranscript}</span>
      </p>
    </div>
  );
}
