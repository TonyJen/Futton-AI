import React from 'react';
import { Card } from '../ui/Card';
import { cn } from '@/lib/utils';

interface KpiCardProps {
  label: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: React.ReactNode;
  suffix?: string;
}

export function KpiCard({ label, value, change, changeType = 'neutral', icon, suffix }: KpiCardProps) {
  return (
    <Card className="kpi-card">
      <div className="flex items-start justify-between">
        <div>
          <div className="kpi-label">{label}</div>
          <div className="kpi-value mt-2">
            {value}
            {suffix && <span className="text-2xl font-medium text-slate-400 ml-0.5">{suffix}</span>}
          </div>
        </div>
        {icon && (
          <div className="text-primary-500/70 mt-1">
            {icon}
          </div>
        )}
      </div>
      {change && (
        <div className={cn(
          'text-xs font-medium mt-3 flex items-center gap-1',
          changeType === 'positive' && 'text-emerald-600',
          changeType === 'negative' && 'text-red-600',
          changeType === 'neutral' && 'text-slate-500'
        )}>
          {change}
        </div>
      )}
    </Card>
  );
}
