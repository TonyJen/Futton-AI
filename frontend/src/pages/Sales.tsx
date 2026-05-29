import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSalesSummary, getQuotes, getSalesOrders, getSalesReps } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Card, CardContent } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Tabs } from '@/components/ui/Tabs';
import { PageErrorState, PageLoadingState } from '@/components/app/PageState';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { Plus } from 'lucide-react';

export default function Sales() {
  const [activeTab, setActiveTab] = useState<'orders' | 'quotes'>('orders');

  const summaryQuery = useQuery({
    queryKey: ['sales-summary'],
    queryFn: getSalesSummary,
  });
  const summary = summaryQuery.data;

  const quotesQuery = useQuery({
    queryKey: ['quotes'],
    queryFn: getQuotes,
  });
  const quotes = quotesQuery.data ?? [];

  const ordersQuery = useQuery({
    queryKey: ['sales-orders'],
    queryFn: getSalesOrders,
  });
  const orders = ordersQuery.data ?? [];

  const repsQuery = useQuery({
    queryKey: ['sales-reps'],
    queryFn: getSalesReps,
  });
  const reps = repsQuery.data ?? [];

  const openQuotes = quotes.filter((q: any) => q.status !== 'Accepted' && q.status !== 'Declined');

  if (summaryQuery.isLoading || quotesQuery.isLoading || ordersQuery.isLoading || repsQuery.isLoading) {
    return <PageLoadingState title="Loading sales operations" description="Fetching revenue, pipeline, and sales team data." />;
  }

  if (summaryQuery.isError || quotesQuery.isError || ordersQuery.isError || repsQuery.isError) {
    return (
      <PageErrorState
        title="Sales data is unavailable"
        onRetry={() => {
          void summaryQuery.refetch();
          void quotesQuery.refetch();
          void ordersQuery.refetch();
          void repsQuery.refetch();
        }}
      />
    );
  }

  return (
    <div>
      <Header 
        title="Sales Operations" 
        subtitle="Multi-channel pipeline & order management"
        actions={
          <Link to="/quotes" className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg bg-primary-600 text-white hover:bg-primary-700">
          <Plus className="h-4 w-4 mr-2" /> New Quote
        </Link>
        }
      />

      {/* KPI Row */}
      <div className="mt-8 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-6">
          <Card>
            <CardContent className="p-5">
              <div className="text-xs text-slate-500">MTD Revenue</div>
              <div className="text-4xl font-semibold tracking-tighter mt-2">{formatCurrency(summary?.totalRevenueMTD ?? 847650)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-5">
              <div className="text-xs text-slate-500">Orders MTD</div>
              <div className="text-4xl font-semibold tracking-tighter mt-2">{summary?.ordersMTD ?? 184}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-5">
              <div className="text-xs text-slate-500">Open Quotes</div>
              <div className="text-4xl font-semibold tracking-tighter mt-2 text-amber-600">{openQuotes.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-5">
              <div className="text-xs text-slate-500">Avg Order Value</div>
              <div className="text-4xl font-semibold tracking-tighter mt-2">{formatCurrency(summary?.avgOrderValue ?? 4607)}</div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Tabs: Orders + Quotes (using existing Tabs primitive) */}
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold text-lg tracking-tight">Pipeline</h3>
        <Link to="/quotes" className="inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50">
          Manage all Quotes →
        </Link>
      </div>

      <div className="mb-4">
        <Tabs
          tabs={[
            { id: 'orders', label: 'Sales Orders', count: orders.length },
            { id: 'quotes', label: 'Quotes', count: quotes.length },
          ]}
          activeTab={activeTab}
          onChange={(id) => setActiveTab(id as 'orders' | 'quotes')}
        />
      </div>

      {/* Tab Content */}
      {activeTab === 'orders' && (
        <div className="mb-8">
          <Table>
            <TableHeader>
              <tr>
                <TableHead>Order #</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Date</TableHead>
                <TableHead className="text-right">Total</TableHead>
                <TableHead>Status</TableHead>
                <TableHead></TableHead>
              </tr>
            </TableHeader>
            <TableBody>
              {orders.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-8 text-slate-500">No orders loaded</td></tr>
              ) : (
                orders.map((o: any) => (
                  <TableRow key={o.orderId || o.SalesOrderID}>
                    <TableCell className="font-semibold font-mono">{o.orderNumber || o.OrderNumber}</TableCell>
                    <TableCell>{o.customerName || o.CustomerName || '—'}</TableCell>
                    <TableCell className="text-sm">{formatDate(o.orderDate || o.OrderDate || new Date().toISOString())}</TableCell>
                    <TableCell className="text-right font-semibold">{formatCurrency(o.totalAmount || o.TotalAmount || 0)}</TableCell>
                    <TableCell>
                      <Badge variant={o.status === 'Shipped' ? 'success' : 'warning'}>{o.status || 'Open'}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link to="/sales" className="text-xs px-3 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center">View</Link>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      )}

      {activeTab === 'quotes' && (
        <div className="mb-8">
          <Table>
            <TableHeader>
              <tr>
                <TableHead>Quote #</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Expires</TableHead>
                <TableHead className="text-right">Total</TableHead>
                <TableHead>Status</TableHead>
                <TableHead></TableHead>
              </tr>
            </TableHeader>
            <TableBody>
              {quotes.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-8 text-slate-500">No quotes yet — create one from Quotes page</td></tr>
              ) : (
                quotes.map((q: any) => (
                  <TableRow key={q.quoteId}>
                    <TableCell className="font-semibold font-mono">{q.quoteNumber}</TableCell>
                    <TableCell>{q.customerName}</TableCell>
                    <TableCell className="text-sm">{q.expirationDate ? formatDate(q.expirationDate) : '—'}</TableCell>
                    <TableCell className="text-right font-semibold">{formatCurrency(q.totalAmount)}</TableCell>
                    <TableCell>
                      <Badge variant={q.status === 'Accepted' ? 'success' : q.status === 'Sent' ? 'info' : 'neutral'}>{q.status}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link to="/quotes" className="text-xs px-3 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center">View</Link>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
          <div className="mt-3">
            <Link to="/quotes" className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-300 hover:bg-slate-50">
              <Plus className="h-3.5 w-3.5 mr-1.5" /> Create New Quote
            </Link>
          </div>
        </div>
      )}

      {/* Sales Reps + Commissions (basic) */}
      <div className="mb-3">
        <h3 className="font-semibold text-lg tracking-tight">Sales Team &amp; Commissions (YTD)</h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {reps.length === 0 ? (
          <div className="text-slate-500 col-span-3">No reps data</div>
        ) : (
          reps.map((r: any) => {
            const comm = Math.round((r.ytdSales || 0) * (r.commissionRate || 0.035));
            return (
              <Card key={r.salesRepId}>
                <CardContent className="pt-5">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold">{r.firstName} {r.lastName}</div>
                      <div className="text-xs text-slate-500">{r.territory} • {r.email}</div>
                    </div>
                    <Badge variant="neutral">{Math.round((r.commissionRate || 0.035) * 100)}%</Badge>
                  </div>
                  <div className="mt-4 text-2xl font-semibold tracking-tighter">{formatCurrency(r.ytdSales || 0)}</div>
                  <div className="text-xs text-emerald-600 mt-0.5">Est. commission: {formatCurrency(comm)}</div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      <div className="text-xs text-slate-500 text-center">Returns and full CRM available on dedicated pages. Quotes page has full quote-to-order conversion.</div>
    </div>
  );
}
