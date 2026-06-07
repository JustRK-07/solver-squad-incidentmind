// ── FRONTEND ── numbered remediation steps + provenance pills (Part II §3, §6)
// PROVENANCE RULE (non-negotiable §6): pills render ONLY from real source ids.
// No step may cite an incident that was not recalled. Empty sources → no pill.
'use client';

import type { RemediationStep } from '../lib/types';

export function RecommendationCard({
  steps,
  sourceCount,
}: {
  steps: RemediationStep[];
  sourceCount: number;
}) {
  return (
    <section className="card" style={{ borderColor: 'var(--info)', borderWidth: 2, display: 'grid', gap: 10 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between' }}>
        <strong style={{ fontWeight: 500 }}>Recommended remediation</strong>
        <span className="pill">based on {sourceCount} past incidents</span>
      </header>
      <ol style={{ margin: 0, paddingLeft: 20, display: 'grid', gap: 8 }}>
        {steps.map((s) => (
          <li key={s.order}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
              <span>{s.text}</span>
              {s.sources.length > 0 && (
                <span className="pill" style={{ whiteSpace: 'nowrap' }}>
                  from {s.sources.join(' · ')}
                </span>
              )}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
