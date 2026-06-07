// ── FRONTEND ── service + symptom + Memory ON/OFF toggle + Diagnose btn
// The toggle is the highest-scoring 60 seconds (§13.7): OFF = raw baseline,
// ON = cited agent diagnosis. Wire it before anything else.
'use client';

import { useState } from 'react';
import type { IncidentInput } from '../lib/types';

interface Props {
  onDiagnose: (input: IncidentInput, useMemory: boolean) => void;
  loading: boolean;
}

export function IncidentForm({ onDiagnose, loading }: Props) {
  const [service, setService] = useState('Auth Service');
  const [symptom, setSymptom] = useState('');
  const [useMemory, setUseMemory] = useState(true);

  return (
    <form
      className="card"
      style={{ display: 'grid', gap: 12 }}
      onSubmit={(e) => {
        e.preventDefault();
        onDiagnose({ service, symptom }, useMemory);
      }}
    >
      <input value={service} onChange={(e) => setService(e.target.value)} placeholder="Service" />
      <textarea
        value={symptom}
        onChange={(e) => setSymptom(e.target.value)}
        placeholder="Symptom (e.g. login 429 cascade during a surge)"
        rows={3}
      />
      <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <input type="checkbox" checked={useMemory} onChange={(e) => setUseMemory(e.target.checked)} />
        Memory {useMemory ? 'ON' : 'OFF'}
      </label>
      <button type="submit" disabled={loading || !symptom}>
        {loading ? 'Diagnosing…' : 'Diagnose'}
      </button>
    </form>
  );
}
