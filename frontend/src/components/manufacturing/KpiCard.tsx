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
          <div className="kpi-value mt-1.5">
            {value}
            {suffix && <span className="text-2xl font-medium text-slate-400 ml-0.5">{suffix}</span>}
          </div>
        </div>
        {icon && (
          <div className="text-primary-600 flex-shrink-0 mt-0.5">
            {React.cloneElement(icon as React.ReactElement<any>, { 
              className: "h-5 w-5" 
            })}
          </div>
        )}
      </div>
      {change && (
        <div className={cn(
          'text-[10px] font-medium mt-1 flex items-center gap-1',
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
