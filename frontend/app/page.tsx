// ── FRONTEND ── the single screen (BUILD_PLAN.md §3 + Part II §2)
// Vertical stack, no horizontal scroll. Orchestrates the demo: incident header →
// metric cards → agent flow cards → recommendation → "why this matched".
// Keep state + wiring here; push all rendering into components/.
'use client';

import { useState } from 'react';
import { IncidentForm } from '../components/IncidentForm';
import { DiagnosisCard } from '../components/DiagnosisCard';
import { EvidencePanel } from '../components/EvidencePanel';
import { ImpactBar } from '../components/ImpactBar';
import { diagnose } from '../lib/api';
import type { DiagnosisResult, IncidentInput } from '../lib/types';

export default function Page() {
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function onDiagnose(input: IncidentInput, useMemory: boolean) {
    setLoading(true);
    try {
      setResult(await diagnose(input, useMemory));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 920, margin: '0 auto', padding: 24, display: 'grid', gap: 16 }}>
      <h1 style={{ fontSize: 20, fontWeight: 500, margin: 0 }}>IncidentMind</h1>
      <ImpactBar result={result} />
      <IncidentForm onDiagnose={onDiagnose} loading={loading} />
      {result && (
        <>
          <DiagnosisCard result={result} />
          <EvidencePanel evidence={result.evidence} />
        </>
      )}
    </main>
  );
}
