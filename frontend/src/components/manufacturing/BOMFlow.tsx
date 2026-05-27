import React, { useCallback } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { BOMComponent } from '@/lib/types';
import { formatCurrency, formatNumber } from '@/lib/utils';

interface BOMFlowProps {
  components: BOMComponent[];
  rootItemName?: string;
  rootItemId?: number;
}

export function BOMFlow({ components, rootItemName = 'Finished Good' }: BOMFlowProps) {
  // Build a simple layered layout: root at top, then components below
  const rootNode: Node = {
    id: 'root',
    type: 'default',
    data: { label: rootItemName, isRoot: true },
    position: { x: 280, y: 20 },
    style: {
      background: '#6366f1',
      color: 'white',
      border: '2px solid #4f46e5',
      borderRadius: 12,
      padding: 12,
      fontWeight: 600,
      minWidth: 180,
    },
  };

  const compNodes: Node[] = components.map((c, idx) => ({
    id: `comp-${c.componentItemId || idx}`,
    data: {
      label: (
        <div className="text-center">
          <div className="font-semibold text-sm">{c.componentItemCode}</div>
          <div className="text-[10px] text-slate-600">{c.componentItemName}</div>
          <div className="mt-1 text-emerald-600 font-mono text-xs">
            {formatNumber(c.quantity, 1)} {c.unit}
            {c.scrapRate > 0 && <span className="text-amber-600"> (+{c.scrapRate}%)</span>}
          </div>
        </div>
      ),
    },
    position: { x: 60 + (idx % 3) * 180, y: 140 + Math.floor(idx / 3) * 95 },
    style: {
      background: '#f8fafc',
      border: '1px solid #cbd5e1',
      borderRadius: 8,
      padding: 8,
      minWidth: 160,
      fontSize: 11,
    },
  }));

  const edges: Edge[] = components.map((c, idx) => ({
    id: `e-root-${idx}`,
    source: 'root',
    target: `comp-${c.componentItemId || idx}`,
    animated: true,
    style: { stroke: '#64748b', strokeWidth: 1.5 },
    label: `L${c.level}`,
    labelStyle: { fontSize: 10, fill: '#475569' },
  }));

  const [nodes, , onNodesChange] = useNodesState([rootNode, ...compNodes]);
  const [edgesState, , onEdgesChange] = useEdgesState(edges);

  const onNodeClick = useCallback((event: any, node: any) => {
    if (node.id === 'root') {
      alert(`Root: ${rootItemName}\nTotal components: ${components.length}`);
    } else {
      const comp = components.find((c, i) => `comp-${c.componentItemId || i}` === node.id);
      if (comp) alert(`${comp.componentItemName}\nQty: ${comp.quantity} ${comp.unit}\nScrap: ${comp.scrapRate}%`);
    }
  }, [components, rootItemName]);

  if (!components.length) {
    return <div className="text-sm text-slate-500 p-8 text-center border rounded-lg">No BOM data for visualizer.</div>;
  }

  return (
    <div className="h-[420px] w-full border border-slate-200 rounded-2xl overflow-hidden bg-white">
      <ReactFlow
        nodes={nodes}
        edges={edgesState}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        attributionPosition="bottom-left"
        proOptions={{ hideAttribution: true }}
      >
        <MiniMap
          nodeColor={(node) => (node.id === 'root' ? '#6366f1' : '#94a3b8')}
          maskColor="#f1f5f9"
        />
        <Controls />
        <Background color="#e2e8f0" gap={18} />
      </ReactFlow>
      <div className="px-3 py-1 text-[10px] text-slate-400 border-t bg-slate-50 flex justify-between">
        <div>Interactive BOM • Click nodes for details • Drag to rearrange</div>
        <div>{components.length} components • Level 1–{Math.max(...components.map(c => c.level || 1))}</div>
      </div>
    </div>
  );
}
