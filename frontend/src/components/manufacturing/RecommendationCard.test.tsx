import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { RecommendationCard } from './RecommendationCard';
import type { AgentRecommendation } from '@/lib/types';

const mockRecommendation: AgentRecommendation = {
  id: 1,
  agentName: 'MRP Agent',
  title: 'Replenish Memory Foam',
  description: 'Stock is critically low',
  impact: 'Avoids a line stoppage',
  confidence: 85,
  estimatedSavings: 1240,
  actionType: 'CREATE_PO',
  status: 'PENDING',
  createdAt: '2026-05-25T06:18:00Z',
};

describe('RecommendationCard', () => {
  it('renders recommendation details', () => {
    render(
      <RecommendationCard
        rec={mockRecommendation}
        onApprove={() => {}}
        onReject={() => {}}
      />
    );

    expect(screen.getByText('Replenish Memory Foam')).toBeInTheDocument();
    expect(screen.getByText(/85%/)).toBeInTheDocument();
  });

  it('calls onApprove when Approve is clicked', () => {
    const onApprove = vi.fn();
    render(
      <RecommendationCard
        rec={mockRecommendation}
        onApprove={onApprove}
        onReject={() => {}}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /approve/i }));
    expect(onApprove).toHaveBeenCalledWith(1);
  });

  it('calls onReject when Reject is clicked', () => {
    const onReject = vi.fn();
    render(
      <RecommendationCard
        rec={mockRecommendation}
        onApprove={() => {}}
        onReject={onReject}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /reject/i }));
    expect(onReject).toHaveBeenCalledWith(1);
  });
});
