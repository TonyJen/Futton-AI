import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getDashboardKpis, getInventoryDistribution, getProductionTrend, 
  getWorkCenterUtilization, getRecommendations, approveRecommendation, rejectRecommendation 
} from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { KpiCard } from '@/components/manufacturing/KpiCard';
import { RecommendationCard } from '@/components/manufacturing/RecommendationCard';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { 
  Package, DollarSign, Factory, AlertTriangle, TrendingUp, Users, Bot 
} from 'lucide-react';
import { formatCurrency } from '@/lib/utils';
import { toast } from 'sonner';

export default function Dashboard() {
  const queryClient = useQueryClient();
  const [processingId, setProcessingId] = useState<number | null>(null);

  const { data: kpis } = useQuery({
    queryKey: ['dashboard-kpis'],
    queryFn: getDashboardKpis,
  });

  const { data: inventoryDist = [] } = useQuery({
    queryKey: ['inventory-dist'],
    queryFn: getInventoryDistribution,
  });

  const { data: productionTrend = [] } = useQuery({
    queryKey: ['production-trend'],
    queryFn: getProductionTrend,
  });

  const { data: workCenters = [] } = useQuery({
    queryKey: ['workcenter-util'],
    queryFn: getWorkCenterUtilization,
  });

  const { data: recommendations = [] } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => getRecommendations(),
  });

  const pendingRecs = recommendations.filter(r => r.status === 'PENDING');

  const approveMutation = useMutation({
    mutationFn: approveRecommendation,
    onMutate: (id) => setProcessingId(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-kpis'] });
      toast.success('Recommendation approved and action executed', {
        description: 'The system has been updated accordingly.',
      });
    },
    onError: () => toast.error('Failed to approve recommendation'),
    onSettled: () => setProcessingId(null),
  });

  const rejectMutation = useMutation({
    mutationFn: rejectRecommendation,
    onMutate: (id) => setProcessingId(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      toast.info('Recommendation rejected');
    },
    onSettled: () => setProcessingId(null),
  });

  const handleApprove = (id: number) => approveMutation.mutate(id);
  const handleReject = (id: number) => rejectMutation.mutate(id);

  return (
    <div>
      <Header 
        title="Executive Dashboard" 
        subtitle="Real-time manufacturing operations & AI recommendations"
        actions={
          <Button variant="secondary" size="sm" onClick={() => window.location.reload()}>
            <Bot className="h-4 w-4 mr-2" /> Refresh All Agents
          </Button>
        }
      />

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-8 gap-4 mb-8">
        <KpiCard 
          label="Total SKUs" 
          value={kpis?.totalSkus ?? 87} 
          change="+3 this week" 
          changeType="positive"
          icon={<Package className="h-5 w-5" />} 
        />
        <KpiCard 
          label="Inventory Value" 
          value={kpis ? formatCurrency(kpis.totalInventoryValue) : '$1.25M'} 
          change="−1.8% MoM" 
          icon={<DollarSign className="h-5 w-5" />} 
        />
        <KpiCard 
          label="Open Production Orders" 
          value={kpis?.openProductionOrders ?? 3} 
          change="2 high priority"
          icon={<Factory className="h-5 w-5" />} 
        />
        <KpiCard 
          label="Low Stock Alerts" 
          value={kpis?.lowStockItems ?? 7} 
          changeType="negative"
          icon={<AlertTriangle className="h-5 w-5" />} 
        />
        <KpiCard 
          label="On-Time Delivery" 
          value={kpis?.avgOnTimeDelivery ?? 94} 
          suffix="%" 
          change="+2.4 pts"
          changeType="positive"
          icon={<TrendingUp className="h-5 w-5" />} 
        />
        <KpiCard 
          label="Active Work Centers" 
          value={kpis?.activeWorkCenters ?? 4} 
          icon={<Users className="h-5 w-5" />} 
        />
        <KpiCard 
          label="AI Recommendations" 
          value={kpis?.pendingRecommendations ?? 3} 
          change="Pending review"
          icon={<Bot className="h-5 w-5" />} 
        />
        <KpiCard 
          label="Material Shortages" 
          value={kpis?.totalShortages ?? 2} 
          changeType="negative"
          icon={<AlertTriangle className="h-5 w-5" />} 
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-5 mb-8">
        {/* Production Trend */}
        <Card className="xl:col-span-3">
          <CardHeader>
            <CardTitle>Production Throughput — Last 7 Days</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-72 -mx-1">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={productionTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#64748b' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="planned" stroke="#94a3b8" strokeWidth={2} name="Planned" dot={false} />
                  <Line type="monotone" dataKey="completed" stroke="#6366f1" strokeWidth={3} name="Completed" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Inventory Distribution */}
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Inventory Value by Category</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-72 flex items-center justify-center -mx-4">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={inventoryDist}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="46%"
                    innerRadius={68}
                    outerRadius={108}
                    paddingAngle={2}
                  >
                    {inventoryDist.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(val) => formatCurrency(val as number)} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs mt-1 pl-2">
              {inventoryDist.map((entry, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ background: entry.fill }} />
                  <span className="text-slate-600">{entry.name}</span>
                  <span className="font-mono tabular-nums ml-auto text-slate-800 font-medium">{formatCurrency(entry.value)}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Work Center Utilization + AI Recommendations */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-5">
        {/* Utilization bars */}
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Work Center Utilization</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 pt-2">
            {workCenters.map((wc: any, idx: number) => (
              <div key={idx}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-semibold text-slate-800">{wc.name}</span>
                  <span className="font-mono text-primary-700 font-semibold">{wc.utilization}%</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div 
                    className="h-2 bg-primary-600 rounded-full transition-all" 
                    style={{ width: `${wc.utilization}%` }} 
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* AI Recommended Actions - THE STAR */}
        <Card className="xl:col-span-3 ai-section border-primary-200">
          <div className="flex items-center justify-between mb-5">
            <div>
              <div className="flex items-center gap-3">
                <Bot className="h-6 w-6 text-primary-600" />
                <h3 className="font-semibold text-xl tracking-tighter text-slate-900">AI Recommended Actions</h3>
              </div>
              <p className="text-sm text-primary-700 mt-1">
                {pendingRecs.length} pending proposals • Human approval required
              </p>
            </div>
            <Badge variant="info">{pendingRecs.length} READY</Badge>
          </div>

          <div className="space-y-3">
            {pendingRecs.length > 0 ? (
              pendingRecs.slice(0, 3).map(rec => (
                <RecommendationCard
                  key={rec.id}
                  rec={rec}
                  onApprove={handleApprove}
                  onReject={handleReject}
                  isProcessing={processingId === rec.id}
                />
              ))
            ) : (
              <div className="text-center py-8 text-sm text-slate-500">
                No pending recommendations. All agents are up to date.
              </div>
            )}
            {recommendations.length > 3 && (
              <div className="pt-1 text-center">
                <Button variant="ghost" size="sm" onClick={() => window.location.href = '/agents'}>
                  View full approval queue in AI Hub →
                </Button>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
