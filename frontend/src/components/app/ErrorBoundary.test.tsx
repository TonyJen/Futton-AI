import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

import { ErrorBoundary } from './ErrorBoundary';

const reportRuntimeError = vi.fn();

vi.mock('@/lib/runtime-monitoring', () => ({
  reportRuntimeError: (...args: unknown[]) => reportRuntimeError(...args),
}));

function Bomb(): never {
  throw new Error('kaboom');
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    reportRuntimeError.mockReset();
  });

  it('renders a fallback UI and reports the error', () => {
    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('kaboom')).toBeInTheDocument();
    expect(reportRuntimeError).toHaveBeenCalled();
  });
});
