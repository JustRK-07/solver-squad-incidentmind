// ── FRONTEND ── MTTR clock + cost counter (Recharts)
// Money + time MUST be on screen at all times (§9) — business-judge translation.
// TODO: replace placeholder math with real MTTR trend from GET /api/memory (A4),
//       and a Recharts sparkline of mttrTrend.
'use client';

import type { DiagnosisResult } from '../lib/types';

const COST_PER_MINUTE = Number(process.env.NEXT_PUBLIC_COST_PER_MINUTE ?? 500); // ₹/min downtime

export function ImpactBar({ result }: { result: DiagnosisResult | null }) {
  // Placeholder until wired to /api/memory: baseline ~240m vs recalled MTTR.
  const baselineMin = 240;
  const recalledMin = result ? 20 : baselineMin;
  const saved = Math.max(0, baselineMin - recalledMin) * COST_PER_MINUTE;

  return (
    <section
      className="card"
      style={{ display: 'flex', gap: 24, justifyContent: 'space-around' }}
    >
      <Metric label="MTTR" value={`${recalledMin}m`} />
      <Metric label="vs baseline" value={`${baselineMin}m`} />
      <Metric label="Downtime saved" value={`₹${saved.toLocaleString('en-IN')}`} />
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: 13, color: 'var(--muted)' }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 500 }}>{value}</div>
    </div>
  );
}
