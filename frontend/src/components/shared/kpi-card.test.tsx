import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KpiCard } from './kpi-card';
import { Flame } from 'lucide-react';

describe('KpiCard', () => {
  it('renders title and value', () => {
    render(
      <KpiCard
        title="连续学习天数"
        value={7}
        icon={Flame}
      />
    );

    expect(screen.getByText(/连续学习天数/)).toBeInTheDocument();
    expect(screen.getByText('7')).toBeInTheDocument();
  });

  it('renders subtitle when provided', () => {
    render(
      <KpiCard
        title="连续学习天数"
        value={7}
        subtitle="保持心流"
        icon={Flame}
      />
    );

    expect(screen.getByText(/保持心流/)).toBeInTheDocument();
  });

  it('does not render subtitle when not provided', () => {
    const { container } = render(
      <KpiCard
        title="连续学习天数"
        value={7}
        icon={Flame}
      />
    );

    expect(container.textContent).not.toContain('保持心流');
  });

  it('applies highlight styling when highlight prop is true', () => {
    const { container } = render(
      <KpiCard
        title="连续学习天数"
        value={7}
        icon={Flame}
        highlight
      />
    );

    const card = container.querySelector('[class*="border"]');
    expect(card).toBeInTheDocument();
  });

  it('renders icon from Lucide', () => {
    const { container } = render(
      <KpiCard
        title="连续学习天数"
        value={7}
        icon={Flame}
      />
    );

    // Check for icon rendering
    const iconContainer = container.querySelector('[class*="bg-"]');
    expect(iconContainer).toBeInTheDocument();
  });

  it('formats value correctly for string values', () => {
    render(
      <KpiCard
        title="今日学习时长"
        value="45 min"
        icon={Flame}
      />
    );

    expect(screen.getByText(/45 min/)).toBeInTheDocument();
  });

  it('formats value correctly for numeric values', () => {
    render(
      <KpiCard
        title="待修复漏洞"
        value={3}
        icon={Flame}
      />
    );

    expect(screen.getByText('3')).toBeInTheDocument();
  });
});
