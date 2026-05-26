import React from 'react';
import { AgentRecommendation } from '@/lib/types';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { formatCurrency, formatDateTime } from '@/lib/utils';
import { Check, X, TrendingUp } from 'lucide-react';

interface RecommendationCardProps {
  rec: AgentRecommendation;
  onApprove: (id: number) => void;
  onReject: (id: number) => void;
  isProcessing?: boolean;
}

export function RecommendationCard({ rec, onApprove, onReject, isProcessing }: RecommendationCardProps) {
  const isPending = rec.status === 'PENDING';

  return (
    <div className="recommendation-card">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="info">{rec.agentName.split(' ')[0]}</Badge>
            <span className="text-xs text-slate-500">{formatDateTime(rec.createdAt)}</span>
          </div>
          <h4 className="font-semibold text-base text-slate-900 mt-1.5 tracking-tight leading-tight">{rec.title}</h4>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-xs text-emerald-700 font-semibold flex items-center justify-end gap-1">
            <TrendingUp className="h-3 w-3" /> {rec.confidence}% confidence
          </div>
        </div>
      </div>

      <p className="text-sm text-slate-600 leading-snug mt-1">{rec.description}</p>

      <div className="flex items-center justify-between pt-3 border-t mt-auto">
        <div>
          <span className="text-xs text-slate-500">Impact</span>
          <div className="font-medium text-sm text-slate-800">{rec.impact}</div>
          {rec.estimatedSavings && (
            <div className="text-emerald-700 text-xs font-semibold mt-0.5">
              Est. {formatCurrency(rec.estimatedSavings)} savings
            </div>
          )}
        </div>

        {isPending ? (
          <div className="flex gap-2">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => onReject(rec.id)}
              disabled={isProcessing}
            >
              <X className="h-3.5 w-3.5 mr-1" /> Reject
            </Button>
            <Button 
              size="sm" 
              onClick={() => onApprove(rec.id)}
              isLoading={isProcessing}
            >
              <Check className="h-3.5 w-3.5 mr-1" /> Approve & Execute
            </Button>
          </div>
        ) : (
          <Badge variant={rec.status === 'APPROVED' ? 'success' : 'danger'}>
            {rec.status}
          </Badge>
        )}
      </div>
    </div>
  );
}
