import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSuppliers, getPurchaseOrders, getPurchaseOrder, createPurchaseOrder, receiveGoods, getItems } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Card, CardContent } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { formatCurrency, formatDate } from '@/lib/utils';
import { toast } from 'sonner';
import { Plus, Truck, Eye, CheckCircle } from 'lucide-react';

export default function Purchasing() {
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedPO, setSelectedPO] = useState<any>(null);
  const [receiveQty, setReceiveQty] = useState<Record<number, number>>({});

  // Create PO form state (simplified)
  const [cpSupplierId, setCpSupplierId] = useState<number | ''>('');
  const [cpWarehouseId] = useState(1);
  const [cpNotes, setCpNotes] = useState('');
  const [cpLines, setCpLines] = useState<any[]>([{ itemId: 4, itemName: 'Oak Lumber 4x4x96"', qty: 100, price: 31.0 }]);

  const { data: pos = [], isLoading } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: () => getPurchaseOrders(),
  });

  const { data: suppliers = [] } = useQuery({ queryKey: ['suppliers'], queryFn: getSuppliers });
  const { data: items = [] } = useQuery({ queryKey: ['items'], queryFn: getItems });

  const createMutation = useMutation({
    mutationFn: createPurchaseOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      resetCreateForm();
      setIsCreateOpen(false);
      toast.success('Purchase Order created');
    },
    onError: () => toast.error('Failed to create PO'),
  });

  const receiveMutation = useMutation({
    mutationFn: ({ poId, payload }: { poId: number; payload: any }) => receiveGoods(poId, payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      toast.success(data.message || 'Goods received');
      setSelectedPO(null);
      setReceiveQty({});
    },
    onError: () => toast.error('Receive failed'),
  });

  const openPOs = pos.filter((p: any) => p.status !== 'Received' && p.status !== 'Cancelled');
  const totalOpenValue = openPOs.reduce((sum: number, p: any) => sum + (p.totalAmount || 0), 0);

  function resetCreateForm() {
    setCpSupplierId('');
    setCpNotes('');
    setCpLines([{ itemId: 4, itemName: 'Oak Lumber 4x4x96"', qty: 100, price: 31.0 }]);
  }

  function addCpLine() {
    setCpLines([...cpLines, { itemId: 6, itemName: 'High-Density Foam 3"', qty: 50, price: 8.95 }]);
  }

  function updateCpLine(idx: number, field: string, val: any) {
    const next = [...cpLines];
    next[idx] = { ...next[idx], [field]: field === 'qty' || field === 'price' ? Number(val) : val };
    setCpLines(next);
  }

  function removeCpLine(idx: number) {
    if (cpLines.length === 1) return;
    setCpLines(cpLines.filter((_, i) => i !== idx));
  }

  function handleCreatePO() {
    if (!cpSupplierId || cpLines.length === 0) {
      toast.error('Select supplier and add at least one line');
      return;
    }
    const subtotal = cpLines.reduce((s, l) => s + l.qty * l.price, 0);
    const payload = {
      supplierId: Number(cpSupplierId),
      warehouseId: cpWarehouseId,
      notes: cpNotes || undefined,
      details: cpLines.map((l, i) => ({
        lineNumber: i + 1,
        itemId: l.itemId,
        quantity: l.qty,
        unitPrice: l.price,
      })),
      subtotal,
      taxAmount: 0,
      shippingAmount: Math.round(subtotal * 0.05),
      totalAmount: subtotal + Math.round(subtotal * 0.05),
    };
    createMutation.mutate(payload);
  }

  function openPODetail(po: any) {
    setSelectedPO(po);
    // Initialize receive inputs
    const init: Record<number, number> = {};
    (po.details || []).forEach((d: any) => {
      const remaining = (d.quantity || 0) - (d.quantityReceived || 0);
      init[d.poDetailId || d.PODetailID] = Math.max(0, remaining);
    });
    setReceiveQty(init);
  }

  function submitReceive() {
    if (!selectedPO) return;
    const lines = Object.entries(receiveQty)
      .filter(([, qty]) => qty > 0)
      .map(([poDetailId, qty]) => ({ poDetailId: Number(poDetailId), quantityReceived: qty }));

    if (lines.length === 0) {
      toast.error('Enter quantities to receive');
      return;
    }
    receiveMutation.mutate({
      poId: selectedPO.poId || selectedPO.PurchaseOrderID,
      payload: { lines, received_by: 'Receiving' },
    });
  }

  return (
    <div>
      <Header
        title="Purchasing &amp; Receiving"
        subtitle="Supplier orders, pricing, and goods receipt"
        actions={
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="h-4 w-4 mr-2" /> New Purchase Order
          </Button>
        }
      />

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8 mb-8">
        <Card><CardContent className="pt-6"><div className="text-sm text-slate-500">Open POs</div><div className="text-4xl font-semibold tracking-tighter mt-1">{openPOs.length}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-sm text-slate-500">Open PO Value</div><div className="text-4xl font-semibold tracking-tighter mt-1 text-emerald-600">{formatCurrency(totalOpenValue)}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-sm text-slate-500">Awaiting Delivery</div><div className="text-4xl font-semibold tracking-tighter mt-1">{openPOs.filter((p: any) => p.status === 'Sent' || p.status === 'Partial').length}</div></CardContent></Card>
      </div>

      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-lg tracking-tight">Purchase Orders</h3>
      </div>

      <Table>
        <TableHeader>
          <tr>
            <TableHead>PO #</TableHead>
            <TableHead>Supplier</TableHead>
            <TableHead>Expected</TableHead>
            <TableHead className="text-right">Total</TableHead>
            <TableHead>Status</TableHead>
            <TableHead></TableHead>
          </tr>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <tr><td colSpan={6} className="text-center py-8">Loading...</td></tr>
          ) : pos.length === 0 ? (
            <tr><td colSpan={6} className="text-center py-8 text-slate-500">No purchase orders yet</td></tr>
          ) : (
            pos.map((po: any) => (
              <TableRow key={po.poId || po.PurchaseOrderID}>
                <TableCell className="font-semibold font-mono">{po.poNumber || po.PONumber}</TableCell>
                <TableCell>{po.supplierName || po.SupplierName}</TableCell>
                <TableCell className="text-sm">{po.expectedDeliveryDate ? formatDate(po.expectedDeliveryDate) : '—'}</TableCell>
                <TableCell className="text-right font-semibold">{formatCurrency(po.totalAmount || po.TotalAmount)}</TableCell>
                <TableCell>
                  <Badge variant={po.status === 'Received' ? 'success' : po.status === 'Partial' ? 'warning' : 'neutral'}>
                    {po.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex gap-2 justify-end">
                    <Button size="sm" variant="ghost" onClick={() => openPODetail(po)}>
                      <Eye className="h-4 w-4 mr-1" /> View
                    </Button>
                    {(po.status === 'Draft' || po.status === 'Partial' || po.status === 'Sent') && (
                      <Button size="sm" variant="outline" onClick={() => openPODetail(po)}>
                        <Truck className="h-4 w-4 mr-1" /> Receive
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {/* Detail + Receive Modal */}
      <Modal isOpen={!!selectedPO} onClose={() => { setSelectedPO(null); setReceiveQty({}); }} title={selectedPO ? selectedPO.poNumber || selectedPO.PONumber : 'PO Detail'} size="lg">
        {selectedPO && (
          <div className="space-y-5">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>Supplier<br /><strong>{selectedPO.supplierName}</strong></div>
              <div>Status<br /><Badge>{selectedPO.status}</Badge></div>
              <div>Order Date<br />{formatDate(selectedPO.orderDate)}</div>
              <div>Expected<br />{selectedPO.expectedDeliveryDate ? formatDate(selectedPO.expectedDeliveryDate) : '—'}</div>
            </div>

            <div>
              <div className="font-semibold mb-2">Lines</div>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <tr>
                      <TableHead>Item</TableHead>
                      <TableHead className="text-right">Qty</TableHead>
                      <TableHead className="text-right">Received</TableHead>
                      <TableHead className="text-right">Unit Price</TableHead>
                    </tr>
                  </TableHeader>
                  <TableBody>
                    {(selectedPO.details || []).map((d: any, i: number) => {
                      const pid = d.poDetailId || d.PODetailID;
                      const remaining = (d.quantity || 0) - (d.quantityReceived || 0);
                      return (
                        <TableRow key={i}>
                          <TableCell>{d.itemName || d.itemCode}</TableCell>
                          <TableCell className="text-right">{d.quantity}</TableCell>
                          <TableCell className="text-right font-medium text-emerald-600">{d.quantityReceived || 0}</TableCell>
                          <TableCell className="text-right">{formatCurrency(d.unitPrice)}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            </div>

            {/* Receive Goods Section */}
            {(selectedPO.status !== 'Received' && selectedPO.status !== 'Cancelled') && (
              <div className="bg-slate-50 border rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Truck className="h-4 w-4" />
                  <span className="font-semibold">Receive Goods</span>
                </div>
                <div className="space-y-2 mb-3">
                  {(selectedPO.details || []).map((d: any, i: number) => {
                    const pid = d.poDetailId || d.PODetailID;
                    const remaining = Math.max(0, (d.quantity || 0) - (d.quantityReceived || 0));
                    return (
                      <div key={i} className="flex items-center gap-3 text-sm">
                        <div className="flex-1">{d.itemName}</div>
                        <div className="text-slate-500">Remaining: {remaining}</div>
                        <Input
                          type="number"
                          className="w-24 h-8"
                          value={receiveQty[pid] || 0}
                          onChange={(e) => setReceiveQty({ ...receiveQty, [pid]: Math.min(remaining, Math.max(0, Number(e.target.value))) })}
                          max={remaining}
                        />
                      </div>
                    );
                  })}
                </div>
                <Button onClick={submitReceive} disabled={receiveMutation.isPending} className="w-full">
                  <CheckCircle className="h-4 w-4 mr-2" /> Confirm Receipt &amp; Update Inventory
                </Button>
              </div>
            )}

            <div className="text-right text-sm border-t pt-3">
              Total: <span className="font-semibold text-lg">{formatCurrency(selectedPO.totalAmount)}</span>
            </div>
          </div>
        )}
      </Modal>

      {/* Create PO Modal (basic) */}
      <Modal isOpen={isCreateOpen} onClose={() => { resetCreateForm(); setIsCreateOpen(false); }} title="Create Purchase Order" size="lg">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-500">Supplier</label>
              <select className="w-full border rounded-lg p-2 mt-1 bg-white" value={cpSupplierId} onChange={(e) => setCpSupplierId(e.target.value ? Number(e.target.value) : '')}>
                <option value="">Select supplier...</option>
                {suppliers.map((s: any) => <option key={s.supplierId} value={s.supplierId}>{s.supplierName}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-500">Warehouse</label>
              <select className="w-full border rounded-lg p-2 mt-1 bg-white" disabled>
                <option>Main Plant</option>
              </select>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs text-slate-500">Lines</label>
              <Button variant="ghost" size="sm" onClick={addCpLine}>+ Add line</Button>
            </div>
            <div className="space-y-2">
              {cpLines.map((ln, idx) => (
                <div key={idx} className="flex gap-2 bg-slate-50 p-2 rounded items-center">
                  <select className="flex-1 border rounded p-1.5 text-sm" value={ln.itemId} onChange={(e) => {
                    const it = items.find((i: any) => i.itemId === Number(e.target.value));
                    updateCpLine(idx, 'itemId', e.target.value);
                    if (it) updateCpLine(idx, 'itemName', it.itemName);
                  }}>
                    {items.slice(0, 20).map((it: any) => <option key={it.itemId} value={it.itemId}>{it.itemName} ({it.itemCode})</option>)}
                  </select>
                  <Input type="number" className="w-20" value={ln.qty} onChange={(e) => updateCpLine(idx, 'qty', e.target.value)} />
                  <Input type="number" className="w-24" value={ln.price} onChange={(e) => updateCpLine(idx, 'price', e.target.value)} />
                  {cpLines.length > 1 && <button onClick={() => removeCpLine(idx)} className="text-red-500 text-sm">×</button>}
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-500">Notes</label>
            <Input value={cpNotes} onChange={(e) => setCpNotes(e.target.value)} placeholder="Lead time notes, pricing agreement..." className="mt-1" />
          </div>

          <div className="flex gap-3 pt-3 border-t">
            <Button variant="secondary" className="flex-1" onClick={() => { resetCreateForm(); setIsCreateOpen(false); }}>Cancel</Button>
            <Button className="flex-1" onClick={handleCreatePO} disabled={createMutation.isPending || !cpSupplierId}>Create PO</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
