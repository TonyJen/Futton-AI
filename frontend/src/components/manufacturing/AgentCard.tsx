import { Agent } from '@/lib/types';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Play, Clock } from 'lucide-react';
import { formatDateTime } from '@/lib/utils';

interface AgentCardProps {
  agent: Agent;
  onRun: (id: number) => void;
  isRunning?: boolean;
}

export function AgentCard({ agent, onRun, isRunning }: AgentCardProps) {
  return (
    <div className="agent-card">
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-9 w-9 rounded-xl bg-primary-100 text-primary-700 flex items-center justify-center flex-shrink-0">
            <Play className="h-4 w-4" />
          </div>
          <div>
            <div className="font-semibold text-lg tracking-tighter leading-none text-slate-900 break-words">{agent.name}</div>
            <Badge variant="neutral" className="mt-1.5">{agent.category}</Badge>
          </div>
        </div>

        <p className="text-sm text-slate-600 leading-snug line-clamp-3 break-words">{agent.description}</p>
      </div>

      <div className="mt-5 pt-4 border-t flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5 text-slate-500">
          <Clock className="h-3.5 w-3.5" />
          Last run {formatDateTime(agent.lastRun)}
        </div>
        <div className="font-mono text-primary-600 font-semibold">
          {agent.recommendationsGenerated} recs
        </div>
      </div>

      <Button 
        className="mt-4 w-full" 
        onClick={() => onRun(agent.id)}
        isLoading={isRunning}
        disabled={agent.status === 'Running'}
      >
        {isRunning ? 'Running Agent...' : 'Run Agent'}
      </Button>
    </div>
  );
}
