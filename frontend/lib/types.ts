// ── SHARED DTOs ────────────────────────────────────────────────────────────
// Source of truth for the contracts crossing the Frontend ↔ Backend boundary.
// (BUILD_PLAN.md §4). Both tiers import from here. Keep this dependency-free.
// -----------------------------------------------------------------------------

export type Outcome = 'success' | 'failure';

/** A resolved incident as stored in the seed / mirrored for the UI. */
export interface IncidentRecord {
  id: string;
  service: string;
  symptom: string;
  root_cause: string;
  fix: string;
  outcome: Outcome;
  mttr_minutes: number;
  date: string;            // ISO yyyy-mm-dd
  lesson?: string;
  tags?: string[];
  retain_text: string;     // first-person Experience Fact → fed to Hindsight retain()
}

/** Freshness trend for a recalled fix (drives the weakening beat). */
export type Freshness = 'stable' | 'strengthening' | 'weakening' | 'stale';

/** What the diagnose endpoint returns. Confidence is COMPUTED, never asked of the LLM. */
export interface DiagnosisResult {
  rootCause: string;
  recommendedFix: string;
  avoid: string[];                       // fixes that failed before (failure memory)
  supportingIncidentIds: string[];       // citations
  confidence: number;                    // 0–100, computed in backend/core/confidence.ts
  confidenceBand: 'high' | 'medium' | 'low';
  freshnessWarning: string | null;
  verified: boolean;                     // false ⇒ novel / unverified
  evidence: EvidenceItem[];
  rationale: string;
}

export interface EvidenceItem {
  incidentId: string;
  date: string;
  outcome: Outcome;
  freshness?: Freshness;
  snippet: string;
}

export interface IncidentInput {
  service: string;
  symptom: string;
}

export interface OutcomeReport {
  incidentInput: IncidentInput;
  appliedFix: string;
  outcome: Outcome;
  mttrMinutes: number;
}

// ── Part II — GRR-style flow console DTOs ─────────────────────────────────────
// The inspectable agent pipeline: Retain → Recall → Reflect → Recommend.

export type FlowKind = 'retain' | 'recall' | 'reflect' | 'recommend';
export type FlowStatus = 'pending' | 'running' | 'success' | 'error';

export interface AgentFlow {
  kind: FlowKind;
  label: string;
  status: FlowStatus;
  resultCount: number;
  payload: unknown;        // raw flow body (recall hits, reflect prompt, llm json) — honesty guard §8
}

export interface RetrievedIncident {
  id: string;
  title: string;
  similarityPct: number;   // rounded integer
  status: string;          // e.g. "resolved"
  mttrLabel: string;       // e.g. "~25m"
  freshness?: Freshness;
}

export interface RemediationStep {
  order: number;
  text: string;
  sources: string[];       // source_incident_ids — MUST be a subset of recalled ids (§6)
}

export interface ObservationView {
  pattern: string;
  successes: number;
  failures: number;
  freshness: Freshness;
  daysSinceLastEvidence: number;
  mttrTrend: number[];     // chronological MTTR for the sparkline (A4)
}
