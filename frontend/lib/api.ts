// ── FRONTEND ── fetch wrappers → backend (BUILD_PLAN.md §3)
// The ONLY module the UI uses to reach the backend. No business logic here —
// just typed HTTP calls. Components import these, never call fetch directly.
// -----------------------------------------------------------------------------

import type {
  DiagnosisResult,
  IncidentInput,
  ObservationView,
  OutcomeReport,
} from './types';

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? '';

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

/** POST /api/diagnose — useMemory=false is the dumb baseline control (the toggle). */
export function diagnose(
  input: IncidentInput,
  useMemory: boolean,
): Promise<DiagnosisResult> {
  return post<DiagnosisResult>('/api/diagnose', { input, useMemory });
}

/** POST /api/outcome — report a fix outcome → retained as an Experience Fact. */
export function reportOutcome(report: OutcomeReport): Promise<{ ok: boolean }> {
  return post('/api/outcome', { outcomeReport: report });
}

/** GET /api/memory?pattern=… — drives the freshness panel + MTTR trend. */
export async function getMemory(pattern: string): Promise<ObservationView> {
  const res = await fetch(`${BASE}/api/memory?pattern=${encodeURIComponent(pattern)}`);
  if (!res.ok) throw new Error(`GET /api/memory → ${res.status}`);
  return res.json() as Promise<ObservationView>;
}
