import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AgentCard } from './AgentCard';
import type { Agent } from '@/lib/types';

const mockAgent: Agent = {
  id: 1,
  name: 'MRP Agent',
  description: 'Plans material requirements',
  category: 'Planning',
  lastRun: '2026-05-25T06:15:00Z',
  status: 'Completed',
  recommendationsGenerated: 4,
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
    expect(onRun).toHaveBeenCalledWith(1);
  });

  it('shows the agent category badge', () => {
    render(<AgentCard agent={mockAgent} onRun={() => {}} />);
    expect(screen.getByText('Planning')).toBeInTheDocument();
  });
});
