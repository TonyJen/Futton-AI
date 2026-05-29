import { AlertTriangle, Loader2 } from 'lucide-react';

import { Button } from '@/components/ui/Button';

interface LoadingStateProps {
  title?: string;
  description?: string;
}

interface ErrorStateProps extends LoadingStateProps {
  actionLabel?: string;
  onRetry?: () => void;
}

export function PageLoadingState({
  title = 'Loading data',
  description = 'Please wait while the latest information is loaded.',
}: LoadingStateProps) {
  return (
    <div className="mt-8 rounded-xl border border-slate-200 bg-white p-10 text-center shadow-soft">
      <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary-600" />
      <h2 className="mt-4 text-lg font-semibold text-slate-900">{title}</h2>
      <p className="mt-2 text-sm text-slate-600">{description}</p>
    </div>
  );
}

export function PageErrorState({
  title = 'Unable to load this page',
  description = 'Try again in a moment. If the problem continues, check the backend and runtime monitoring output.',
  actionLabel = 'Retry',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="mt-8 rounded-xl border border-rose-200 bg-rose-50 p-10 text-center shadow-soft">
      <AlertTriangle className="mx-auto h-8 w-8 text-rose-600" />
      <h2 className="mt-4 text-lg font-semibold text-rose-950">{title}</h2>
      <p className="mt-2 text-sm text-rose-700">{description}</p>
      {onRetry && (
        <Button className="mt-4" variant="outline" onClick={onRetry}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
