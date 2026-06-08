import { describe, it, expect } from 'vitest';
import { masteryToStatus, masteryToColor, masteryToScale, formatPercent } from './utils';

describe('lib/utils', () => {
  describe('masteryToStatus', () => {
    it('returns critical for score < 40', () => {
      expect(masteryToStatus(30)).toBe('critical');
      expect(masteryToStatus(0)).toBe('critical');
      expect(masteryToStatus(39)).toBe('critical');
    });

    it('returns unstable for score 40-69', () => {
      expect(masteryToStatus(40)).toBe('unstable');
      expect(masteryToStatus(50)).toBe('unstable');
      expect(masteryToStatus(69)).toBe('unstable');
    });

    it('returns growing for score 70-89', () => {
      expect(masteryToStatus(70)).toBe('growing');
      expect(masteryToStatus(80)).toBe('growing');
      expect(masteryToStatus(89)).toBe('growing');
    });

    it('returns mastered for score >= 90', () => {
      expect(masteryToStatus(90)).toBe('mastered');
      expect(masteryToStatus(100)).toBe('mastered');
    });
  });

  describe('masteryToColor', () => {
    it('returns error color for critical status', () => {
      const color = masteryToColor(30);
      expect(color).toBe('hsl(var(--error))');
    });

    it('returns warning color for unstable status', () => {
      const color = masteryToColor(50);
      expect(color).toBe('hsl(var(--warning))');
    });

    it('returns accent color for growing status', () => {
      const color = masteryToColor(75);
      expect(color).toBe('hsl(var(--accent))');
    });

    it('returns success color for mastered status', () => {
      const color = masteryToColor(95);
      expect(color).toBe('hsl(var(--success))');
    });
  });

  describe('masteryToScale', () => {
    it('returns 0.8 for critical status', () => {
      expect(masteryToScale(30)).toBe(0.8);
    });

    it('returns 1.0 for unstable status', () => {
      expect(masteryToScale(50)).toBe(1.0);
    });

    it('returns 1.2 for growing status', () => {
      expect(masteryToScale(75)).toBe(1.2);
    });

    it('returns 1.4 for mastered status', () => {
      expect(masteryToScale(95)).toBe(1.4);
    });
  });

  describe('formatPercent', () => {
    it('formats number as percentage string', () => {
      expect(formatPercent(85)).toBe('85%');
      expect(formatPercent(50)).toBe('50%');
      expect(formatPercent(100)).toBe('100%');
    });

    it('rounds percentage correctly', () => {
      expect(formatPercent(85.6)).toBe('86%');
      expect(formatPercent(85.4)).toBe('85%');
    });

    it('handles edge cases', () => {
      expect(formatPercent(0)).toBe('0%');
      expect(formatPercent(100)).toBe('100%');
    });
  });
});
