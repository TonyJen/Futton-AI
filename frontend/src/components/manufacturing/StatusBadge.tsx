import { Badge } from '../ui/Badge';
import { getStatusColor } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const color = getStatusColor(status) as 'success' | 'warning' | 'danger' | 'neutral';
  
  return (
    <Badge variant={color}>
      {status}
    </Badge>
  );
}
