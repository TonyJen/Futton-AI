import { render, screen } from '@testing-library/react';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  it('renders proposed status correctly', () => {
    render(<StatusBadge status="proposed" />);
    expect(screen.getByText(/proposed/i)).toBeInTheDocument();
  });

  it('renders executed status with success styling', () => {
    render(<StatusBadge status="executed" />);
    const badge = screen.getByText(/executed/i);
    expect(badge).toBeInTheDocument();
  });

  it('applies different styles for different statuses', () => {
    const { rerender } = render(<StatusBadge status="proposed" />);
    const proposed = screen.getByText(/proposed/i);

    rerender(<StatusBadge status="executed" />);
    const executed = screen.getByText(/executed/i);

    expect(proposed).not.toHaveClass('bg-green-500');
    expect(executed).toHaveClass('bg-green-500');
  });
});
