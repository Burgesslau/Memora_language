import { create } from "zustand";
import { persist } from "zustand/middleware";

interface ThemeWheelState {
  hue: number;
  saturation: number;
  lightness: number;
  setWheel: (h: number, s: number, l: number) => void;
  applyToDocument: () => void;
}

function injectHslVariables(h: number, s: number, l: number) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.style.setProperty("--accent", `${h} ${s}% ${l}%`);
  root.style.setProperty("--accent-hover", `${h} ${s}% ${Math.max(l - 10, 0)}%`);
  root.style.setProperty("--accent-active", `${h} ${s}% ${Math.max(l - 15, 0)}%`);
  root.style.setProperty("--graph-highlight", `${(h + 120) % 360} ${s}% ${l}%`);
}

export const useThemeStore = create<ThemeWheelState>()(
  persist(
    (set, get) => ({
      hue: 243,
      saturation: 75,
      lightness: 59,
      setWheel: (h, s, l) => {
        set({ hue: h, saturation: s, lightness: l });
        injectHslVariables(h, s, l);
      },
      applyToDocument: () => {
        const { hue, saturation, lightness } = get();
        injectHslVariables(hue, saturation, lightness);
      },
    }),
    { name: "sg-theme-wheel" },
  ),
);
