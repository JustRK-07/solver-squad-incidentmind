// ── FRONTEND ── root cause, fix, confidence band, avoid list, freshness banner
// Confidence + band come pre-computed from the backend — render, don't compute.
'use client';

import type { DiagnosisResult } from '../lib/types';

const bandColor: Record<DiagnosisResult['confidenceBand'], string> = {
  high: 'var(--success-fg)',
  medium: 'var(--warning-fg)',
  low: 'var(--danger-fg)',
};

export function DiagnosisCard({ result }: { result: DiagnosisResult }) {
  return (
    <section className="card" style={{ display: 'grid', gap: 8, borderColor: 'var(--info)' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between' }}>
        <strong style={{ fontWeight: 500 }}>Recommended remediation</strong>
        <span className="pill" style={{ color: bandColor[result.confidenceBand] }}>
          confidence {result.confidence} ({result.confidenceBand.toUpperCase()})
        </span>
      </header>

      {!result.verified && <div>⚠️ Treating as novel — UNVERIFIED.</div>}
      {result.freshnessWarning && (
        <div style={{ color: 'var(--warning-fg)' }}>⚠️ {result.freshnessWarning}</div>
      )}

      <p><span style={{ color: 'var(--muted)' }}>Root cause:</span> {result.rootCause}</p>
      <p><span style={{ color: 'var(--muted)' }}>Fix:</span> {result.recommendedFix}</p>

      {result.avoid.length > 0 && (
        <div style={{ color: 'var(--danger-fg)' }}>
          Do NOT: {result.avoid.join('; ')}
        </div>
      )}

      <footer style={{ fontSize: 12, color: 'var(--muted)' }}>
        based on {result.supportingIncidentIds.length} past incidents ·{' '}
        {result.supportingIncidentIds.join(' · ')}
      </footer>
    </section>
  );
}
