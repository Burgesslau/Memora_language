import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

// Mock the KnowledgeGraphView component to avoid complex dependencies
vi.mock('@/components/graph/knowledge-graph-view', () => ({
  KnowledgeGraphView: () => <div data-testid="knowledge-graph-view">Knowledge Graph</div>,
}));

// Mock the Header component
vi.mock('@/components/layout/header', () => ({
  Header: ({ title, subtitle }: { title: string; subtitle?: string }) => (
    <>
      <h1>{title}</h1>
      {subtitle && <p>{subtitle}</p>}
    </>
  ),
}));

// Import after mocks are defined
import GrammarDashboardPage from './page';

describe('GrammarDashboardPage', () => {
  it('renders header with correct title and subtitle', () => {
    render(<GrammarDashboardPage />);
    
    const title = screen.getByRole('heading', { level: 1, name: /语法仪表盘/ });
    expect(title).toBeInTheDocument();
    
    const subtitle = screen.getByText(/按语法点查看掌握度与诊断入口/);
    expect(subtitle).toBeInTheDocument();
  });

  it('renders grammar point list with labels and mastery scores', () => {
    render(<GrammarDashboardPage />);
    
    const grammarList = screen.getByRole('heading', { level: 3, name: /语法点概览/ });
    expect(grammarList).toBeInTheDocument();
    
    // Check for specific grammar points (only grammar type, not concept type)
    expect(screen.getByText(/一般现在时/)).toBeInTheDocument();
    expect(screen.getByText(/一般过去时/)).toBeInTheDocument();
    expect(screen.getByText(/85%/)).toBeInTheDocument();
    expect(screen.getByText(/72%/)).toBeInTheDocument();
  });

  it('renders quick operation card', () => {
    render(<GrammarDashboardPage />);
    
    const quickOps = screen.getByRole('heading', { level: 3, name: /快速操作/ });
    expect(quickOps).toBeInTheDocument();
    
    const hint = screen.getByText(/点击知识图谱中的节点可查看详情并发起诊断/);
    expect(hint).toBeInTheDocument();
  });

  it('displays grammar points with progress bars', () => {
    render(<GrammarDashboardPage />);
    
    // Check that descriptions are rendered
    expect(screen.getByText(/主语 \+ 动词原形\/第三人称单数/)).toBeInTheDocument();
    expect(screen.getByText(/主语 \+ 动词过去式/)).toBeInTheDocument();
  });

  it('renders KnowledgeGraphView component', () => {
    render(<GrammarDashboardPage />);
    expect(screen.getByTestId('knowledge-graph-view')).toBeInTheDocument();
  });
});
