"use client";

import { useCallback, useEffect, useRef } from "react";
import { useAudioStore } from "@/stores/useAudioStore";

interface SpeechRecognitionEvent {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionResultList {
  length: number;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  isFinal: boolean;
  [index: number]: { transcript: string };
}

interface SpeechRecognitionInstance extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  onend: (() => void) | null;
}

type SpeechRecognitionCtor = new () => SpeechRecognitionInstance;

function getSpeechRecognition(): SpeechRecognitionCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as Window & {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

/** Web Speech API 实时字幕 Hook */
export function useSpeechRecognition() {
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const {
    isRecording,
    setRecording,
    setTranscript,
    setInterimTranscript,
    reset,
  } = useAudioStore();

  const start = useCallback(() => {
    const Ctor = getSpeechRecognition();
    if (!Ctor) return false;

    const recognition = new Ctor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const text = event.results[i][0].transcript;
        if (event.results[i].isFinal) final += text;
        else interim += text;
      }
      if (final) setTranscript(useAudioStore.getState().transcript + final);
      setInterimTranscript(interim);
    };

    recognition.onend = () => setRecording(false);
    recognition.start();
    recognitionRef.current = recognition;
    setRecording(true);
    return true;
  }, [setRecording, setTranscript, setInterimTranscript]);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setRecording(false);
    setInterimTranscript("");
  }, [setRecording, setInterimTranscript]);

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop();
    };
  }, []);

  return { isRecording, start, stop, reset, supported: !!getSpeechRecognition() };
}
