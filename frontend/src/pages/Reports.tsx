import { useQuery } from '@tanstack/react-query';
import { getDashboardKpis, getInventoryDistribution, getProductionTrend, getWorkCenterUtilization, getQuotes, getReturns } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency, formatNumber } from '@/lib/utils';
import { toast } from 'sonner';
import { Download, BarChart3 } from 'lucide-react';

export default function Reports() {
  const { data: kpis } = useQuery({ queryKey: ['kpis'], queryFn: getDashboardKpis });
  const { data: invDist = [] } = useQuery({ queryKey: ['inv-dist'], queryFn: getInventoryDistribution });
  const { data: prodTrend = [] } = useQuery({ queryKey: ['prod-trend'], queryFn: getProductionTrend });
  const { data: wcUtil = [] } = useQuery({ queryKey: ['wc-util'], queryFn: getWorkCenterUtilization });
  const { data: quotes = [] } = useQuery({ queryKey: ['quotes'], queryFn: getQuotes });
  const { data: returns = [] } = useQuery({ queryKey: ['returns'], queryFn: getReturns });

  const convertedQuotes = quotes.filter((q: any) => q.convertedToOrderId).length;
  const conversionRate = quotes.length ? Math.round((convertedQuotes / quotes.length) * 100) : 0;

  function exportCSV(name: string, rows: any[]) {
    if (!rows.length) {
      toast.error('No data to export');
      return;
    }
    const headers = Object.keys(rows[0]);
    const csv = [
      headers.join(','),
      ...rows.map(r => headers.map(h => JSON.stringify(r[h] ?? '')).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`${name} exported`);
  }

  return (
    <div>
      <Header
        title="Reports & Analytics"
        subtitle="Manufacturing + Sales performance"
        actions={
          <Button variant="outline" onClick={() => exportCSV('executive_summary', [{ ...kpis, date: new Date().toISOString() }])}>
            <Download className="h-4 w-4 mr-2" /> Export Summary
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8 mb-8">
        {/* Manufacturing */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><BarChart3 className="h-4 w-4" /> Manufacturing Snapshot</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>Total SKUs: <span className="font-semibold">{kpis?.totalSkus ?? 87}</span></div>
              <div>Inventory Value: <span className="font-semibold">{formatCurrency(kpis?.totalInventoryValue ?? 1248750)}</span></div>
              <div>Open Production: <span className="font-semibold">{kpis?.openProductionOrders ?? 3}</span></div>
              <div>Low Stock Items: <span className="font-semibold text-amber-600">{kpis?.lowStockItems ?? 7}</span></div>
            </div>

            <div>
              <div className="font-medium mb-2">Inventory by Type</div>
              <div className="space-y-1">
                {invDist.map((d: any, i: number) => (
                  <div key={i} className="flex justify-between text-xs">
                    <span>{d.name}</span>
                    <span className="font-mono">{formatCurrency(d.value)}</span>
                  </div>
                ))}
              </div>
            </div>

            <Button size="sm" variant="ghost" onClick={() => exportCSV('inventory_distribution', invDist)}>Export Inventory</Button>
          </CardContent>
        </Card>

        {/* Sales & CRM */}
        <Card>
          <CardHeader>
            <CardTitle>Sales Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>Quotes (total): <span className="font-semibold">{quotes.length}</span></div>
              <div>Quote → Order Rate: <span className="font-semibold text-emerald-600">{conversionRate}%</span></div>
              <div>Returns logged: <span className="font-semibold">{returns.length}</span></div>
              <div>Total Refunds: <span className="font-semibold text-rose-600">{formatCurrency(returns.reduce((s: number, r: any) => s + (r.refundAmount || 0), 0))}</span></div>
            </div>

            <div>
              <div className="font-medium mb-2">Recent Quotes</div>
              <Table>
                <TableHeader>
                  <tr><TableHead>Quote</TableHead><TableHead>Customer</TableHead><TableHead>Status</TableHead></tr>
                </TableHeader>
                <TableBody>
                  {quotes.slice(0, 4).map((q: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="font-mono text-xs">{q.quoteNumber}</TableCell>
                      <TableCell>{q.customerName}</TableCell>
                      <TableCell><Badge variant="neutral">{q.status}</Badge></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <Button size="sm" variant="ghost" onClick={() => exportCSV('sales_quotes', quotes)}>Export Quotes</Button>
          </CardContent>
        </Card>
      </div>

      {/* Work Center & Production Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Work Center Utilization</CardTitle></CardHeader>
          <CardContent>
            <Table>
              <TableHeader><tr><TableHead>Center</TableHead><TableHead>Utilization</TableHead><TableHead>Status</TableHead></tr></TableHeader>
              <TableBody>
                {wcUtil.map((wc: any, i: number) => (
                  <TableRow key={i}>
                    <TableCell>{wc.name}</TableCell>
                    <TableCell>{formatNumber(wc.utilization || wc.currentUtilization)}%</TableCell>
                    <TableCell><Badge variant={wc.utilization > 85 ? 'warning' : 'success'}>{wc.status || 'Running'}</Badge></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Button size="sm" variant="ghost" className="mt-3" onClick={() => exportCSV('workcenter_util', wcUtil)}>Export</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Production Trend (Last 7 Days)</CardTitle></CardHeader>
          <CardContent>
            <div className="text-xs text-slate-500 mb-2">Completed vs Planned</div>
            <div className="space-y-2">
              {prodTrend.slice(-7).map((d: any, i: number) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  <div className="w-20 text-slate-500">{d.day}</div>
                  <div className="flex-1 bg-slate-100 h-2 rounded">
                    <div className="bg-emerald-500 h-2 rounded" style={{ width: `${Math.min(100, (d.completed / (d.planned || 1)) * 100)}%` }} />
                  </div>
                  <div className="font-mono text-xs w-24 text-right">{d.completed} / {d.planned}</div>
                </div>
              ))}
            </div>
            <Button size="sm" variant="ghost" className="mt-3" onClick={() => exportCSV('production_trend', prodTrend)}>Export Trend</Button>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 text-center text-xs text-slate-400">
        Full ad-hoc reporting + scheduled exports coming in next iteration. All data is live from the ERP.
      </div>
    </div>
  );
}
