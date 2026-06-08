"use client";

import { Header } from "@/components/layout/header";
import { MicButton } from "@/components/speech/mic-button";
import { LiveTranscript } from "@/components/speech/live-transcript";
import { useSpeechRecognition } from "@/hooks/useSpeechRecognition";
import { useAudioStore } from "@/stores/useAudioStore";
import { Card, CardContent } from "@/components/ui/card";

export default function TalkPage() {
  const { start, stop, supported } = useSpeechRecognition();
  const { transcript, reset } = useAudioStore();

  return (
    <>
      <Header title="口语练兵场" subtitle="低延迟实时字幕 + 自由练习" />
      <div className="flex flex-1 flex-col items-center justify-center gap-8 p-8">
        <MicButton
          onStart={() => { reset(); start(); }}
          onStop={stop}
          disabled={!supported}
        />
        <LiveTranscript />
        {transcript && (
          <Card className="max-w-lg">
            <CardContent className="p-4 text-sm text-[hsl(var(--muted))]">
              已录制内容将保留在本地，可在自由表达模式中提交分析。
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
