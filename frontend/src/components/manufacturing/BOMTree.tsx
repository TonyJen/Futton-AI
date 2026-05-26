import React from 'react';
import { BOMComponent } from '@/lib/types';
import { formatNumber } from '@/lib/utils';
import { ChevronRight } from 'lucide-react';

interface BOMTreeProps {
  components: BOMComponent[];
  rootItemName?: string;
}

export function BOMTree({ components, rootItemName }: BOMTreeProps) {
  if (!components.length) {
    return <div className="text-sm text-slate-500 py-4">No BOM defined for this item.</div>;
  }

  return (
    <div>
      {rootItemName && (
        <div className="text-sm font-semibold text-slate-500 mb-3 flex items-center gap-2">
          <ChevronRight className="h-3.5 w-3.5" /> {rootItemName} — Bill of Materials
        </div>
      )}
      <div className="space-y-1 font-mono text-xs">
        {components.map((comp, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 hover:bg-white transition"
          >
            <div className="flex items-center gap-3">
              <div className="text-primary-600 font-bold tracking-[1px] w-14">L{comp.level}</div>
              <div>
                <div className="font-semibold text-slate-900 tracking-tight">{comp.componentItemCode}</div>
                <div className="text-slate-600 text-[13px]">{comp.componentItemName}</div>
              </div>
            </div>
            <div className="text-right tabular-nums">
              <div className="font-semibold text-slate-900">
                {formatNumber(comp.quantity, 2)} {comp.unit}
              </div>
              {comp.scrapRate > 0 && (
                <div className="text-[10px] text-amber-600">+{comp.scrapRate}% scrap</div>
              )}
            </div>
          </div>
        ))}
      </div>
      <div className="text-[10px] text-slate-400 mt-3 pl-1">
        Total components shown: {components.length}
      </div>
    </div>
  );
}
