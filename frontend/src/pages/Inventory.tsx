import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getInventory, getInventoryTransactions } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Modal } from '@/components/ui/Modal';
import { Badge } from '@/components/ui/Badge';
import { Tabs } from '@/components/ui/Tabs';
import { StatusBadge } from '@/components/manufacturing/StatusBadge';
import { formatDateTime, formatNumber } from '@/lib/utils';
import { PageErrorState, PageLoadingState } from '@/components/app/PageState';
import { AlertTriangle, ArrowRight } from 'lucide-react';
import type { InventoryRecord, InventoryTransaction } from '@/lib/types';
import { toast } from 'sonner';

const WAREHOUSES = ['All', 'Main Plant', 'East Warehouse', 'West Distribution', 'Finished Goods'];

export default function Inventory() {
  const [activeWarehouse, setActiveWarehouse] = useState('All');
  const [selectedItem, setSelectedItem] = useState<InventoryRecord | null>(null);
  const [txns, setTxns] = useState<InventoryTransaction[]>([]);
  const [isTxnOpen, setIsTxnOpen] = useState(false);

  const inventoryQuery = useQuery({
    queryKey: ['inventory', activeWarehouse],
    queryFn: () => getInventory(activeWarehouse === 'All' ? undefined : activeWarehouse),
  });
  const inventory = inventoryQuery.data ?? [];

  const openTransactions = async (item: InventoryRecord) => {
    setSelectedItem(item);
    try {
      const data = await getInventoryTransactions(item.itemId);
      setTxns(data);
      setIsTxnOpen(true);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to load transaction history');
    }
  };

  const lowStock = inventory.filter(i => i.available < 15);

  if (inventoryQuery.isLoading) {
    return <PageLoadingState title="Loading inventory" description="Fetching warehouse balances and stock availability." />;
  }

  if (inventoryQuery.isError) {
    return <PageErrorState title="Inventory data is unavailable" onRetry={() => inventoryQuery.refetch()} />;
  }

  return (
    <div>
      <Header title="Inventory Operations" subtitle="Multi-warehouse visibility & transaction history" />

      {/* Warehouse Tabs */}
      <Tabs 
        tabs={WAREHOUSES.map(w => ({ id: w, label: w }))} 
        activeTab={activeWarehouse} 
        onChange={setActiveWarehouse} 
        className="mt-8 mb-6" 
      />

      {/* Alerts */}
      {lowStock.length > 0 && (
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-2xl p-4 flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          <div className="font-semibold text-amber-900">
            {lowStock.length} items below critical threshold in current view
          </div>
        </div>
      )}

      <Table>
        <TableHeader>
          <tr>
            <TableHead>Item</TableHead>
            <TableHead>Warehouse</TableHead>
            <TableHead className="text-right">On Hand</TableHead>
            <TableHead className="text-right">Allocated</TableHead>
            <TableHead className="text-right">Available</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Last Updated</TableHead>
            <TableHead></TableHead>
          </tr>
        </TableHeader>
        <TableBody>
          {inventory.length === 0 ? (
            <tr><td colSpan={8} className="text-center py-8 text-slate-500">No inventory records.</td></tr>
          ) : (
            inventory.map((inv) => {
              const isLow = inv.available < (inv.itemType === 'Finished Good' ? 12 : 25);
              return (
                <TableRow key={inv.inventoryId}>
                  <TableCell>
                    <div className="font-mono font-semibold">{inv.itemCode}</div>
                    <div className="text-sm text-slate-600">{inv.itemName}</div>
                  </TableCell>
                  <TableCell><Badge variant="neutral">{inv.warehouseName}</Badge></TableCell>
                  <TableCell className="text-right font-semibold tabular-nums">{formatNumber(inv.quantityOnHand)}</TableCell>
                  <TableCell className="text-right text-slate-600 tabular-nums">{formatNumber(inv.quantityAllocated)}</TableCell>
                  <TableCell className="text-right font-bold tabular-nums text-lg">{formatNumber(inv.available)}</TableCell>
                  <TableCell>
                    <StatusBadge status={isLow ? 'Low Stock' : 'In Stock'} />
                  </TableCell>
                  <TableCell className="text-xs text-slate-500">{formatDateTime(inv.lastUpdated)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" onClick={() => openTransactions(inv)}>
                      History <ArrowRight className="ml-1 h-3 w-3" />
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>

      {/* Transaction History Modal */}
      <Modal 
        isOpen={isTxnOpen} 
        onClose={() => setIsTxnOpen(false)} 
        title={selectedItem ? `Transaction History — ${selectedItem.itemCode}` : ''} 
        size="lg"
      >
        {selectedItem && (
          <>
            <div className="mb-4 text-sm text-slate-600">{selectedItem.itemName} @ {selectedItem.warehouseName}</div>
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>Date</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Qty</TableHead>
                  <TableHead>Reference</TableHead>
                  <TableHead>By</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {txns.map(t => (
                  <TableRow key={t.transactionId}>
                    <TableCell className="text-sm">{formatDateTime(t.transactionDate)}</TableCell>
                    <TableCell><StatusBadge status={t.transactionType} /></TableCell>
                    <TableCell className={`text-right font-semibold ${t.quantity < 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                      {t.quantity > 0 ? '+' : ''}{t.quantity}
                    </TableCell>
                    <TableCell className="font-mono text-xs">{t.referenceNumber || t.notes}</TableCell>
                    <TableCell>{t.createdBy}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </>
        )}
      </Modal>
    </div>
  );
}
