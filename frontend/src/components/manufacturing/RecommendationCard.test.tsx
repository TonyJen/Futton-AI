import { render, screen, fireEvent } from '@testing-library/react';
import { RecommendationCard } from './RecommendationCard';

const mockRecommendation = {
  id: 1,
  title: 'Replenish Memory Foam',
  description: 'Stock is critically low',
  confidence: 0.85,
  estimatedSavings: 1240,
  actionType: 'CREATE_PURCHASE_ORDER',
};

describe('RecommendationCard', () => {
  it('renders recommendation details', () => {
    render(
      <RecommendationCard
        recommendation={mockRecommendation}
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
        recommendation={mockRecommendation}
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
        recommendation={mockRecommendation}
        onApprove={() => {}}
        onReject={onReject}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /reject/i }));
    expect(onReject).toHaveBeenCalledWith(1);
  });
});
