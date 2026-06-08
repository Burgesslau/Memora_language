import { create } from "zustand";

interface AudioState {
  isRecording: boolean;
  transcript: string;
  interimTranscript: string;
  volumeLevel: number;
  setRecording: (v: boolean) => void;
  setTranscript: (v: string) => void;
  setInterimTranscript: (v: string) => void;
  setVolumeLevel: (v: number) => void;
  reset: () => void;
}

export const useAudioStore = create<AudioState>((set) => ({
  isRecording: false,
  transcript: "",
  interimTranscript: "",
  volumeLevel: 0,
  setRecording: (v) => set({ isRecording: v }),
  setTranscript: (v) => set({ transcript: v }),
  setInterimTranscript: (v) => set({ interimTranscript: v }),
  setVolumeLevel: (v) => set({ volumeLevel: v }),
  reset: () =>
    set({ isRecording: false, transcript: "", interimTranscript: "", volumeLevel: 0 }),
}));
