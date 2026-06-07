// ── FRONTEND ── GRR-style agent flow card (BUILD_PLAN.md Part II §3)
// `Recall — searched incident memory · 4 results · ✓` — expandable to payload.
// HONESTY GUARD (§8): status + resultCount come from the live flow record,
// never hardcoded in JSX.
'use client';

import { useState } from 'react';
import type { AgentFlow, FlowStatus } from '../lib/types';

const statusIcon: Record<FlowStatus, string> = {
  pending: '◌',
  running: '◍',
  success: '✓',
  error: '⚠',
};

const statusColor: Record<FlowStatus, string> = {
  pending: 'var(--muted)',
  running: 'var(--info)',
  success: 'var(--success-fg)',
  error: 'var(--danger-fg)',
};

export function FlowCard({ flow, defaultExpanded = false }: { flow: AgentFlow; defaultExpanded?: boolean }) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  return (
    <div className="card" style={{ padding: 12 }}>
      <button
        onClick={() => setExpanded((v) => !v)}
        style={{ all: 'unset', cursor: 'pointer', display: 'flex', width: '100%', gap: 8, alignItems: 'center' }}
      >
        <span style={{ color: statusColor[flow.status] }}>{statusIcon[flow.status]}</span>
        <span style={{ flex: 1 }}>{flow.label}</span>
        <span style={{ color: 'var(--muted)', fontSize: 13 }}>{flow.resultCount} results</span>
        <span style={{ color: 'var(--muted)' }}>{expanded ? '▾' : '▸'}</span>
      </button>
      {expanded && (
        // B1: raw flow payload (expand to JSON) — signals depth + honesty.
        <pre style={{ marginTop: 8, fontSize: 12, overflow: 'auto', color: 'var(--muted)' }}>
          {JSON.stringify(flow.payload, null, 2)}
        </pre>
      )}
    </div>
  );
}
