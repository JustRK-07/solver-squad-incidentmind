// ── FRONTEND ── "why this matched" detail card (Part II §3)
// Shows the single top match by default; clicking a recall row swaps it.
'use client';

export interface WhyMatchedProps {
  incidentId: string;
  similarityPct: number;
  rootCause: string;
  resolution: string;
  mttrLabel: string;
}

export function WhyMatchedCard({
  incidentId,
  similarityPct,
  rootCause,
  resolution,
  mttrLabel,
}: WhyMatchedProps) {
  return (
    <section className="card" style={{ display: 'grid', gap: 6 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between' }}>
        <strong style={{ fontWeight: 500 }}>{incidentId} · why this matched</strong>
        <span className="pill">{similarityPct}% similar</span>
      </header>
      <p style={{ margin: 0 }}><span style={{ color: 'var(--muted)' }}>Root cause:</span> {rootCause}</p>
      <p style={{ margin: 0 }}>
        <span style={{ color: 'var(--muted)' }}>Resolution:</span> {resolution} ({mttrLabel})
      </p>
    </section>
  );
}
