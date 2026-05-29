import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getItems, getItemBOM } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Modal } from '@/components/ui/Modal';
import { BOMTree } from '@/components/manufacturing/BOMTree';
import { BOMFlow } from '@/components/manufacturing/BOMFlow';
import { Badge } from '@/components/ui/Badge';
import { PageErrorState, PageLoadingState } from '@/components/app/PageState';
import { formatCurrency } from '@/lib/utils';
import { Search, Eye } from 'lucide-react';
import type { Item, BOMComponent } from '@/lib/types';
import { toast } from 'sonner';

export default function Items() {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('All');
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);
  const [bomData, setBomData] = useState<BOMComponent[]>([]);
  const [isBomOpen, setIsBomOpen] = useState(false);

  const itemsQuery = useQuery({
    queryKey: ['items', search, typeFilter],
    queryFn: () => getItems({ search, type: typeFilter }),
  });
  const items = itemsQuery.data ?? [];

  const openBOM = async (item: Item) => {
    setSelectedItem(item);
    try {
      const bom = await getItemBOM(item.itemId);
      setBomData(bom);
      setIsBomOpen(true);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to load the BOM');
    }
  };

  const itemTypes = ['All', 'Raw Material', 'Component', 'Finished Good', 'Packaging'];

  if (itemsQuery.isLoading) {
    return <PageLoadingState title="Loading item master" description="Fetching items and BOM metadata." />;
  }

  if (itemsQuery.isError) {
    return <PageErrorState title="Item master is unavailable" onRetry={() => itemsQuery.refetch()} />;
  }

  return (
    <div>
      <Header 
        title="Items & Bill of Materials" 
        subtitle="Master data with multi-level BOM explorer"
      />

      <div className="flex items-center gap-3 mt-8 mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search by code or name..." 
            value={search} 
            onChange={(e) => setSearch(e.target.value)} 
            className="pl-9" 
          />
        </div>
        
        <select 
          value={typeFilter} 
          onChange={(e) => setTypeFilter(e.target.value)} 
          className="select w-52"
        >
          {itemTypes.map(t => <option key={t} value={t}>{t}</option>)}
        </select>

        <Button variant="secondary" className="ml-auto">
          + New Item
        </Button>
      </div>

      <Table>
        <TableHeader>
          <tr>
            <TableHead className="w-28">Item Code</TableHead>
            <TableHead>Item Name</TableHead>
            <TableHead className="w-36">Type</TableHead>
            <TableHead className="w-24 text-right">Std Cost</TableHead>
            <TableHead className="w-24 text-right">List Price</TableHead>
            <TableHead className="w-20 text-center">Lead Time</TableHead>
            <TableHead className="w-24 text-center">Reorder Pt</TableHead>
            <TableHead className="w-16"></TableHead>
          </tr>
        </TableHeader>
        <TableBody>
          {items.length === 0 ? (
            <tr><TableCell colSpan={8} className="text-center py-10 text-slate-500">No items found.</TableCell></tr>
          ) : (
            items.map(item => (
              <TableRow key={item.itemId}>
                <TableCell className="font-mono font-semibold text-primary-700">{item.itemCode}</TableCell>
                <TableCell className="font-medium text-slate-900">{item.itemName}</TableCell>
                <TableCell><Badge variant="neutral">{item.itemType}</Badge></TableCell>
                <TableCell className="text-right tabular-nums font-medium">{formatCurrency(item.standardCost)}</TableCell>
                <TableCell className="text-right tabular-nums font-semibold text-emerald-700">{formatCurrency(item.listPrice)}</TableCell>
                <TableCell className="text-center">{item.leadTimeDays} days</TableCell>
                <TableCell className="text-center font-mono">{item.reorderPoint}</TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm" onClick={() => openBOM(item)}>
                    <Eye className="h-4 w-4 mr-1.5" /> BOM
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {/* BOM Modal */}
      <Modal 
        isOpen={isBomOpen} 
        onClose={() => setIsBomOpen(false)} 
        title={selectedItem ? `BOM: ${selectedItem.itemCode} — ${selectedItem.itemName}` : ''}
        size="lg"
      >
        {selectedItem && (
          <>
            <div className="mb-3 text-xs font-medium text-slate-500">Interactive Visualizer (drag nodes • zoom • click for details)</div>
            <BOMFlow components={bomData} rootItemName={selectedItem.itemName} />

            <div className="mt-6 text-xs font-medium text-slate-500 mb-2">Text Tree (detailed)</div>
            <BOMTree components={bomData} rootItemName={selectedItem.itemName} />
          </>
        )}
        
        <div className="mt-6 pt-4 border-t text-xs text-slate-500">
          All quantities per finished unit. Visual + recursive explosion used by MRP agent.
        </div>
      </Modal>
    </div>
  );
}
