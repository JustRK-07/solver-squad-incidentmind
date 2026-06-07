// ── TypeScript data models for AfterMath ────────────────────────
// Mirrors the shape of every constant in standalone.html (Phase 1 §15).

// ── memory & freshness ──────────────────────────────────────────────
export type Freshness = "stable" | "strengthening" | "weakening" | "stale";
export type Outcome   = "success" | "failure" | "open";

// ── bank (memory bank) ──────────────────────────────────────────────
export interface BankIncident {
  id: string;
  svc: string;
  title: string;
  outcome: Outcome;
  date: string;                  // ISO yyyy-mm-dd
  mttr: number | null;           // minutes
  freshness: Freshness | null;
  status: string;                // "Degraded" | "Resolved" | …
}

export interface IncidentDetail {
  rootCause: string;
  resolution: string;
  mttr: string | null;           // human-formatted ("38m", "1h12m")
  fix: string;
  date: string;                  // human-formatted
  tags: string[];
}

// ── signals & deploys ──────────────────────────────────────────────
export type SignalLevel = "info" | "warn" | "error" | "crit";

export interface Signal {
  ts: string;                    // "06:42:01"
  level: SignalLevel;
  msg: string;
  hl?: boolean;                  // highlight: linked to root-cause hypothesis
}

export interface Deploy {
  sha: string;
  committer: string;
  time: string;
  delta: string;                 // "11 min before incident" | "3 days ago"
  desc: string;
  linked: boolean;               // highlighted in the UI as relevant
}

// ── recall & top match ─────────────────────────────────────────────
export interface RecallHit {
  id: string;
  title: string;
  sim: number;                   // 0–100
  status: "resolved" | "failed";
  mttr: string;                  // "38m" | "1h12m"
  freshness?: Freshness;
}

export interface TopMatch {
  id: string;
  sim: number;
  rootCause: string;
  resolution: string;
  mttr: string;
}

// ── scenario (the diagnosis payload) ───────────────────────────────
export interface Step {
  order: number;
  text: string;
  sources: string[];             // cited incident ids
}

export interface ScenarioHistory {
  mttr: number[];                // mttr in minutes
  labels: string[];              // incident ids in order
}

export interface Scenario {
  key: ScenarioKey;
  rootCause: string;
  recommendedFix: string;
  confidence: number;            // 0–100
  confidenceBand: "high" | "medium" | "low";
  freshnessWarning: string | null;
  avoid: string[];
  citations: string[];
  verified: boolean;
  mttr: number;                  // minutes
  rationale: string;
  steps: Step[];
  retrieved: RecallHit[];
  top: TopMatch | null;
  history: ScenarioHistory;
}

// ── scenario keys (the lookup table) ───────────────────────────────
export type ScenarioKey =
  | "payments5xx"
  | "auth429"
  | "oom"
  | "tls"
  | "stale"
  | "baseline";

// ── agent flow (Retain / Recall / Reflect) ─────────────────────────
export type FlowKind = "retain" | "recall" | "reflect";

export interface Flow {
  kind: FlowKind;
  name: "Retain" | "Recall" | "Reflect";
  desc: string;
  resultCount: number;
  resultLabel: string;
  expanded: boolean;
  ts: number;                    // millisecond epoch (Date.now())
  body: unknown;                 // shape varies by kind — typed below
}

export interface RetainBody {
  signals: Array<{ service: string; ts: string; note: string }>;
}
export interface RetainSkippedBody { note: "memory OFF — no retention performed" }

export interface RecallBody { hits: RecallHit[] }
export interface RecallSkippedBody { note: "memory OFF — no retrieval performed" }

export interface ReflectBody {
  hypothesis: string;
  confidence: number;
  band: "high" | "medium" | "low";
  citations: string[];
}
export interface ReflectRawBody {
  prompt: string;
  response: string;
  citations: string[];
}

// ── agent status (the diagnosis pipeline) ──────────────────────────
export type DiagnosisStatus = "idle" | "running" | "done";

// ── outcome (DARC loop closure) ─────────────────────────────────────
export interface OutcomeReport {
  incidentInput: { service: string; symptom: string };
  appliedFix: string;
  outcome: "success" | "failure";
  mttrMinutes: number;
}

// ── what the diagnose form captures ─────────────────────────────────
export interface DiagnoseInput {
  service: string;
  symptom: string;
  useMemory: boolean;
}
