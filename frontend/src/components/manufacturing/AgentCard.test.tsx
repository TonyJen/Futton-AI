import { render, screen, fireEvent } from '@testing-library/react';
import { AgentCard } from './AgentCard';

const mockAgent = {
  name: 'MRP Agent',
  description: 'Plans material requirements',
  status: 'production' as const,
};

describe('AgentCard', () => {
  it('renders agent information', () => {
    render(<AgentCard agent={mockAgent} onRun={() => {}} />);
    expect(screen.getByText('MRP Agent')).toBeInTheDocument();
    expect(screen.getByText('Plans material requirements')).toBeInTheDocument();
  });

  it('calls onRun when Run button is clicked', () => {
    const onRun = vi.fn();
    render(<AgentCard agent={mockAgent} onRun={onRun} />);
    
    fireEvent.click(screen.getByRole('button', { name: /run/i }));
    expect(onRun).toHaveBeenCalledWith('MRP Agent');
  });

  it('shows production badge for production agents', () => {
    render(<AgentCard agent={mockAgent} onRun={() => {}} />);
    expect(screen.getByText('production')).toBeInTheDocument();
  });
});
