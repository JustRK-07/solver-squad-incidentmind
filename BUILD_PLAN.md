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
| **Persistence** | **Supabase** (Postgres + RLS) | Relational mirror for the UI: `incidents`, `signals`, `agent_flows`, `recommendations`, `recommendation_sources`. **Hindsight stays the memory source of truth; Supabase holds the flow/provenance rows the console renders.** See Part II §4. |
| UI | **Tailwind CSS** + **Recharts** + **Tabler icons** (`ti-*`) | GRR-style inspectable console (Part II) + MTTR/cost counters + freshness viz. |
| Deploy | **Vercel** (frontend + API) · OpenClaw agent hosted separately | One-command for the web app. Keep local backups running. |
| Seed data | `aftermath-seed.json` (✅) → expand to **15–25 incidents** for recall depth (Part II §9) | The 11 in the seed prove the demo beats; more corpus makes recall similarity believable. |

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

---
---

# PART II — GRR-inspired UI & Agent Flows (primary console)

> **Reconciliation with Part I.** This is the **primary screen** going forward — an inspectable
> incident console (target header → agent "flows" → cited recommendation), modeled on GRR's
> legibility. It *supersedes* the 4-zone sketch in Part I §9, but **keeps Part I's differentiators**
> and folds them in: the **confidence score** (§5) rides on the Recommendation card, the
> **freshness / weakening** signal (§6.4) becomes a badge on recall rows + a "pitfalls" flow, and
> the **Memory ON/OFF toggle** (§7) re-runs recall against an empty vs full corpus for the
> before/after. The DARC loop, Experience Facts, and the seed→beat map (Part I §10) are unchanged.
> New dependency: **Supabase** (relational mirror); Hindsight remains the memory source of truth.

## 0. Goal and grading hook

Problem Statement 5 grades one thing: **demonstrate that historical knowledge improves
future incident management.** Every UI element below exists to make that loop *visible*.
The agent must recall real past incidents, reason over them, and recommend fixes that
**cite which past incidents they came from**. The provenance is the deliverable, not decoration.

Stack mapping (do not deviate):
- **OpenClaw** — agent runtime. Orchestrates the `retain → recall → reflect → recommend` loop and renders each step as an inspectable "flow".
- **Hindsight** — memory. `retain` stores incidents, `recall` retrieves similar ones, `reflect` reasons over them.
- **OpenAI LLM** — reasoning inside `reflect` and `recommend`.
- **Next.js App Router + Supabase + TypeScript + Vercel** — app shell, persistence, hosting. Server actions are the backend; no Express.

## 1. The idea we take from GRR (and the idea we reject)

GRR's UI makes machine state **legible and inspectable**: a target header with live status,
a list of "flows" (each action with a status icon + result count, expandable to its payload),
and a per-artifact detail panel with provenance. We steal that *structure*.

We **reject** GRR's forensics semantics: no filesystem tree as navigation, no raw artifact
or hex dumps. Our primary object is the **incident** and the **memory** behind it, not a disk.

| GRR concept | Our equivalent |
|---|---|
| Client header + `Online` badge | Incident header: service + status badge (`Degraded` / `Down` / `Resolved`) + severity pill |
| Flow row (`ListProcesses · 77 results · ✓`) | Agent flow card (`Recall · 4 results · ✓`) — expandable |
| Flow arguments (collapsible) | Flow payload (collapsible): retrieved incidents, hypothesis, plan |
| File detail panel (Stat / metadata) | "Why this matched" detail card: root cause, resolution, similarity |
| Collected-file provenance (path, hash, time) | Recommendation provenance pills (`from INC-204`) |

## 2. Screen layout — match the mockup exactly (top to bottom)

Single full-width console route at `/incidents/[id]`. Vertical stack, no horizontal scroll.

1. **Incident header bar** (full-width card)
   - Left: `ti-server-2` icon, service name (`payments-api-prod`, 15px/500),
     subtitle `INC-231 · opened 06:42 UTC` (13px, muted, tabular numerals).
   - Right: status badge pill (`Degraded` with `ti-alert-triangle`, danger background/text),
     then severity pill (`P1`, neutral surface).
2. **Metric cards row** — 3 cards, responsive grid `repeat(auto-fit, minmax(150px, 1fr))`, gap 12px.
   Each: muted 13px label, 24px/500 number. Values: `Similar incidents found`, `Top match` (%),
   `Est. fix time`. **All three derive from recall output — never static.**
3. **`Agent activity` section label** (13px, muted).
4. **Flow cards** (the GRR borrow), in pipeline order:
   - `Retain — ingested live signals` · `N signals` · status icon · chevron.
   - `Recall — searched incident memory` · `N results` · status icon · chevron-up (expanded by default).
     - Expanded body: one row per retrieved incident — similarity pill (blue, e.g. `92%`),
       incident id + title, right-aligned `resolved · {MTTR}`.
   - `Reflect — root-cause hypothesis` · `1 hypothesis` · status icon · chevron.
5. **Recommended remediation card** — accent border (`2px solid` info), header
   `Recommended remediation` + pill `based on N past incidents`. Numbered steps; each step
   right-aligns one or more **provenance pills** (`from INC-204`, `INC-204 · INC-187`).
6. **"Why this matched" detail card** — surface background. Header: `INC-204 · why this matched`
   + `92% similar` pill. Body: `Root cause:` … and `Resolution:` … with MTTR.

Visual tokens: 0.5px borders, `radius-lg` cards, no gradients/shadows, sentence case,
two font weights (400/500). Status = semantic colors (`danger`/`success`/`warning`),
similarity & provenance pills = blue ramp (`bg #E6F1FB`, text `#0C447C`). Dark-mode safe.

## 3. Component spec (data + behavior + visual per component)

**IncidentHeader** — props: `{ service, incidentId, openedAt, status, severity }`.
`status` ∈ `degraded | down | resolved` → badge color. `severity` ∈ `P1..P4`.

**MetricCards** — props: `{ similarCount, topMatchPct, estFixTime }`.
`similarCount` = number of recall hits above threshold. `topMatchPct` = highest similarity,
rounded integer. `estFixTime` = median MTTR of the matched incidents, formatted `~{n}m` / `~{h}h{m}m`.

**FlowCard** — props: `{ kind, label, status, resultCount, expanded, payload }`.
`kind` ∈ `retain | recall | reflect | recommend`. `status` ∈ `pending | running | success | error`
→ icon (`ti-circle-dashed` / spinner / `ti-circle-check` / `ti-alert-circle`) + color.
Clicking the header toggles `expanded` and reveals `payload`. **Status and resultCount come
from the live flow record (section 4), not props hardcoded in JSX.**

**RecallPayload** — list of `RetrievedIncident { id, title, similarityPct, status, mttrLabel }`,
sorted by similarity desc. similarityPct rounded integer.

**RecommendationCard** — props: `{ steps: RemediationStep[], sourceCount }`.
`RemediationStep { order, text, sources: IncidentRef[] }`. Render one provenance pill per
source; if 2+ sources join with ` · `. **`sources` is populated by the recommend step — see §6.**

**WhyMatchedCard** — props: `{ incidentId, similarityPct, rootCause, resolution, mttrLabel }`.
Shows the single top match by default; clicking any recall row swaps this card to that incident.

## 4. Data model

**Supabase (Postgres + RLS):**
- `incidents` — `id (INC-###)`, `service`, `title`, `symptoms`, `root_cause`, `mitigation`,
  `resolution`, `severity`, `status`, `opened_at`, `resolved_at`, `mttr_seconds`.
- `signals` — `id`, `incident_id`, `source`, `payload jsonb`, `observed_at`.
- `agent_flows` — `id`, `incident_id`, `kind (retain|recall|reflect|recommend)`,
  `status`, `result_count`, `payload jsonb`, `started_at`, `finished_at`, `order`.
- `recommendations` — `id`, `incident_id`, `order`, `text`.
- `recommendation_sources` — `recommendation_id`, `source_incident_id`, `similarity`
  (the provenance join — this table *is* the grade).

**Hindsight (memory):** each resolved incident is `retain`ed as an Experience
(symptoms + root cause + mitigation + resolution, with `incident_id` in metadata).
`recall` queries against this store; `reflect` reasons over the hits.

RLS: incidents scoped to the workspace/team. Seed data is global/read-mostly for the demo.

## 5. Agent pipeline (OpenClaw orchestration)

A new incident triggers a server action that runs the loop and writes an `agent_flows`
row per step (so the UI streams real status, not a fake animation):

1. **Retain (context)** — normalize incoming `signals`, write them, `retain` the live
   incident context into Hindsight. Flow `result_count` = number of signals. Detailed info per signal in the flow payload.
2. **Recall** — call Hindsight `recall` with the incident's symptoms. Persist hits
   (incident_id + similarity) into the recall flow `payload`. `result_count` = hits above threshold. Detailed info on each recalled incident in the payload.
3. **Reflect** — call Hindsight `reflect` (or OpenAI over the recalled incidents) to produce a
   single root-cause hypothesis. Store hypothesis + the incident_ids it relied on.
4. **Recommend** — OpenAI generates ordered remediation steps. **Every step must return the
   `source_incident_id`(s) it was derived from** (see §6). Persist to `recommendations` +
   `recommendation_sources`.

UI reads `agent_flows` + `recommendations` for the incident and renders §2. If you stream,
flip each flow `pending → running → success` as it completes.

## 6. Provenance rule (non-negotiable)

- Each remediation step is produced **with** a list of source incident ids. Prompt the LLM to
  return JSON: `[{ "text": "...", "source_incident_ids": ["INC-204"] }]`, and reject/repair any
  step whose sources are not a subset of the recalled incident ids. **No step may cite an
  incident that was not recalled.**
- Provenance pills render *only* from `recommendation_sources`. If the join is empty, render
  no pill — never a placeholder string.
- `Top match`, `Est. fix time`, similarity pills, and "Why this matched" all read from recall
  output. **Zero hardcoded numbers anywhere in the render path.**

## 7. Learning loop (the before/after that wins)

- On `Resolve`, write `resolution` + `mttr_seconds`, then `retain` the now-resolved incident
  into Hindsight. It immediately becomes recall-able for future incidents.
- Demo proof: fire incident A (thin recall), resolve it, then fire incident B that rhymes with A
  and show A appearing in B's recall with high similarity and feeding B's recommendation.
  The visible jump = "historical knowledge improving future management."

## 8. Honesty guards (build will fail review without these)

- No static similarity, MTTR, counts, or provenance strings in components.
- Recall must run against the seeded corpus; an empty corpus must render an empty recall flow,
  not fabricated rows.
- Flow statuses reflect real execution outcomes (including `error` if a step throws).

## 9. Build order (hackathon clock)

1. Seed corpus: 15–25 realistic resolved incidents (`incidents` + `retain` into Hindsight). **Do this first.**
2. Recall server action + `recall` flow card with real hits + metric cards.
3. Recommend action with enforced JSON provenance + `recommendation_sources`.
4. Recommendation card + provenance pills + "Why this matched" card.
5. Retain/Reflect flow cards + header + status states.
6. Resolve → retain loop + the before/after demo script.

## 10. Acceptance criteria

- New incident → all four flows render with live statuses and real counts.
- Recall shows ≥1 seeded incident with a computed similarity; metric cards match recall output.
- Every remediation step shows a provenance pill tracing to a recalled incident; none are literals.
- Resolving an incident makes it appear in a later similar incident's recall.
- Screen matches the mockup layout, tokens, and dark-mode behavior in §2.

## 11. 90-second demo script

1. Open `INC-231` (payments-api-prod, Degraded, P1).
2. Watch Retain → Recall populate: 4 matches, top 92% (`INC-204`).
3. Expand Recall; click `INC-204` → "Why this matched" shows its root cause + resolution.
4. Recommendation card: 3 steps, each pill tracing to `INC-204` / `INC-187`.
5. Resolve a fresh incident live, fire a similar one, show it now recalled — the agent got smarter on stage.

---
---

# PART III — Suggested additional functionality

> Ranked by **judge-impact ÷ build-cost**. Each ties back to the grading hook ("historical
> knowledge improves future management") and reuses primitives we already have. Build top-down;
> stop when the clock runs out. ★ = highest leverage for the demo.

## A. Must-add — these *are* the differentiators (cheap, high impact)

| # | Feature | What it adds | Cost | Reuses |
|---|---|---|---|---|
| **A1 ★** | **Memory ON/OFF toggle** (carry from Part I §7) | Re-runs Recall against an **empty corpus vs the full bank** on the same incident. Flows go from "0 results, generic" → "4 results, cited". The single most legible before/after in 10 seconds. | XS | recall action, two branches |
| **A2 ★** | **Freshness / weakening badge on recall rows + a `Reflect — pitfalls` flow** (carry Part I §6.4 + failure memory §10) | A recalled fix that's **decaying** gets an amber `weakening` badge; a 5th flow card lists **"do NOT do — failed before"** with provenance. This is the failure-memory beat in GRR styling — almost no team will have it. | S | freshness trend, `avoid` list |
| **A3 ★** | **Grounded confidence on the Recommendation card** (carry Part I §5) | A `confidence: 91 (HIGH)` pill computed from proof count + success ratio + freshness — *not* asked of the LLM. Pairs with the "was 96 → now 32" collapse when evidence weakens. | S | `confidence.ts` (already written in prototype) |
| **A4** | **MTTR-over-time sparkline** on the service | Recharts line showing this service's MTTR **dropping across incidents** = "the agent is making us faster." Money + time on screen. | S | `mttr_seconds`, Recharts |
| **A5** | **Cost counter** (₹ downtime saved vs no-memory baseline) | Business-judge translation. Delta between baseline MTTR and recalled MTTR × cost/min. | XS | metric cards |

## B. Should-add — deepen the "inspectable agent" story

| # | Feature | What it adds | Cost |
|---|---|---|---|
| **B1** | **Raw flow payload (expand to JSON)** | GRR's "flow arguments" — every flow card expands to its raw `payload jsonb` (the recall query, the reflect prompt, the LLM JSON). Signals *depth* and honesty to technical judges. | S |
| **B2** | **Operator feedback on the recommendation** (👍/👎 + "applied / rejected") | Retained as an **Experience Fact** → closes the loop on *recommendation quality itself*, not just incidents. The agent learns which of its own suggestions land. | S |
| **B3** | **"Pin as Runbook" → Hindsight Mental Model** | Promote a recurring incident to a curated playbook checked first; show a `📌 Runbook matched` flow above Recall. Demonstrates the full Hindsight hierarchy (mental models → observations → facts). | M |
| **B4** | **Similarity explanation / shared-entity chips** | Each recall row shows *why* it matched: shared `service`, `root_cause` tags, temporal proximity (TEMPR's 4 strategies made visible). Turns "92%" from magic into evidence. | M |
| **B5** | **Live signal simulator** | A button to inject fake PagerDuty/Datadog-style alerts that populate the **Retain** flow — makes the ingestion real-looking without a real integration. | S |

## C. Could-add — polish & business surface (only if ahead of schedule)

| # | Feature | What it adds | Cost |
|---|---|---|---|
| **C1** | **Auto-drafted postmortem** | On Resolve, generate a markdown/Notion postmortem from the incident + flows + citations. Tangible artifact a real team would pay for. | M |
| **C2** | **Incident list / command palette** | `⌘K` search over incident memory; a left rail of open incidents. Makes it feel like a product, not a demo. | M |
| **C3** | **Risk gate on apply** | If confidence is LOW or evidence is `weakening`, require an explicit "I verified this" confirm before marking a step applied. Shows the agent's caution (disposition: skepticism=4). | S |
| **C4** | **Notify on-call (stub)** | A "page the owner" button → toast + a logged notification row. Faked integration, real-feeling. | XS |
| **C5** | **Multi-service blast-radius hint** | If recalled incidents touched dependent services, surface "also check: API Gateway" from the graph strategy. | M |

## D. Decisions to confirm before building (flagged risks)

1. **Supabase vs. memory-only.** Supabase adds setup + a second source of truth. Recommended split: **Hindsight = memory/recall truth; Supabase = relational mirror for flows + provenance join (the gradeable rows).** Don't double-write incident *content* as the canonical store in both — `retain` to Hindsight, then mirror the flow/recommendation rows to Supabase for the UI. If the clock is tight, **skip Supabase** and render flows from the server action's in-memory result + Hindsight metadata.
2. **One UI or two?** Part II is now primary. The Part I 4-zone gauge sketch and the working `ui-prototype/` stay as a **logic reference** (confidence math, freshness, toggle) to port *into* the flow-card console — not as a second screen to maintain.
3. **Light vs dark.** The mockup is light-mode; Part I prototype is dark. Pick light to match the mockup; keep tokens dark-mode-safe per §2.
4. **Seed expansion.** Recall similarity only looks credible with depth. Expand the 11 seed incidents toward 15–25 (more Payments/DB + Gateway variants) **before** wiring recall, per §9.1.

---

*Recommended demo spine: open incident → flows stream (Retain→Recall→Reflect→Recommend) → every step cited (§6) → flip Memory OFF to show the collapse (A1) → resolve + re-fire to show it learned (§7). A2/A3 (failure memory + confidence) are the beats that separate us from every other "we used memory" team.*
