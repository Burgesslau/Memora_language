import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { InlineHighlight } from './inline-highlight';
import type { ErrorTag } from '@/types/api';

describe('InlineHighlight', () => {
  it('renders text without highlights when no errors', () => {
    const text = 'This is a correct sentence.';
    const errors: ErrorTag[] = [];

    render(<InlineHighlight text={text} errorTags={errors} />);
    expect(screen.getByText(text)).toBeInTheDocument();
  });

  it('highlights error spans with correct styling', () => {
    const text = 'He go to school.';
    const errors: ErrorTag[] = [
      {
        grammar_point: 'third_person_singular',
        message: 'Missing -s for third person singular',
        severity: 'high',
        star_level: 2,
        error_type: 'VERB_FORM',
        span: { start_char: 3, end_char: 5, text: 'go', token_index: 1 },
        suggestion: 'goes',
      },
    ];

    render(<InlineHighlight text={text} errorTags={errors} />);
    
    // Check that the error text is highlighted
    const highlighted = screen.getByTitle(/Missing -s for third person singular/);
    expect(highlighted).toBeInTheDocument();
  });

  it('displays suggestion in tooltip when available', () => {
    const text = 'He go to school.';
    const errors: ErrorTag[] = [
      {
        grammar_point: 'third_person_singular',
        message: 'Missing -s for third person singular',
        severity: 'high',
        star_level: 2,
        error_type: 'VERB_FORM',
        span: { start_char: 3, end_char: 5, text: 'go', token_index: 1 },
        suggestion: 'goes',
      },
    ];

    const { container } = render(<InlineHighlight text={text} errorTags={errors} />);
    expect(container.textContent).toContain('建议: goes');
  });

  it('handles multiple error spans correctly', () => {
    const text = 'He go to the school.';
    const errors: ErrorTag[] = [
      {
        grammar_point: 'third_person_singular',
        message: 'Missing -s',
        severity: 'high',
        star_level: 2,
        error_type: 'VERB_FORM',
        span: { start_char: 3, end_char: 5, text: 'go', token_index: 1 },
        suggestion: 'goes',
      },
      {
        grammar_point: 'article_usage',
        message: 'Unnecessary article',
        severity: 'low',
        star_level: 1,
        error_type: 'ARTICLE',
        span: { start_char: 11, end_char: 14, text: 'the', token_index: 3 },
        suggestion: null,
      },
    ];

    render(<InlineHighlight text={text} errorTags={errors} />);
    
    // Both errors should be present
    expect(screen.getByTitle(/Missing -s/)).toBeInTheDocument();
    expect(screen.getByTitle(/Unnecessary article/)).toBeInTheDocument();
  });

  it('preserves non-error text between highlights', () => {
    const text = 'He go to school.';
    const errors: ErrorTag[] = [
      {
        grammar_point: 'third_person_singular',
        message: 'Missing -s',
        severity: 'high',
        star_level: 2,
        error_type: 'VERB_FORM',
        span: { start_char: 3, end_char: 5, text: 'go', token_index: 1 },
        suggestion: 'goes',
      },
    ];

    const { container } = render(<InlineHighlight text={text} errorTags={errors} />);
    
    // Check that surrounding text is preserved
    expect(container.textContent).toContain('He');
    expect(container.textContent).toContain('to school.');
  });
});
