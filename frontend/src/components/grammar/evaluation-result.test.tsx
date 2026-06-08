import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EvaluationResult } from './evaluation-result';
import type { ParseOutputResponse } from '@/types/api';

describe('EvaluationResult', () => {
  const mockFreeResult: ParseOutputResponse = {
    passed: true,
    mode: 'free',
    user_text: 'I am learning English.',
    core_structure: {
      has_subject: true,
      has_verb: true,
      has_object: false,
      is_semantically_fluent: true,
      structure_score: 0.9,
    },
    silent_errors: [
      {
        grammar_point: 'article_usage',
        error_type: 'MISSING_ARTICLE',
        message: 'Missing article before "English"',
        confidence: 0.8,
      },
    ],
    error_tags: [],
    feedback: 'Good sentence structure!',
    micro_drills: [],
  };

  const mockStrictResult: ParseOutputResponse = {
    passed: false,
    mode: 'strict',
    user_text: 'He go to school.',
    core_structure: {
      has_subject: true,
      has_verb: true,
      has_object: false,
      is_semantically_fluent: true,
      structure_score: 0.7,
    },
    silent_errors: [],
    error_tags: [
      {
        grammar_point: 'third_person_singular',
        message: 'Missing -s for third person singular',
        severity: 'high',
        star_level: 2,
        error_type: 'VERB_FORM',
        span: { start_char: 3, end_char: 5, text: 'go', token_index: 1 },
        suggestion: 'goes',
      },
    ],
    feedback: 'Verb form error detected.',
    micro_drills: [],
  };

  it('renders pass/fail badge correctly', () => {
    const { rerender } = render(<EvaluationResult result={mockFreeResult} />);
    const badges = screen.getAllByText(/通过/);
    expect(badges.length).toBeGreaterThan(0);

    rerender(<EvaluationResult result={mockStrictResult} />);
    expect(screen.getByText(/未通过/)).toBeInTheDocument();
  });

  it('displays feedback message', () => {
    render(<EvaluationResult result={mockFreeResult} />);
    expect(screen.getByText(/Good sentence structure!/)).toBeInTheDocument();
  });

  it('shows structure score and error count in free mode', () => {
    const { container } = render(<EvaluationResult result={mockFreeResult} />);
    expect(screen.getByText(/结构评分/)).toBeInTheDocument();
    // The score is displayed with percentage styling
    const scoreElements = container.querySelectorAll('[class*="font-semibold"]');
    let found90 = false;
    scoreElements.forEach(el => {
      if (el.textContent?.includes('90')) found90 = true;
    });
    expect(found90).toBe(true);
    expect(screen.getByText(/发现问题/)).toBeInTheDocument();
  });

  it('displays silent errors in free mode', () => {
    render(<EvaluationResult result={mockFreeResult} />);
    expect(screen.getByText(/静默记录/)).toBeInTheDocument();
    expect(screen.getByText(/Missing article before "English"/)).toBeInTheDocument();
  });

  it('displays error tags in strict mode', () => {
    const { container } = render(<EvaluationResult result={mockStrictResult} />);
    expect(screen.getByText(/third_person_singular/)).toBeInTheDocument();
    
    // Check that error message is in the document somewhere
    const errorElements = container.querySelectorAll('span');
    let foundError = false;
    errorElements.forEach(el => {
      if (el.textContent?.includes('Missing -s for third person singular')) foundError = true;
    });
    expect(foundError).toBe(true);
  });

  it('displays user text in free mode', () => {
    render(<EvaluationResult result={mockFreeResult} />);
    expect(screen.getByText(/I am learning English\./)).toBeInTheDocument();
  });
});
