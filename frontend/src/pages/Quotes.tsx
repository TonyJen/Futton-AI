import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getQuotes, createQuote, convertQuoteToOrder, updateQuoteStatus, getCustomers, getItems } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Card, CardContent } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { formatCurrency, formatDate } from '@/lib/utils';
import { toast } from 'sonner';
import { Plus, FileText, ArrowRight, Trash2 } from 'lucide-react';

export default function Quotes() {
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedQuote, setSelectedQuote] = useState<any>(null);
  const [isConverting, setIsConverting] = useState(false);

  // Create Quote form state
  const [cqCustomerId, setCqCustomerId] = useState<number | ''>('');
  const [cqCustomerSearch, setCqCustomerSearch] = useState('');
  const [cqItemSearch, setCqItemSearch] = useState('');
  const [cqPendingItemId, setCqPendingItemId] = useState<number | ''>('');
  const [cqPendingQty, setCqPendingQty] = useState(1);
  const [cqPendingPrice, setCqPendingPrice] = useState(0);
  const [cqLines, setCqLines] = useState<any[]>([]);
  const [cqDiscount, setCqDiscount] = useState(0);
  const [cqTaxRate, setCqTaxRate] = useState(0.08); // 8%
  const [cqShipping, setCqShipping] = useState(0);
  const [cqNotes, setCqNotes] = useState('');

  const { data: quotes = [], isLoading } = useQuery({
    queryKey: ['quotes'],
    queryFn: getQuotes,
  });

  const { data: customers = [] } = useQuery({
    queryKey: ['customers'],
    queryFn: getCustomers,
  });

  const { data: items = [] } = useQuery({
    queryKey: ['items'],
    queryFn: () => getItems(),
  });

  // Filtered customers for picker
  const filteredCustomers = useMemo(() => {
    const q = cqCustomerSearch.toLowerCase();
    return customers.filter((c: any) =>
      !q || c.customerName?.toLowerCase().includes(q) || c.customerCode?.toLowerCase().includes(q)
    );
  }, [customers, cqCustomerSearch]);

  // Items filtered for line item picker (prefer Finished Goods)
  const filteredItemsForPicker = useMemo(() => {
    const q = cqItemSearch.toLowerCase();
    let list = items.filter((i: any) => i.isActive !== false);
    if (q) {
      list = list.filter((i: any) =>
        i.itemName?.toLowerCase().includes(q) || i.itemCode?.toLowerCase().includes(q)
      );
    }
    // Put finished goods first
    return [...list].sort((a: any, b: any) => {
      const aFG = a.itemType === 'Finished Good' ? 0 : 1;
      const bFG = b.itemType === 'Finished Good' ? 0 : 1;
      return aFG - bFG || a.itemName.localeCompare(b.itemName);
    });
  }, [items, cqItemSearch]);

  // Live calculations for create quote
  const createCalc = useMemo(() => {
    const subtotal = cqLines.reduce((sum: number, ln: any) => {
      const lt = ln.quantity * ln.unitPrice * (1 - (ln.discountPercent || 0) / 100);
      return sum + lt;
    }, 0);
    const disc = Math.min(cqDiscount, subtotal);
    const taxable = subtotal - disc;
    const tax = Math.round(taxable * cqTaxRate * 100) / 100;
    const total = taxable + tax + cqShipping;
    return { subtotal, discount: disc, tax, shipping: cqShipping, total };
  }, [cqLines, cqDiscount, cqTaxRate, cqShipping]);

  const createQuoteMutation = useMutation({
    mutationFn: createQuote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      resetCreateQuoteForm();
      setIsCreateModalOpen(false);
      toast.success('Quote created successfully');
    },
    onError: (e: any) => toast.error(e?.message || 'Failed to create quote'),
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ quoteId, status }: { quoteId: number; status: string }) => 
      updateQuoteStatus(quoteId, status),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      if (selectedQuote) {
        setSelectedQuote({ ...selectedQuote, status: variables.status });
      }
      toast.success(`Quote marked as ${variables.status}`);
    },
    onError: () => toast.error('Failed to update quote status'),
  });

  const convertMutation = useMutation({
    mutationFn: convertQuoteToOrder,
    onMutate: () => setIsConverting(true),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      toast.success('Quote converted to order', {
        description: `New order: ${data.orderNumber || data.OrderNumber}`,
      });
      setSelectedQuote(null);
    },
    onError: () => toast.error('Failed to convert quote'),
    onSettled: () => setIsConverting(false),
  });

  const handleConvert = (quoteId: number) => {
    convertMutation.mutate(quoteId);
  };

  function resetCreateQuoteForm() {
    setCqCustomerId('');
    setCqCustomerSearch('');
    setCqItemSearch('');
    setCqPendingItemId('');
    setCqPendingQty(1);
    setCqPendingPrice(0);
    setCqLines([]);
    setCqDiscount(0);
    setCqTaxRate(0.08);
    setCqShipping(0);
    setCqNotes('');
  }

  function addLineFromPicker() {
    if (!cqPendingItemId) return;
    const it = items.find((i: any) => i.itemId === Number(cqPendingItemId));
    if (!it) return;
    const price = cqPendingPrice > 0 ? cqPendingPrice : (it.listPrice || it.standardCost || 0);
    const newLine = {
      tempId: Date.now(),
      itemId: it.itemId,
      itemName: it.itemName,
      itemCode: it.itemCode,
      quantity: Math.max(1, cqPendingQty),
      unitPrice: price,
      discountPercent: 0,
    };
    setCqLines([...cqLines, newLine]);
    // reset picker row
    setCqPendingItemId('');
    setCqPendingQty(1);
    setCqPendingPrice(0);
    setCqItemSearch('');
  }

  function updateLine(tempId: number, field: string, value: any) {
    setCqLines(cqLines.map(ln =>
      ln.tempId === tempId ? { ...ln, [field]: field === 'quantity' || field === 'unitPrice' || field === 'discountPercent' ? Number(value) : value } : ln
    ));
  }

  function removeLine(tempId: number) {
    setCqLines(cqLines.filter(ln => ln.tempId !== tempId));
  }

  function handleCreateQuote() {
    if (!cqCustomerId || cqLines.length === 0) {
      toast.error('Select a customer and add at least one line item');
      return;
    }
    const payload = {
      customerId: Number(cqCustomerId),
      details: cqLines.map((ln, _idx) => ({
        itemId: ln.itemId,
        quantity: ln.quantity,
        unitPrice: ln.unitPrice,
        discountPercent: ln.discountPercent || 0,
      })),
      taxAmount: createCalc.tax,
      shippingAmount: createCalc.shipping,
      discountAmount: createCalc.discount,
      notes: cqNotes || undefined,
    };
    createQuoteMutation.mutate(payload);
  }

  const pendingQuotes = quotes.filter((q: any) => q.status === 'Draft' || q.status === 'Sent');
  const acceptedQuotes = quotes.filter((q: any) => q.status === 'Accepted');

  return (
    <div>
      <Header 
        title="Sales Quotes" 
        subtitle="Manage customer quotations and conversions" 
        actions={
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" /> New Quote
          </Button>
        }
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-slate-500">Open Quotes</div>
            <div className="text-4xl font-semibold tracking-tighter mt-1">{pendingQuotes.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-slate-500">Accepted (Ready to Convert)</div>
            <div className="text-4xl font-semibold tracking-tighter mt-1 text-emerald-600">{acceptedQuotes.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-slate-500">Total Quote Value (Open)</div>
            <div className="text-4xl font-semibold tracking-tighter mt-1">
              {formatCurrency(pendingQuotes.reduce((sum: number, q: any) => sum + q.totalAmount, 0))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quotes Table */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-lg tracking-tight">All Quotes</h3>
      </div>

      <Table>
        <TableHeader>
          <tr>
            <TableHead>Quote #</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead>Date</TableHead>
            <TableHead>Expires</TableHead>
            <TableHead className="text-right">Total</TableHead>
            <TableHead>Status</TableHead>
            <TableHead></TableHead>
          </tr>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <tr><td colSpan={7} className="text-center py-8">Loading quotes...</td></tr>
          ) : quotes.length === 0 ? (
            <tr><td colSpan={7} className="text-center py-8 text-slate-500">No quotes yet</td></tr>
          ) : (
            quotes.map((quote: any) => (
              <TableRow key={quote.quoteId}>
                <TableCell className="font-semibold font-mono">{quote.quoteNumber}</TableCell>
                <TableCell>{quote.customerName || 'N/A'}</TableCell>
                <TableCell className="text-sm">{formatDate(quote.quoteDate)}</TableCell>
                <TableCell className="text-sm">{quote.expirationDate ? formatDate(quote.expirationDate) : '-'}</TableCell>
                <TableCell className="text-right font-semibold">{formatCurrency(quote.totalAmount)}</TableCell>
                <TableCell>
                  <Badge 
                    variant={
                      quote.status === 'Accepted' ? 'success' : 
                      quote.status === 'Sent' ? 'info' : 
                      quote.status === 'Declined' ? 'danger' : 'neutral'
                    }
                  >
                    {quote.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex gap-2 justify-end">
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      onClick={() => setSelectedQuote(quote)}
                    >
                      <FileText className="h-4 w-4 mr-1" /> View
                    </Button>
                    {quote.status === 'Accepted' && !quote.convertedToOrderId && (
                      <Button 
                        size="sm" 
                        onClick={() => handleConvert(quote.quoteId)}
                        isLoading={isConverting}
                      >
                        Convert to Order <ArrowRight className="h-3.5 w-3.5 ml-1" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {/* Quote Detail Modal (single, with actions) */}
      <Modal 
        isOpen={!!selectedQuote} 
        onClose={() => setSelectedQuote(null)}
        title={selectedQuote ? `Quote ${selectedQuote.quoteNumber}` : 'Quote'}
        size="lg"
      >
        {selectedQuote && (
          <div className="space-y-5">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div><span className="text-slate-500">Customer:</span><br /><strong>{selectedQuote.customerName}</strong></div>
              <div><span className="text-slate-500">Status:</span><br /><Badge>{selectedQuote.status}</Badge></div>
              <div><span className="text-slate-500">Quote Date:</span><br />{formatDate(selectedQuote.quoteDate)}</div>
              <div><span className="text-slate-500">Expires:</span><br />{selectedQuote.expirationDate ? formatDate(selectedQuote.expirationDate) : '—'}</div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">Line Items</h4>
                <div className="text-xs text-slate-500">{selectedQuote.details?.length || 0} lines</div>
              </div>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <tr>
                      <TableHead>Item</TableHead>
                      <TableHead className="text-right">Qty × Price</TableHead>
                      <TableHead className="text-right">Line Total</TableHead>
                    </tr>
                  </TableHeader>
                  <TableBody>
                    {(selectedQuote.details || []).map((d: any, _idx: number) => (
                      <TableRow key={_idx}>
                        <TableCell className="font-medium">{d.itemName || d.itemCode}</TableCell>
                        <TableCell className="text-right text-sm">{d.quantity} × {formatCurrency(d.unitPrice)}</TableCell>
                        <TableCell className="text-right font-medium">{formatCurrency(d.lineTotal)}</TableCell>
                      </TableRow>
                    ))}
                    {(!selectedQuote.details || selectedQuote.details.length === 0) && (
                      <TableRow><TableCell colSpan={3} className="text-center py-3 text-slate-500">No line details</TableCell></TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </div>

            <div className="bg-slate-50 rounded-lg p-4 text-sm">
              <div className="flex justify-between"><span>Subtotal</span><span className="font-medium">{formatCurrency(selectedQuote.subtotal || selectedQuote.totalAmount)}</span></div>
              {selectedQuote.discountAmount > 0 && <div className="flex justify-between text-emerald-600"><span>Discount</span><span>−{formatCurrency(selectedQuote.discountAmount)}</span></div>}
              {selectedQuote.taxAmount > 0 && <div className="flex justify-between"><span>Tax</span><span>{formatCurrency(selectedQuote.taxAmount)}</span></div>}
              <div className="flex justify-between pt-2 mt-2 border-t font-semibold text-base">
                <span>Total</span><span>{formatCurrency(selectedQuote.totalAmount)}</span>
              </div>
            </div>

            {selectedQuote.notes && <div className="text-sm"><span className="text-slate-500">Notes:</span> {selectedQuote.notes}</div>}

            {/* Workflow Actions */}
            <div className="pt-2 border-t space-y-2">
              {selectedQuote.status === 'Draft' && (
                <div className="flex gap-2">
                  <Button variant="secondary" className="flex-1" onClick={() => updateStatusMutation.mutate({ quoteId: selectedQuote.quoteId, status: 'Sent' })}>
                    Send to Customer
                  </Button>
                  <Button className="flex-1" onClick={() => updateStatusMutation.mutate({ quoteId: selectedQuote.quoteId, status: 'Accepted' })}>
                    Mark Accepted
                  </Button>
                </div>
              )}
              {selectedQuote.status === 'Sent' && (
                <div className="flex gap-2">
                  <Button variant="ghost" className="flex-1" onClick={() => updateStatusMutation.mutate({ quoteId: selectedQuote.quoteId, status: 'Declined' })}>
                    Mark Declined
                  </Button>
                  <Button className="flex-1" onClick={() => updateStatusMutation.mutate({ quoteId: selectedQuote.quoteId, status: 'Accepted' })}>
                    Accept Quote
                  </Button>
                </div>
              )}
              {selectedQuote.status === 'Accepted' && !selectedQuote.convertedToOrderId && (
                <Button className="w-full" onClick={() => handleConvert(selectedQuote.quoteId)} isLoading={isConverting}>
                  Convert to Sales Order <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              )}
              {selectedQuote.convertedToOrderId && (
                <div className="text-center text-sm text-emerald-600 font-medium">Converted to Order #{selectedQuote.convertedToOrderId}</div>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Create Quote Modal - Fully functional with searchable pickers + dynamic lines */}
      <Modal 
        isOpen={isCreateModalOpen} 
        onClose={() => { resetCreateQuoteForm(); setIsCreateModalOpen(false); }}
        title="Create New Quote"
        size="lg"
      >
        <div className="space-y-5">
          {/* Customer Picker (searchable) */}
          <div>
            <label className="text-sm font-medium mb-1 block">Customer</label>
            <div className="flex gap-2">
              <Input 
                placeholder="Search customers..." 
                value={cqCustomerSearch} 
                onChange={(e) => setCqCustomerSearch(e.target.value)} 
                className="flex-1" 
              />
              <select 
                className="border rounded-lg px-3 py-2 bg-white min-w-[260px] text-sm"
                value={cqCustomerId} 
                onChange={(e) => setCqCustomerId(e.target.value ? Number(e.target.value) : '')}
              >
                <option value="">Select customer...</option>
                {filteredCustomers.map((c: any) => (
                  <option key={c.customerId || c.CustomerID} value={c.customerId || c.CustomerID}>
                    {c.customerName || c.CustomerName} ({c.customerCode || c.CustomerCode})
                  </option>
                ))}
              </select>
            </div>
            {customers.length === 0 && <div className="text-xs text-amber-600 mt-1">Loading customers...</div>}
          </div>

          {/* Line Items */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-sm font-medium">Line Items</label>
              <span className="text-xs text-slate-500">{cqLines.length} line(s)</span>
            </div>

            {/* Current Lines */}
            {cqLines.length > 0 && (
              <div className="border rounded-lg mb-3 overflow-hidden">
                <Table>
                  <TableHeader>
                    <tr>
                      <TableHead>Item</TableHead>
                      <TableHead className="w-20">Qty</TableHead>
                      <TableHead className="w-28">Unit Price</TableHead>
                      <TableHead className="w-24 text-right">Line Total</TableHead>
                      <TableHead className="w-8"></TableHead>
                    </tr>
                  </TableHeader>
                  <TableBody>
                    {cqLines.map((ln) => {
                      const lt = ln.quantity * ln.unitPrice * (1 - (ln.discountPercent || 0) / 100);
                      return (
                        <TableRow key={ln.tempId}>
                          <TableCell className="font-medium text-sm pr-2">{ln.itemName} <span className="text-xs text-slate-400">({ln.itemCode})</span></TableCell>
                          <TableCell>
                            <Input type="number" value={ln.quantity} onChange={(e) => updateLine(ln.tempId, 'quantity', e.target.value)} className="h-8 w-20" />
                          </TableCell>
                          <TableCell>
                            <Input type="number" value={ln.unitPrice} onChange={(e) => updateLine(ln.tempId, 'unitPrice', e.target.value)} className="h-8 w-24" />
                          </TableCell>
                          <TableCell className="text-right font-medium tabular-nums">{formatCurrency(lt)}</TableCell>
                          <TableCell>
                            <button onClick={() => removeLine(ln.tempId)} className="p-1 text-slate-400 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            )}

            {/* Add Line Picker */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
              <div className="text-xs font-medium text-slate-600 mb-2">Add item to quote</div>
              <div className="flex flex-wrap gap-2 items-end">
                <div className="flex-1 min-w-[180px]">
                  <Input 
                    placeholder="Search items (FG preferred)..." 
                    value={cqItemSearch} 
                    onChange={(e) => setCqItemSearch(e.target.value)} 
                    className="h-9" 
                  />
                </div>
                <div className="min-w-[210px]">
                  <select 
                    className="w-full border rounded-lg h-9 px-2 text-sm bg-white"
                    value={cqPendingItemId} 
                    onChange={(e) => {
                      const id = e.target.value ? Number(e.target.value) : '';
                      setCqPendingItemId(id);
                      const itm = items.find((i: any) => i.itemId === id);
                      if (itm) setCqPendingPrice(itm.listPrice || itm.standardCost || 0);
                    }}
                  >
                    <option value="">Choose item...</option>
                    {filteredItemsForPicker.slice(0, 40).map((it: any) => (
                      <option key={it.itemId} value={it.itemId}>
                        {it.itemName} — {formatCurrency(it.listPrice || it.standardCost)} ({it.itemCode})
                      </option>
                    ))}
                  </select>
                </div>
                <Input type="number" value={cqPendingQty} onChange={(e) => setCqPendingQty(Math.max(1, Number(e.target.value)))} className="w-20 h-9" placeholder="Qty" />
                <Input type="number" value={cqPendingPrice} onChange={(e) => setCqPendingPrice(Number(e.target.value))} className="w-24 h-9" placeholder="Price" />
                <Button onClick={addLineFromPicker} disabled={!cqPendingItemId} size="sm" className="h-9">Add Line</Button>
              </div>
              <div className="text-[10px] text-slate-500 mt-1.5">Tip: Filter by typing in the search box above the dropdown. Finished Goods shown first.</div>
            </div>
          </div>

          {/* Totals + Adjustments */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            <div className="space-y-3 text-sm">
              <div>
                <label className="text-xs text-slate-500">Discount Amount ($)</label>
                <Input type="number" value={cqDiscount} onChange={(e) => setCqDiscount(Math.max(0, Number(e.target.value)))} className="mt-1" />
              </div>
              <div>
                <label className="text-xs text-slate-500">Shipping ($)</label>
                <Input type="number" value={cqShipping} onChange={(e) => setCqShipping(Math.max(0, Number(e.target.value)))} className="mt-1" />
              </div>
              <div>
                <label className="text-xs text-slate-500">Tax Rate</label>
                <div className="flex items-center gap-2 mt-1">
                  <Input type="number" step="0.01" value={cqTaxRate} onChange={(e) => setCqTaxRate(Math.max(0, Math.min(0.3, Number(e.target.value))))} className="w-24" />
                  <span className="text-slate-500">({(cqTaxRate * 100).toFixed(0)}%)</span>
                </div>
              </div>
            </div>

            <div className="bg-white border rounded-xl p-4 text-sm space-y-1 self-start">
              <div className="flex justify-between"><span>Subtotal</span><span className="font-medium">{formatCurrency(createCalc.subtotal)}</span></div>
              <div className="flex justify-between text-emerald-600"><span>Discount</span><span>−{formatCurrency(createCalc.discount)}</span></div>
              <div className="flex justify-between"><span>Tax</span><span>{formatCurrency(createCalc.tax)}</span></div>
              <div className="flex justify-between"><span>Shipping</span><span>{formatCurrency(createCalc.shipping)}</span></div>
              <div className="pt-2 mt-1 border-t flex justify-between font-semibold text-lg">
                <span>Total</span><span>{formatCurrency(createCalc.total)}</span>
              </div>
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-500">Internal Notes (optional)</label>
            <Input value={cqNotes} onChange={(e) => setCqNotes(e.target.value)} placeholder="Volume pricing, special terms..." className="mt-1" />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-3 border-t">
            <Button variant="secondary" onClick={() => { resetCreateQuoteForm(); setIsCreateModalOpen(false); }} className="flex-1">
              Cancel
            </Button>
            <Button 
              onClick={handleCreateQuote} 
              disabled={createQuoteMutation.isPending || !cqCustomerId || cqLines.length === 0}
              className="flex-1"
            >
              {createQuoteMutation.isPending ? 'Creating...' : 'Create Quote'}
            </Button>
          </div>
          <div className="text-[10px] text-center text-slate-500 -mt-1">Quote will be created in Draft status. Use the detail view to change status or convert.</div>
        </div>
      </Modal>
    </div>
  );
}
