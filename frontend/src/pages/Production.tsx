import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getProductionOrders, getWorkCenters } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { StatusBadge } from '@/components/manufacturing/StatusBadge';
import { Progress } from '@/components/ui/Progress';
import { formatDate } from '@/lib/utils';
import { Play, AlertCircle } from 'lucide-react';
import type { ProductionOrder, WorkCenter } from '@/lib/types';
import { toast } from 'sonner';

export default function Production() {
  const { data: orders = [], isLoading } = useQuery({
    queryKey: ['production-orders'],
    queryFn: () => getProductionOrders(),
  });

  const { data: workCenters = [] } = useQuery({
    queryKey: ['workcenters'],
    queryFn: getWorkCenters,
  });

  const handleAction = (order: ProductionOrder, action: string) => {
    toast.success(`${action} triggered`, {
      description: `${order.orderNumber} — ${order.itemName}. In real system this would call the backend and possibly trigger agent validation.`,
    });
  };

  return (
    <div>
      <Header title="Production Command Center" subtitle="Work orders, capacity, and material readiness" />

      {/* Work Centers */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        {workCenters.map((wc: WorkCenter) => (
          <Card key={wc.workCenterId} className="hover:shadow-card-hover transition">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{wc.name} <span className="font-mono text-xs text-slate-400">({wc.code})</span></CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline justify-between mb-2">
                <div className="text-4xl font-semibold tabular-nums tracking-[-1.5px]">{wc.currentUtilization}</div>
                <div className="text-sm text-slate-500">% utilized</div>
              </div>
              <Progress value={wc.currentUtilization} />
              <div className="flex justify-between text-xs text-slate-500 mt-3">
                <span>{wc.activeOrders} active orders</span>
                <StatusBadge status={wc.status} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Production Orders Table */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold tracking-tight text-lg">Active Production Orders</h3>
        <Button variant="secondary" size="sm">+ New Work Order</Button>
      </div>

      <Table>
        <TableHeader>
          <tr>
            <TableHead>Order #</TableHead>
            <TableHead>Item</TableHead>
            <TableHead className="text-right">Qty / Done</TableHead>
            <TableHead>Work Center</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Due</TableHead>
            <TableHead>Priority</TableHead>
            <TableHead>Materials</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </tr>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <tr><td colSpan={9} className="text-center py-9">Loading production orders...</td></tr>
          ) : orders.length === 0 ? (
            <tr><td colSpan={9} className="text-center py-9 text-slate-500">No active orders</td></tr>
          ) : (
            orders.map((order: ProductionOrder) => {
              const progress = Math.round((order.completedQty / order.quantity) * 100);
              return (
                <TableRow key={order.productionOrderId}>
                  <TableCell className="font-semibold font-mono">{order.orderNumber}</TableCell>
                  <TableCell>
                    <div>{order.itemName}</div>
                    <div className="text-xs text-slate-500">{order.itemCode}</div>
                  </TableCell>
                  <TableCell className="text-right font-semibold tabular-nums">
                    {order.completedQty} / {order.quantity}
                    <div className="mt-1 w-24 ml-auto"><Progress value={progress} /></div>
                  </TableCell>
                  <TableCell>{order.workCenter}</TableCell>
                  <TableCell><StatusBadge status={order.status} /></TableCell>
                  <TableCell className="text-sm">{formatDate(order.dueDate, 'MMM dd')}</TableCell>
                  <TableCell>
                    <Badge variant={order.priority === 'Critical' ? 'danger' : order.priority === 'High' ? 'warning' : 'neutral'}>
                      {order.priority}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {order.materialShortage ? (
                      <span className="inline-flex items-center gap-1 text-red-600 text-xs font-medium"><AlertCircle className="h-3.5 w-3.5" /> Shortage</span>
                    ) : (
                      <span className="text-emerald-600 text-xs font-medium">Ready</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex gap-1 justify-end">
                      <Button size="sm" variant="ghost" onClick={() => handleAction(order, 'Issue Materials')}>Issue</Button>
                      <Button size="sm" onClick={() => handleAction(order, 'Complete Order')}>
                        <Play className="h-3.5 w-3.5 mr-1" /> Complete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </div>
  );
}
