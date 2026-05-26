import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSalesSummary } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency } from '@/lib/utils';

export default function Sales() {
  const { data: summary } = useQuery({
    queryKey: ['sales-summary'],
    queryFn: getSalesSummary,
  });

  const sampleOrders = [
    { id: 'SO-8921', customer: 'West Elm Retail', channel: 'Wholesale', amount: 18420, status: 'Shipped', date: 'May 24' },
    { id: 'SO-8924', customer: 'Direct — Sarah K.', channel: 'Online', amount: 918, status: 'Processing', date: 'May 25' },
    { id: 'SO-8917', customer: 'Restoration Hardware', channel: 'Wholesale', amount: 67240, status: 'Shipped', date: 'May 23' },
    { id: 'QT-441', customer: 'Urban Outfitters', channel: 'Retail', amount: 24400, status: 'Quoted', date: 'May 22' },
  ];

  return (
    <div>
      <Header title="Sales Operations" subtitle="Multi-channel pipeline & order management" />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card><CardContent className="pt-6"><div className="text-xs text-slate-500">MTD Revenue</div><div className="text-4xl font-semibold tracking-tighter mt-1">{formatCurrency(summary?.totalRevenueMTD ?? 847650)}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-slate-500">Orders MTD</div><div className="text-4xl font-semibold tracking-tighter mt-1">{summary?.ordersMTD ?? 184}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-slate-500">Avg Order Value</div><div className="text-4xl font-semibold tracking-tighter mt-1">{formatCurrency(summary?.avgOrderValue ?? 4607)}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-slate-500">Open Quotes</div><div className="text-4xl font-semibold tracking-tighter mt-1">{summary?.openQuotes ?? 27}</div></CardContent></Card>
      </div>

      <div className="flex justify-between mb-3">
        <h3 className="font-semibold text-lg tracking-tight">Recent Orders &amp; Quotes</h3>
        <Button variant="secondary" size="sm">+ New Quote</Button>
      </div>

      <Table>
        <TableHeader>
          <tr>
            <TableHead>Order / Quote #</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead>Channel</TableHead>
            <TableHead className="text-right">Amount</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Date</TableHead>
            <TableHead></TableHead>
          </tr>
        </TableHeader>
        <TableBody>
          {sampleOrders.map((o, i) => (
            <TableRow key={i}>
              <TableCell className="font-semibold font-mono">{o.id}</TableCell>
              <TableCell>{o.customer}</TableCell>
              <TableCell><Badge variant="neutral">{o.channel}</Badge></TableCell>
              <TableCell className="text-right font-semibold">{formatCurrency(o.amount)}</TableCell>
              <TableCell><Badge variant={o.status === 'Shipped' ? 'success' : 'warning'}>{o.status}</Badge></TableCell>
              <TableCell>{o.date}</TableCell>
              <TableCell className="text-right"><Button size="sm" variant="ghost">View</Button></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div className="mt-8 text-xs text-center text-slate-500">
        Full sales + CRM features (quotes, returns, commissions) coming in Phase 2.
      </div>
    </div>
  );
}
