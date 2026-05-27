import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getReturns, createReturn, getCustomers, getSalesOrders } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Card, CardContent } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { formatCurrency, formatDate } from '@/lib/utils';
import { toast } from 'sonner';
import { Plus, RotateCcw, Eye, X } from 'lucide-react';

const RETURN_REASONS = [
  { id: 1, label: 'Damaged in transit' },
  { id: 2, label: 'Defective / Quality issue' },
  { id: 3, label: 'Customer changed mind' },
  { id: 4, label: 'Wrong item shipped' },
  { id: 5, label: 'Other' },
];

export default function Returns() {
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedReturn, setSelectedReturn] = useState<any>(null);

  // Create form state
  const [crOrderId, setCrOrderId] = useState<number | ''>('');
  const [crCustomerId, setCrCustomerId] = useState<number | ''>('');
  const [crReasonId, setCrReasonId] = useState(1);
  const [crNotes, setCrNotes] = useState('');
  const [crLines, setCrLines] = useState<any[]>([{ itemId: 2, itemName: 'Classic Futon Mattress - Queen', qty: 1, price: 329, refund: 329 }]);

  const { data: returns = [], isLoading } = useQuery({
    queryKey: ['returns'],
    queryFn: getReturns,
  });

  const { data: customers = [] } = useQuery({ queryKey: ['customers'], queryFn: getCustomers });
  const { data: orders = [] } = useQuery({ queryKey: ['sales-orders'], queryFn: getSalesOrders });

  const createMutation = useMutation({
    mutationFn: createReturn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['returns'] });
      resetCreateForm();
      setIsCreateOpen(false);
      toast.success('Return created');
    },
    onError: () => toast.error('Failed to create return'),
  });

  const pendingReturns = returns.filter((r: any) => r.status === 'Pending' || r.status === 'Approved');
  const totalRefund = returns.reduce((s: number, r: any) => s + (r.refundAmount || 0), 0);

  function resetCreateForm() {
    setCrOrderId('');
    setCrCustomerId('');
    setCrReasonId(1);
    setCrNotes('');
    setCrLines([{ itemId: 2, itemName: 'Classic Futon Mattress - Queen', qty: 1, price: 329, refund: 329 }]);
  }

  function addCrLine() {
    setCrLines([...crLines, { itemId: 1, itemName: 'Deluxe Futon Frame - Oak', qty: 1, price: 449, refund: 449 }]);
  }
  function updateCrLine(idx: number, field: string, val: any) {
    const next = [...crLines];
    next[idx] = { ...next[idx], [field]: field === 'qty' || field === 'price' || field === 'refund' ? Number(val) : val };
    setCrLines(next);
  }
  function removeCrLine(idx: number) {
    if (crLines.length === 1) return;
    setCrLines(crLines.filter((_, i) => i !== idx));
  }

  function handleCreateReturn() {
    if (!crOrderId || !crCustomerId) {
      toast.error('Select order and customer');
      return;
    }
    const refundTotal = crLines.reduce((s, l) => s + (l.refund || l.qty * l.price), 0);
    const payload = {
      SalesOrderID: Number(crOrderId),
      CustomerID: Number(crCustomerId),
      ReturnReasonID: crReasonId,
      Notes: crNotes || undefined,
      details: crLines.map((l, i) => ({
        SODetailID: 100 + i, // placeholder - real would come from order lines
        ItemID: l.itemId,
        QuantityReturned: l.qty,
        UnitPrice: l.price,
        RefundAmount: l.refund || (l.qty * l.price),
        Disposition: 'Restock',
      })),
      RefundAmount: refundTotal,
      RestockingFee: Math.round(refundTotal * 0.05),
    };
    createMutation.mutate(payload);
  }

  function processRestock(ret: any) {
    // In real app this would call a backend action that does inventory + update status
    toast.success(`Restock processed for ${ret.returnNumber}`, { description: 'Inventory updated + return marked Received' });
    // Optimistic local update for demo
    setSelectedReturn({ ...ret, status: 'Received' });
    queryClient.invalidateQueries({ queryKey: ['returns'] });
  }

  return (
    <div>
      <Header
        title="Returns &amp; RMAs"
        subtitle="Customer returns, restocking and refund processing"
        actions={
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="h-4 w-4 mr-2" /> New Return
          </Button>
        }
      />

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card><CardContent className="pt-6"><div className="text-sm text-slate-500">Open Returns</div><div className="text-4xl font-semibold tracking-tighter mt-1">{pendingReturns.length}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-sm text-slate-500">Total Refunds (all time)</div><div className="text-4xl font-semibold tracking-tighter mt-1 text-rose-600">{formatCurrency(totalRefund)}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-sm text-slate-500">Restock-eligible</div><div className="text-4xl font-semibold tracking-tighter mt-1">{returns.filter((r: any) => r.status !== 'Denied').length}</div></CardContent></Card>
      </div>

      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-lg tracking-tight">All Returns</h3>
      </div>

      <Table>
        <TableHeader>
          <tr>
            <TableHead>Return #</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead>Related Order</TableHead>
            <TableHead>Date</TableHead>
            <TableHead className="text-right">Refund</TableHead>
            <TableHead>Status</TableHead>
            <TableHead></TableHead>
          </tr>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <tr><td colSpan={7} className="text-center py-8">Loading returns...</td></tr>
          ) : returns.length === 0 ? (
            <tr><td colSpan={7} className="text-center py-8 text-slate-500">No returns recorded yet</td></tr>
          ) : (
            returns.map((r: any) => (
              <TableRow key={r.returnId || r.ReturnID}>
                <TableCell className="font-semibold font-mono">{r.returnNumber || r.ReturnNumber}</TableCell>
                <TableCell>{r.customerName || r.CustomerName}</TableCell>
                <TableCell className="font-mono text-sm">{r.orderNumber || `SO-${r.salesOrderId || r.SalesOrderID}`}</TableCell>
                <TableCell className="text-sm">{formatDate(r.returnDate || r.ReturnDate)}</TableCell>
                <TableCell className="text-right font-semibold text-rose-600">{formatCurrency(r.refundAmount || r.RefundAmount)}</TableCell>
                <TableCell>
                  <Badge variant={r.status === 'Approved' || r.status === 'Received' ? 'success' : r.status === 'Denied' ? 'danger' : 'warning'}>
                    {r.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex gap-2 justify-end">
                    <Button size="sm" variant="ghost" onClick={() => setSelectedReturn(r)}>
                      <Eye className="h-4 w-4 mr-1" /> View
                    </Button>
                    {(r.status === 'Approved' || r.status === 'Pending') && (
                      <Button size="sm" variant="outline" onClick={() => processRestock(r)}>
                        <RotateCcw className="h-3.5 w-3.5 mr-1" /> Restock
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {/* Detail Modal */}
      <Modal isOpen={!!selectedReturn} onClose={() => setSelectedReturn(null)} title={selectedReturn ? selectedReturn.returnNumber || 'Return Detail' : ''}>
        {selectedReturn && (
          <div className="space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-x-8 gap-y-3">
              <div>Customer: <strong>{selectedReturn.customerName}</strong></div>
              <div>Status: <Badge>{selectedReturn.status}</Badge></div>
              <div>Order: <span className="font-mono">{selectedReturn.orderNumber || selectedReturn.salesOrderId}</span></div>
              <div>Refund: <span className="font-semibold text-rose-600">{formatCurrency(selectedReturn.refundAmount)}</span></div>
            </div>

            <div>
              <div className="font-medium mb-1">Items Returned</div>
              <div className="border rounded p-2">
                {(selectedReturn.details || []).map((d: any, i: number) => (
                  <div key={i} className="flex justify-between py-0.5 border-b last:border-none text-sm">
                    <span>{d.itemName} ×{d.quantityReturned}</span>
                    <span>{formatCurrency(d.refundAmount)} • {d.disposition}</span>
                  </div>
                ))}
                {(!selectedReturn.details || selectedReturn.details.length === 0) && <div className="text-slate-500">No detail lines</div>}
              </div>
            </div>

            {selectedReturn.notes && <div>Notes: {selectedReturn.notes}</div>}

            {(selectedReturn.status === 'Approved' || selectedReturn.status === 'Pending') && (
              <Button className="w-full mt-2" onClick={() => processRestock(selectedReturn)}>
                Process Restock &amp; Close Return
              </Button>
            )}
          </div>
        )}
      </Modal>

      {/* Create Return Modal */}
      <Modal isOpen={isCreateOpen} onClose={() => { resetCreateForm(); setIsCreateOpen(false); }} title="Create Return / RMA" size="lg">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-500">Related Sales Order</label>
              <select className="w-full border rounded-lg p-2 mt-1 bg-white" value={crOrderId} onChange={(e) => {
                const v = e.target.value ? Number(e.target.value) : '';
                setCrOrderId(v);
                const ord = orders.find((o: any) => (o.orderId || o.SalesOrderID) === v);
                if (ord) setCrCustomerId(ord.customerId || ord.CustomerID || '');
              }}>
                <option value="">Select order...</option>
                {orders.map((o: any) => (
                  <option key={o.orderId || o.SalesOrderID} value={o.orderId || o.SalesOrderID}>
                    {o.orderNumber || o.OrderNumber} — {o.customerName || o.CustomerName}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-500">Customer</label>
              <select className="w-full border rounded-lg p-2 mt-1 bg-white" value={crCustomerId} onChange={(e) => setCrCustomerId(e.target.value ? Number(e.target.value) : '')}>
                <option value="">Select customer</option>
                {customers.map((c: any) => <option key={c.customerId} value={c.customerId}>{c.customerName}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-500">Reason</label>
            <select className="w-full border rounded-lg p-2 mt-1 bg-white" value={crReasonId} onChange={(e) => setCrReasonId(Number(e.target.value))}>
              {RETURN_REASONS.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
            </select>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs text-slate-500">Returned Items</label>
              <Button variant="ghost" size="sm" onClick={addCrLine}>+ Add line</Button>
            </div>
            <div className="space-y-2">
              {crLines.map((ln, idx) => (
                <div key={idx} className="flex gap-2 items-center bg-slate-50 p-2 rounded">
                  <Input className="flex-1" value={ln.itemName} onChange={(e) => updateCrLine(idx, 'itemName', e.target.value)} />
                  <Input type="number" className="w-16" value={ln.qty} onChange={(e) => updateCrLine(idx, 'qty', e.target.value)} />
                  <Input type="number" className="w-20" value={ln.price} onChange={(e) => updateCrLine(idx, 'price', e.target.value)} />
                  <Input type="number" className="w-24" value={ln.refund} onChange={(e) => updateCrLine(idx, 'refund', e.target.value)} placeholder="Refund" />
                  {crLines.length > 1 && <button onClick={() => removeCrLine(idx)} className="text-red-500"><X className="h-4 w-4" /></button>}
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-500">Notes</label>
            <Input value={crNotes} onChange={(e) => setCrNotes(e.target.value)} placeholder="Condition notes, photos ref..." className="mt-1" />
          </div>

          <div className="flex gap-3 pt-3 border-t">
            <Button variant="secondary" className="flex-1" onClick={() => { resetCreateForm(); setIsCreateOpen(false); }}>Cancel</Button>
            <Button className="flex-1" onClick={handleCreateReturn} disabled={createMutation.isPending}>Create Return</Button>
          </div>
          <div className="text-[10px] text-center text-slate-500">Restocking action available after approval in the detail view.</div>
        </div>
      </Modal>
    </div>
  );
}
