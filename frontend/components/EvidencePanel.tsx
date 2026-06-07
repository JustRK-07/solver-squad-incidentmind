// ── FRONTEND ── cited incidents w/ date + outcome + freshness badge
// Provenance is the deliverable, not decoration (§0). Render only real citations.
'use client';

import type { EvidenceItem, Freshness } from '../lib/types';

const freshBadge: Record<Freshness, string> = {
  stable: 'var(--success-fg)',
  strengthening: 'var(--success-fg)',
  weakening: 'var(--warning-fg)',
  stale: 'var(--muted)',
};

export function EvidencePanel({ evidence }: { evidence: EvidenceItem[] }) {
  if (evidence.length === 0) return null;
  return (
    <section className="card" style={{ display: 'grid', gap: 8 }}>
      <strong style={{ fontWeight: 500 }}>Evidence</strong>
      {evidence.map((e) => (
        <div key={e.incidentId} style={{ display: 'grid', gap: 2 }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span className="pill">{e.incidentId}</span>
            <span style={{ color: 'var(--muted)', fontSize: 12 }}>{e.date}</span>
            <span style={{ fontSize: 12 }}>{e.outcome}</span>
            {e.freshness && (
              <span style={{ fontSize: 12, color: freshBadge[e.freshness] }}>{e.freshness}</span>
            )}
          </div>
          <p style={{ margin: 0, fontSize: 13 }}>{e.snippet}</p>
        </div>
      ))}
    </section>
  );
}
