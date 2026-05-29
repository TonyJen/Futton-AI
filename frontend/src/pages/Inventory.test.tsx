import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

import Inventory from './Inventory';

const getInventory = vi.fn();
const getInventoryTransactions = vi.fn();

vi.mock('@/lib/api', () => ({
  getInventory: (...args: unknown[]) => getInventory(...args),
  getInventoryTransactions: (...args: unknown[]) => getInventoryTransactions(...args),
}));

function renderInventory() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <Inventory />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('Inventory page', () => {
  beforeEach(() => {
    getInventory.mockReset();
    getInventoryTransactions.mockReset();
  });

  it('shows a page loading state', () => {
    getInventory.mockReturnValue(new Promise(() => undefined));

    renderInventory();

    expect(screen.getByText('Loading inventory')).toBeInTheDocument();
  });

  it('shows a page error state when the query fails', async () => {
    getInventory.mockRejectedValue(new Error('backend down'));

    renderInventory();

    await waitFor(() => {
      expect(screen.getByText('Inventory data is unavailable')).toBeInTheDocument();
    });
  });

  it('renders inventory data and the low stock alert', async () => {
    getInventory.mockResolvedValue([
      {
        inventoryId: 1,
        itemId: 10,
        itemCode: 'RM-100',
        itemName: 'Foam Roll',
        itemType: 'Raw Material',
        warehouseName: 'Main Plant',
        quantityOnHand: 12,
        quantityAllocated: 2,
        available: 10,
        lastUpdated: '2026-05-29T09:00:00Z',
      },
    ]);
    getInventoryTransactions.mockResolvedValue([]);

    renderInventory();

    expect(await screen.findByText('Foam Roll')).toBeInTheDocument();
    expect(screen.getByText('1 items below critical threshold in current view')).toBeInTheDocument();
  });
});
