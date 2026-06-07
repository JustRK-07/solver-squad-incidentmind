# Aftermath / IncidentMind — Architecture & Integration Plan

**One consolidated plan distilled from:** `aftermath-project-brief.md`, `aftermath-solution.md`, `aftermath-seed.json`, `Hackathon_Guide.md`, `README.md`.

> **What we're building:** An on-call SRE agent that *learns* from every outage. It remembers past incidents, proposes evidence-cited mitigations with a real confidence score, remembers its own failures, flags decaying fixes ("weakening"), and gets visibly faster with each incident. **Memory is the product, not a feature.**

> **The core loop (DARC):** Diagnose → Act → Record → Consolidate → (next incident is sharper).

---

## 0. North Star & Non-Negotiables

| Must-have (protect at all costs) | Cut without mercy |
|---|---|
| Closed learning loop, live on stage | Auth / login |
| Failure memory (agent avoids a fix that backfired) | Multi-tenant |
| Weakening / freshness trend visible | Real monitoring / Slack integrations |
| Memory **ON/OFF toggle** (before/after in 60s) | Custom graph DB |
| MTTR clock + cost counter always on screen | Custom causal-graph engine |
| Rehearsed narration | Browser storage / persistence beyond Hindsight |

**Judging reality:** 25% of score is "does memory *visibly* make the agent better in 3 minutes." Build the demo, not the platform. **Fake the infrastructure, make the learning real.**

---

## 1. Tech Stack (locked)

| Layer | Choice | Notes |
|---|---|---|
| Memory (mandatory) | **Hindsight** | Cloud (promo `MEMHACK6` → $50 credits) or Docker self-host as backup. Provides `retain` / `recall` / `reflect` + auto-consolidation + freshness. |
| **Agent host** | **OpenClaw** + official **Hindsight plugin** | The diagnosis agent runs inside OpenClaw; the Hindsight plugin wires memory (`retain`/`recall`/`reflect`) into the agent natively. See `hindsight.vectorize.io/sdks/integrations/openclaw`. |
| Reasoning LLM | **OpenAI** — `gpt-4o` (primary), `gpt-4o-mini` (fallback) | Configured as the OpenClaw agent's model + Hindsight reflect model. Strong function-calling + structured outputs. Retry → fallback on errors. |
| Frontend | **Next.js (App Router) + TypeScript** | Single-screen UI; talks to the backend over HTTP/JSON only. |
| Backend | **Next.js API routes (or a thin Node service)** | Orchestration layer: receives UI requests, calls the OpenClaw agent + Hindsight, computes confidence, returns `DiagnosisResult`. |
| Hindsight client | **Hindsight TypeScript SDK** (`/sdks/nodejs`) | Used by the OpenClaw plugin + our adapter; wrapped behind one interface. |
| UI | **Tailwind CSS** + **Recharts** | MTTR/cost counters, freshness viz. |
| Deploy | **Vercel** (frontend + API) · OpenClaw agent hosted separately | One-command for the web app. Keep local backups running. |
| Seed data | `aftermath-seed.json` (already written ✅) | 11 incidents, 5 types. This IS the demo backbone. |

---

## 2. Architecture (three tiers: Frontend · Backend · API Integration)

```
┌─ FRONTEND (Next.js UI) ──────────────────────────────────────────────┐
│  IncidentForm (+ Memory ON/OFF toggle) · DiagnosisCard · EvidencePanel │
│  ImpactBar (MTTR clock + cost counter)                                 │
└───────────────┬───────────────────────────────────────────────────────┘
                │  HTTP/JSON  (POST /api/diagnose, /api/outcome, GET /api/memory)
┌───────────────▼─── BACKEND (API routes / orchestration) ──────────────┐
│  diagnose:  useMemory? ── false → baseline (raw OpenAI, NO retrieval)   │
│                          └ true → call agent → assembleResult()         │
│                                    + getObservations() → compute conf.   │
│  outcome:   compose Experience Fact → retain                            │
│  memory:    getObservations(pattern) → freshness + MTTR trend           │
└───────────────┬───────────────────────────────────────────────────────┘
                │  via API-integration adapters
┌───────────────▼─── API INTEGRATION ───────────────────────────────────┐
│  OpenClaw agent (hosted)  ──uses──►  OpenAI (gpt-4o)                    │
│        │  Hindsight plugin                                              │
│        └──────────────►  Hindsight bank: reflect / retain / recall      │
│                          + async Observation Consolidation              │
│  HindsightClient adapter (Real | Mock)  ·  OpenAI client (baseline)     │
└────────────────────────────────────────────────────────────────────────┘
        ▲ outcome retained → consolidation updates Observation → next diagnose is sharper
```

**Two key seams:**
1. *Everything* touching Hindsight goes through one `HindsightClient` interface. A `MockHindsightClient` (canned from the seed) lets the frontend run before the integration is wired AND keeps the demo alive if the network flakes.
2. The **agent** (diagnosis reasoning) lives in **OpenClaw** with the Hindsight plugin; the backend talks to it through a single `AgentClient` boundary — so OpenClaw can be swapped or mocked without touching frontend or backend logic.

---

## 3. File / Folder Layout (organized by tier)

```
aftermath/
│
├── frontend/                         # ── FRONTEND ── Next.js UI only (no business logic)
│   ├── app/
│   │   ├── page.tsx                  # the single screen
│   │   ├── layout.tsx, globals.css
│   ├── components/
│   │   ├── IncidentForm.tsx          # service + symptom + Memory ON/OFF toggle + Diagnose btn
│   │   ├── DiagnosisCard.tsx         # root cause, fix, confidence band, avoid list, freshness banner
│   │   ├── EvidencePanel.tsx         # cited incidents w/ date + outcome + freshness badge
│   │   └── ImpactBar.tsx             # MTTR clock + cost counter (Recharts)
│   └── lib/
│       ├── api.ts                    # fetch wrappers → backend (/api/diagnose, /api/outcome, /api/memory)
│       └── types.ts                  # shared DTOs (DiagnosisResult, EvidenceItem, IncidentInput, OutcomeReport)
│
├── backend/                          # ── BACKEND ── orchestration + HTTP endpoints
│   ├── api/
│   │   ├── diagnose.ts               # POST: useMemory? baseline : agent → assembleResult (computes confidence)
│   │   ├── outcome.ts                # POST: compose Experience Fact → retain
│   │   └── memory.ts                 # GET:  getObservations(pattern) → freshness + MTTR trend
│   ├── core/
│   │   ├── confidence.ts             # the confidence formula (grounded, not hallucinated)
│   │   ├── assemble.ts               # reflect + observations → DiagnosisResult
│   │   └── retainText.ts             # composeRetainText() → first-person Experience Fact
│   └── types.ts                      # IncidentRecord, Outcome, internal types
│
├── integration/                      # ── API INTEGRATION ── all external services isolated here
│   ├── agent/
│   │   ├── AgentClient.ts            # interface the backend calls (diagnose via reasoning)
│   │   ├── OpenClawAgent.ts          # real: OpenClaw-hosted agent + Hindsight plugin + OpenAI
│   │   └── MockAgent.ts              # canned responses from the seed
│   ├── memory/
│   │   ├── HindsightClient.ts        # interface (+ ReflectResult, ObservationView)
│   │   ├── RealHindsightClient.ts    # wraps the TS SDK — SDK method names ISOLATED here
│   │   ├── MockHindsightClient.ts    # canned from the seed
│   │   └── index.ts                  # picks Real vs Mock (env flag / try-catch fallback)
│   ├── llm/
│   │   └── openai.ts                 # baseline (no-memory) completion + retry/fallback
│   └── openclaw/
│       └── config.ts                 # OpenClaw bank config: mission, disposition, directives (§6)
│
├── data/
│   └── aftermath-seed.json           # already done ✅
├── scripts/
│   └── prewarm.ts                    # retain all 11 seeds → let consolidation run BEFORE demo
└── .env.local                        # HINDSIGHT_*, OPENAI_API_KEY, OPENCLAW_*, COST_PER_MINUTE
```

> **Boundary rule:** Frontend imports only `frontend/lib`. Backend imports only `integration/*` interfaces — never an SDK directly. All vendor SDKs (OpenClaw, Hindsight, OpenAI) live exclusively under `integration/`. This is what makes the build mock-able and demo-safe.

> **If using a single Next.js app instead of split repos:** map `frontend/` → `app/` + `components/`, `backend/api/` → `app/api/*/route.ts` (or server actions), and `integration/` → `lib/integration/`. Same boundaries, one deployable.

---

## 4. Data Contracts (from solution §4 — put in `lib/types.ts`)

```typescript
export type Outcome = 'success' | 'failure';

export interface IncidentRecord {
  id: string; service: string; symptom: string; root_cause: string;
  fix: string; outcome: Outcome; mttr_minutes: number; date: string;
  lesson?: string; tags?: string[]; retain_text: string;   // feed retain_text to retain()
}

export interface DiagnosisResult {
  rootCause: string; recommendedFix: string;
  avoid: string[];                          // fixes that failed before
  supportingIncidentIds: string[];          // citations
  confidence: number;                       // 0–100, COMPUTED not asked of LLM
  confidenceBand: 'high' | 'medium' | 'low';
  freshnessWarning: string | null;
  verified: boolean;                        // false => novel/unverified
  evidence: EvidenceItem[];
  rationale: string;
}

export interface EvidenceItem {
  incidentId: string; date: string; outcome: Outcome;
  freshness?: 'stable' | 'strengthening' | 'weakening' | 'stale'; snippet: string;
}

export interface IncidentInput { service: string; symptom: string; }
export interface OutcomeReport { incidentInput: IncidentInput; appliedFix: string; outcome: Outcome; mttrMinutes: number; }
```

---

## 5. Confidence Formula (the differentiator — `lib/confidence.ts`)

Confidence is **computed from memory metadata**, never asked of the LLM.

```
n  = supporting prior incidents (proof count)
s  = successes,  f = failures
successRatio    = s / (s + f)
evidenceFactor  = min(1, n / 3)                          # 3+ = full weight
freshnessFactor = { stable:1.0, strengthening:1.0, weakening:0.5, stale:0.6 }[trend]
recencyFactor   = clamp(1 - daysSinceLastEvidence/90, 0.4, 1.0)

confidence = round(100 * successRatio * evidenceFactor * freshnessFactor * recencyFactor)
band: >=70 high · 40–69 medium · <40 low
verified = (n >= 1); if n==0 → forced LOW + UNVERIFIED
```

**The money shot:** Auth 429 pattern collapses **96 (HIGH, stable, pre-migration)** → **32 (LOW, weakening, post-migration)**. That visible collapse IS the demo.

---

## 6. Bank Configuration (set once, ~20 min — cautious senior SRE)

```
reflect_mission:      fast, SAFE mitigations grounded in what worked; distrust recently-failing fixes; never hide uncertainty.
retain_mission:       extract symptom, root cause, exact fix, outcome, date, time-to-resolution.
observations_mission: consolidate by symptom pattern AND by mitigation; track success/fail over time.
disposition:          skepticism=4, literalism=5, empathy=2
directives:
  - Always cite past incident IDs supporting a recommendation.
  - If a mitigation has any FAILURE in evidence, surface it and explain when/why.
  - If supporting observation is 'weakening' or 'stale', warn + recommend verification.
  - If no similar prior incident, say so + mark UNVERIFIED.
```

---

---

## 8. The 3 Backend Endpoints (`backend/api/*`)

The frontend calls these over HTTP; the backend orchestrates the integration tier.

```typescript
// POST /api/diagnose  { input, useMemory }
diagnose(input, useMemory):
  if (!useMemory) return llm.baselineDiagnosis(input);      // OpenAI only, NO retrieval — the dumb control
  reflect = await agent.diagnose({ query: buildQuery(input), responseSchema: DIAGNOSIS_SCHEMA });  // OpenClaw + Hindsight plugin
  obs     = await memory.getObservations(input.symptom);
  return assembleResult(reflect, obs);                      // computes confidence HERE (backend/core)

// POST /api/outcome  { outcomeReport }
outcome(o):
  await memory.retain(composeRetainText(o), { service, outcome });   // consolidation async
  return { ok: true };

// GET /api/memory?pattern=...
memory(pattern):
  return memory.getObservations(pattern);                   // drives freshness panel + MTTR trend
```

- `agent.diagnose` → the **OpenClaw**-hosted reasoning agent (Hindsight plugin does the `reflect`); behind the `AgentClient` interface so it's mockable.
- `composeRetainText` → first-person Experience Fact, same shape as seed `retain_text`.
- The `useMemory=false` branch deliberately skips OpenClaw/Hindsight entirely — raw OpenAI, the dumb control that makes the toggle dramatic.

---

## 9. The Winning Demo Script (rehearse this)

1. **Cold open (memory OFF):** new incident → generic flailing advice. *"This is every incident bot."*
2. **Flip ON:** same incident → instant cited diagnosis (3 past incidents), confidence HIGH, **MTTR 4h → 12min**, cost counter drops.
3. **Failure beat:** show agent *avoiding* the restart fix that backfired (INC-003) → recommends the real LRU fix (INC-004).
4. **Weakening beat:** Auth 429 flagged **weakening** since the 2026-05-15 Envoy migration → confidence **96 → 32**, warns instead of blindly recommending.
5. **Live learning beat:** feed fresh incident → mark outcome → re-run similar → now faster/more confident *because of the last 90 seconds.*
6. **Close:** *"Without memory: a chatbot. With Hindsight: an SRE that never stops learning."*

**Money + time on screen at all times** (MTTR clock + cost counter) for business judges; **citations on screen** for technical judges.

---

## 10. Seed → Demo-Beat Map (already in the data)

| Beat | Incidents | Mechanic |
|---|---|---|
| Closed loop | INC-001, INC-011 | retain outcome → next reflect sharper |
| Failure memory | INC-003 (restart=FAIL), INC-004 (LRU=SUCCESS) | `avoid: ["restart the pods"]` |
| Weakening trend | INC-005→010 (Auth 429, 4 successes then 2 failures post-migration) | freshness `weakening` → confidence collapse |
| Infra change driver | `meta.infrastructureChanges` 2026-05-15 Envoy migration | makes legacy-gateway shed a no-op |

---

## 11. Edge Cases & Resilience

- **Novel incident (no evidence):** `verified=false`, confidence forced LOW, UI: "treating as novel, UNVERIFIED."
- **Conflicting evidence:** surface both, lower via `successRatio`, recommend successful variant + warn.
- **Hindsight down/rate-limited:** adapter catches → falls back to `MockHindsightClient`. Demo never hard-fails.
- **Consolidation not run yet:** NEVER rely on live consolidation — pre-warm. Fall back to raw `recall()` if observation missing.
- **OpenAI function-calling error:** retry once → fallback to `gpt-4o-mini`.

---

## 12. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Hindsight Cloud flakes mid-demo | Smoke-test early; Docker self-host backup; Mock fallback. |
| Consolidation hasn't run at demo time | Pre-warm during build; never consolidate live. |
| Synthetic incidents feel fake | Seed is already specific/believable (✅). |
| OpenAI errors | Retry + `gpt-4o-mini` fallback. |
| **Strong build, flat demo (our known failure mode)** | **Over-rehearse narration; money+time always on screen.** |

---

## 13. Immediate Next Actions (start here)

1. [ ] Scaffold the three tiers: `frontend/` (`npx create-next-app` — TS, App Router, Tailwind), `backend/`, `integration/`.
2. [ ] Provision Hindsight Cloud (`MEMHACK6`); stand up **OpenClaw** + install the **Hindsight plugin**; grab all keys → `.env.local` (`HINDSIGHT_*`, `OPENAI_API_KEY`, `OPENCLAW_*`).
3. [ ] Smoke-test: one `retain` + one `reflect` round-trip **through the OpenClaw agent**. **Do this before writing any feature code.**
4. [ ] Drop `aftermath-seed.json` into `data/`, write `scripts/prewarm.ts`.
5. [ ] Scaffold `integration/memory/HindsightClient` + `MockHindsightClient` and `integration/agent/AgentClient` + `MockAgent`, plus `frontend/lib/types.ts` (unblocks frontend immediately).
6. [ ] Configure OpenClaw bank (§6), run prewarm, confirm observations appear.
7. [ ] Build the toggle path first (frontend toggle → `/api/diagnose` → baseline vs agent) — it's the highest-scoring 60 seconds.

---

*Scope discipline: Hindsight does the heavy lifting. We wire the loop and make the learning visible. Protect the demo above all.*
