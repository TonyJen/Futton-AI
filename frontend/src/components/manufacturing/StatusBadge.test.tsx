import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  it('renders the provided status text', () => {
    render(<StatusBadge status="Running" />);
    expect(screen.getByText(/running/i)).toBeInTheDocument();
  });

  it('maps success statuses to the success badge style', () => {
    render(<StatusBadge status="Executed" />);
    const badge = screen.getByText(/executed/i);
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('badge-success');
  });

  it('applies different styles for warning and danger statuses', () => {
    const { rerender } = render(<StatusBadge status="Pending" />);
    const pending = screen.getByText(/pending/i);
    expect(pending).toHaveClass('badge-warning');

    rerender(<StatusBadge status="Low Stock" />);
    const lowStock = screen.getByText(/low stock/i);

    expect(lowStock).toHaveClass('badge-danger');
  });
});
