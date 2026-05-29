import { cn } from '@/lib/utils';

interface ProgressProps {
  value: number; // 0-100
  className?: string;
  color?: string;
}

export function Progress({ value, className, color = 'bg-primary-600' }: ProgressProps) {
  const clamped = Math.min(100, Math.max(0, value));
  return (
    <div className={cn('progress', className)}>
      <div
        className={cn('progress-bar', color)}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}
