
# AfterMath — the on-call SRE agent that *learns* from every outage

> **Memory is the product, not a feature.** AfterMath is an incident-response agent
> that remembers every past outage, proposes evidence-cited mitigations with a real
> confidence score, refuses fixes that backfired before, flags fixes that are
> *decaying*, and gets visibly faster with each incident it sees.

**Problem Statement 5 grades exactly one thing:** *demonstrate that historical
knowledge improves future incident management.* Everything in AfterMath exists to make
that loop **visible, cited, and undeniable** in three minutes on stage.

---

## 1. The problem

When a service breaks at 3 a.m., the on-call engineer is alone with a wall of alerts.
The hard-won lesson from the *last* time this happened — what the root cause really was,
which fix worked, which fix made it worse — lives in a Slack thread nobody can find and
a postmortem nobody reread. Every incident starts from zero.

Generic "AI incident bots" make this worse: they hallucinate confident-sounding advice
with no memory of what actually happened at *your* company, no citations, and no idea
that the fix they're recommending failed last month. They are autocomplete with a
pager.

**The gap isn't reasoning. It's memory.** An SRE gets better over years because they
*remember*. An agent that doesn't remember is doomed to repeat every outage.

---

## 2. The solution

AfterMath is an agent built around a memory bank instead of a prompt. It runs a closed
learning loop we call **DARC**:

```
Diagnose  →  Act  →  Record  →  Consolidate  →  (the next incident is sharper)
```

- **Diagnose** — recall similar past incidents from memory, reason over them, and
  produce a root-cause hypothesis + a remediation plan where **every step cites the
  past incident it came from**.
- **Act** — the engineer applies the fix.
- **Record** — the outcome (success/failure, MTTR) is written back to memory as a
  first-person "Experience Fact."
- **Consolidate** — memory automatically rolls repeated incidents into trends, so the
  agent learns *which fixes are getting stronger and which are decaying.*

The result is an agent whose confidence is **earned from evidence**, not asserted by a
language model — and that visibly improves while you watch.

---

## 3. USP — what only AfterMath does

Plenty of teams will "use memory." AfterMath is defined by four things almost none of
them will have:

1. **It earns confidence from evidence.** A `91 (HIGH)` or `32 (LOW)` score *computed*
   from proof count, success ratio, and freshness — never a number the LLM made up.
2. **It distrusts decaying fixes.** When a once-reliable mitigation starts failing,
   AfterMath detects the **`weakening`** trend, collapses its confidence, and *warns*
   instead of blindly recommending. Fix-decay awareness is rare and it is ours.
3. **It refuses its own past mistakes.** A fix that backfired before lands on an explicit
   *"do NOT do — failed before"* list, with the failing incident cited.
4. **It proves every claim.** Each remediation step traces to the exact past incident it
   came from; a citation that wasn't actually recalled is rejected. Provenance is the
   deliverable, not decoration.

> **One line:** AfterMath is the incident agent that *cites its evidence, distrusts
> decaying fixes, refuses its own mistakes, and gets measurably faster every time it's
> used.* Without memory it's a chatbot; with memory it's an SRE that never stops learning.

---

## 4. The four differentiators (how the USP is built)

### A. Grounded confidence — computed, never hallucinated
Confidence is **calculated from memory metadata**, never asked of the LLM:

```
n  = number of supporting prior incidents      s = successes,  f = failures
successRatio    = s / (s + f)
evidenceFactor  = min(1, n / 3)                 # 3+ proofs = full weight
freshnessFactor = { stable:1.0, weakening:0.5, stale:0.6 }[trend]
recencyFactor   = clamp(1 - daysSinceLastEvidence / 90, 0.4, 1.0)

confidence = round(100 · successRatio · evidenceFactor · freshnessFactor · recencyFactor)
band: ≥70 HIGH · 40–69 MEDIUM · <40 LOW     verified = (n ≥ 1)
```

If there's no prior evidence, confidence is forced **LOW** and the result is marked
**UNVERIFIED**. The agent never hides uncertainty.

### B. The weakening beat — fixes that decay (the money shot)
The Auth-service "429 cascade" fix worked **four times** (HIGH confidence). Then an
ingress migration to Envoy silently turned the old load-shedding rule into a no-op, and
the same fix **failed twice**. AfterMath sees the trend flip to **`weakening`**, watches
confidence **collapse from HIGH to 32 (LOW)**, and *warns instead of blindly
recommending* — pointing the engineer at the real fix (shed at Envoy, not the legacy
gateway).

### C. Failure memory — the agent avoids its own past mistakes
A worker was OOM-killed; someone "fixed" it by restarting the pods (INC-003) — which
masked the leak and crashed again. The real fix was an LRU-bounded cache (INC-004).
AfterMath **refuses to recommend the restart**, surfaces it on the *"do NOT do"* list,
and recommends the LRU fix with both incidents cited.

### D. Provenance — citations are the deliverable
Every remediation step returns the `source_incident_id`(s) it was derived from, and the
backend **rejects any citation that wasn't actually recalled.** No invented IDs.

### Plus: the Memory ON/OFF toggle
The most legible before/after in ten seconds. Memory **OFF** → raw LLM, generic advice,
`0` confidence, UNVERIFIED. Memory **ON** → instant cited diagnosis, real confidence,
MTTR drops.

---

## 5. The winning demo (90 seconds)

1. **Cold open (memory OFF):** a new Auth 429 incident → generic flailing advice,
   UNVERIFIED. *"This is every incident bot."*
2. **Flip memory ON:** same incident → instant diagnosis citing 6 past incidents,
   MTTR estimate, the real Envoy fix.
3. **Failure beat:** an OOM incident → the agent *avoids* the restart that backfired
   (INC-003) and recommends the LRU fix (INC-004).
4. **Weakening beat:** the Auth 429 pattern is flagged **weakening** since the Envoy
   migration → confidence **collapses to 32**, the agent warns instead of recommending.
5. **Live learning:** resolve a fresh incident → it's retained to memory → re-run a
   similar incident and watch the new citation appear. *The agent got smarter on stage.*

Money + time stay on screen (MTTR clock, ₹ cost-saved counter) for the business judges;
citations stay on screen for the technical judges.

---

## 6. The agent system — three cooperating agents around one memory

AfterMath is not a single prompt — it is a small fleet of specialized agents that
collaborate around a shared **Hindsight** memory bank. Each one maps to a stage of the
DARC loop and pulls real weight.

### Agent 1 — the **Diagnostician** (live, the on-stage star)
A cautious-senior-SRE reasoning agent (disposition: skepticism 4, literalism 5).
On a new incident it **recalls** similar past incidents from Hindsight, **reflects** over
them with OpenAI `gpt-4o`, and **recommends** an ordered remediation plan where every
step carries its `source_incident_id`. It is forced to return strict JSON and is
prompted to *surface failures, warn on weakening evidence, and mark UNVERIFIED when no
prior incident matches.*
**Significant usage:** every diagnosis you see on stage is this agent reasoning live over
recalled memory — root cause, fix, the "do NOT do" list, and the citations all come from
it.

### Agent 2 — the **Recorder** (live, closes the loop)
The moment an incident is resolved, the Recorder composes it into a first-person
**Experience Fact** ("On 2026-06-07 the Auth Service hit a 429 cascade… I applied… Outcome:
SUCCESS, 12 min") and **retains** it to Hindsight with structured metadata.
**Significant usage:** this is the agent that makes learning *happen* — without it a fix is
a one-off; with it, the very next similar incident recalls and cites it. It is what turns
the demo's "live learning" beat from a trick into a real write to the memory bank.

### Agent 3 — the **Consolidator** (live, Hindsight-native reflection)
Hindsight continuously **reflects** over retained facts in the background, rolling
repeated incidents into higher-order **observations** and tracking each mitigation's
success/failure *over time*.
**Significant usage:** this is the agent that produces the **freshness / weakening signal**
— the thing that detects a once-reliable fix is now failing and drives the confidence
collapse. The entire weakening differentiator is powered by this consolidation step.

### Why this is a fleet, not a monolith
The agents are deliberately decoupled behind a single `AgentClient` interface, so the
**reasoning** agent can be served by three interchangeable backends without touching the
loop:

| Backend | What runs the Diagnostician | Used for |
|---|---|---|
| **HindsightAgent** | In-process: Hindsight recall + OpenAI gpt-4o | **Live demo primary** |
| **OpenClawAgent** | The OpenClaw agent host + Hindsight plugin (CLI) | Selectable (`AGENT_BACKEND=openclaw`) |
| **MockAgent** | Canned seed responses | Offline / network-flake safety |

If a live service hiccups mid-demo, the selector **falls back to the mock and logs a loud
warning** — so the demo never hard-fails and a silent fallback can never fool you. The
same seam is what lets us grow the fleet next: a **Postmortem agent** (drafts the writeup
on resolve) and a **Triage agent** (normalizes raw alerts) are designed-for, single-config
additions.

### Detailed agent specifications

Each agent specified across persona, trigger, tools, I/O, and the KPI it moves. Agents
1–3 are live; 4–5 are designed-for (roadmap).

---

#### Agent 1 — Incident Diagnostician *(live)*

1. **Persona & core purpose.** A cautious senior SRE (skepticism 4/5, literalism 5/5).
   **Mission:** recall the most similar past incidents for a new symptom, reason over
   them, and return a ranked, fully-cited remediation plan — surfacing failures, warning
   on decaying evidence, and never hiding uncertainty.
2. **Trigger mechanism.** Event-driven, synchronous. Wakes on a `POST /api/diagnose`
   event the instant an incident is submitted (console form or API call). *Production:*
   the endpoint sits behind an **alerting webhook (PagerDuty/Datadog)** or an **incident
   Kafka topic**, so it fires automatically the moment an alert crosses threshold.
3. **Tools & capabilities.** Hindsight SDK `recall` over the **memory bank** (vector +
   BM25 + graph + temporal retrieval); **OpenAI `gpt-4o`** chat-completions in JSON mode
   (fallback `gpt-4o-mini`); the relational **seed mirror** for clean per-incident
   metadata; all behind the `AgentClient` interface.
4. **Input → output.** *In:* a raw incident `{ service, symptom }` (free text).
   *Out:* a structured `DiagnosisResult` — `rootCause`, `recommendedFix`, ordered
   `steps[]` each with `source_incident_ids`, `avoid[]`, computed `confidence` + band,
   `freshnessWarning`, `evidence[]` (cited incidents w/ similarity + MTTR), `rationale`.
5. **Impact metric (KPI).** Cuts **MTTR** from hours to minutes on a recalled pattern
   (target ~4h → ~12min) and drives **repeat-incident rate → 0** by refusing fixes that
   failed before. Secondary KPI: **diagnosis-with-citation coverage** (% of incidents
   that arrive with ≥1 proven prior).

---

#### Agent 2 — Memory Recorder *(live)*

1. **Persona & core purpose.** The scribe of the loop. **Mission:** convert every
   resolved incident into a first-person "Experience Fact" and persist it to memory so
   the *next* similar incident recalls and cites it.
2. **Trigger mechanism.** Event-driven. Wakes on `POST /api/outcome` when an operator
   marks an incident resolved (or an automation reports closure).
3. **Tools & capabilities.** `compose_retain_text` (deterministic Experience-Fact
   composer) + Hindsight SDK `retain` with structured metadata (service, outcome, date,
   MTTR).
4. **Input → output.** *In:* `OutcomeReport { incidentInput, appliedFix, outcome,
   mttrMinutes }`. *Out:* a first-person Experience Fact written to the Hindsight bank
   (immediately recallable) + an ack.
5. **Impact metric (KPI).** Grows **knowledge coverage** — every resolution becomes
   reusable memory — which compounds into lower MTTR over time and **reduces new-hire
   on-call ramp** (the bank *is* the runbook). KPI: corpus-growth rate + % incidents with
   a cited prior, trending up.

---

#### Agent 3 — Memory Consolidator *(live, Hindsight-native)*

1. **Persona & core purpose.** The pattern-spotter. **Mission:** continuously reflect
   over retained facts to form higher-order observations and track each mitigation's
   success/failure *over time* — detecting when a once-reliable fix is decaying.
2. **Trigger mechanism.** **Background / asynchronous** (cron-like daemon). Runs inside
   Hindsight after each `retain`; not request-bound.
3. **Tools & capabilities.** Hindsight's `reflect` + auto-consolidation engine (forms
   observations; computes the per-pattern **freshness/weakening** trend).
4. **Input → output.** *In:* the accumulating corpus of Experience Facts. *Out:*
   consolidated **observations** + per-pattern freshness metadata that the confidence
   formula consumes.
5. **Impact metric (KPI).** Catches **fix decay** before it causes a prolonged outage —
   directly **reduces failed-mitigation attempts** and prevents stale-runbook P1s. KPI:
   time-to-detect a decaying playbook (from "after the next failure" → proactive).

---

#### Agent 4 — Postmortem Scribe *(roadmap)*

1. **Persona & core purpose.** The technical writer. **Mission:** auto-draft a complete
   postmortem from the incident, the agent's flow trace, and its citations.
2. **Trigger mechanism.** Event-driven, post-resolution (chained after the Recorder on
   `/api/outcome`).
3. **Tools & capabilities.** OpenAI `gpt-4o`; the incident record + agent flow trace +
   cited incidents; optional **Notion API** for publishing.
4. **Input → output.** *In:* resolved incident + agent flows + cited incidents. *Out:* a
   markdown/Notion **postmortem** (summary, timeline, root cause, remediation, citations).
5. **Impact metric (KPI).** Cuts **postmortem authoring time** (hours → minutes) and
   lifts **postmortem completion rate** toward 100%.

---

#### Agent 5 — Signal Triage *(roadmap)*

1. **Persona & core purpose.** The front door. **Mission:** turn noisy, multi-source
   alerts into a single clean, structured incident the Diagnostician can act on.
2. **Trigger mechanism.** Event-driven on inbound alert — a **PagerDuty/Datadog webhook**
   or a **Kafka alert topic** consumer.
3. **Tools & capabilities.** OpenAI `gpt-4o-mini`; alert-source webhooks/consumers.
4. **Input → output.** *In:* raw alert payloads (noisy, deduplicated). *Out:* a
   normalized incident `{ service, symptom, severity }`.
5. **Impact metric (KPI).** Reduces **alert-to-diagnosis latency** and **alert fatigue**
   (collapses alert noise into one actionable incident).

---

## 7. How Hindsight powers AfterMath

Hindsight (by Vectorize) is the reason "memory is the product" is a real claim and not a
slogan. It is an **agent memory system built to make agents *learn*, not just store
text** — and it does three things AfterMath leans on completely:

- **`retain`** — store an Experience Fact. Hindsight extracts entities, relationships,
  and atomic facts in the background. *This is how every resolved incident becomes
  durable institutional memory.*
- **`recall`** — retrieve relevant memories by running **four retrieval strategies in
  parallel** (semantic similarity, keyword/BM25, graph traversal, and **temporal**) and
  fusing them into one ranked list. *This is what surfaces the right past incidents for a
  new symptom — the heart of every diagnosis.*
- **`reflect` + auto-consolidation** — reason over memories to generate higher-order
  **observations**, and roll repeated incidents into trends with a **freshness** signal.
  *This is what makes a fix's confidence decay when it starts failing — our money-shot
  beat exists because Hindsight consolidates.*

Concretely, the value chain is:

```
Hindsight retain   →  every outcome becomes recallable memory          (the Recorder)
Hindsight recall   →  the right past incidents surface for a new symptom (the Diagnostician)
Hindsight reflect  →  repeated incidents become a weakening/stable trend (the Consolidator)
```

Why it's the right tool: Hindsight is **state-of-the-art on the LongMemEval benchmark**
for agent memory, ships the full **facts → observations → mental-models** hierarchy out
of the box, and provides the freshness/consolidation primitives we'd otherwise have to
fake. We wire the loop and make the learning *visible*; Hindsight does the heavy lifting
of remembering well. **It is the load-bearing wall of the product** — remove it and
AfterMath collapses back into a chatbot.

---

## 8. Architecture

Clean three-tier system with one rule: **everything that touches an external service is
isolated behind an interface, so any piece can be mocked or swapped without breaking the
others.** That discipline is what makes the build demo-safe.

```
┌─ FRONTEND — Next.js 15 + TypeScript + Tailwind + shadcn/ui ───────────────────┐
│  Inspectable incident console: header · metric cards · agent "flow" cards      │
│  (Retain → Recall → Reflect) · recommendation w/ provenance pills · why-matched │
│  · MTTR sparkline · Memory ON/OFF toggle · MTTR clock + ₹ cost counter          │
└───────────────┬────────────────────────────────────────────────────────────────┘
                │  /api/diagnose · /api/outcome   (Next.js route → adapts to UI shape)
┌───────────────▼─── BACKEND — FastAPI (Python) ───────────────────────────────────┐
│  diagnose:  memory OFF → raw OpenAI baseline (the control)                       │
│             memory ON  → Diagnostician.diagnose → getObservations → assemble      │
│                          (computes confidence + provenance HERE)                  │
│  outcome:   Recorder → compose Experience Fact → retain (closes the loop)         │
│  memory:    getObservations(pattern) → freshness + MTTR trend                     │
└───────────────┬────────────────────────────────────────────────────────────────┘
                │  via isolated adapters (one interface per service)
┌───────────────▼─── INTEGRATION — all vendor SDKs isolated here ──────────────────┐
│  AgentClient    →  HindsightAgent (live) · OpenClawAgent (selectable) · MockAgent │
│  HindsightClient →  RealHindsightClient (Cloud) · MockHindsightClient (seed)      │
│  OpenAI client   →  gpt-4o reasoning + baseline, retry → gpt-4o-mini fallback     │
└──────────────────────────────────────────────────────────────────────────────────┘
        ▲ outcome retained → consolidation updates the trend → next diagnose is sharper
```

**Memory: live recall + a relational mirror.** Hindsight is the memory source of truth.
Because its recall returns natural-language *facts*, we use the recall's top result to
pick the matching incident *pattern* live, then read that pattern's clean structured
history (outcome / MTTR) from a relational **seed mirror** for the confidence math — so
recall is genuinely Hindsight-driven while confidence is computed over a clean,
query-specific incident history.

---

## 9. Tech stack

| Layer | Choice | Why |
|---|---|---|
| **Agent memory** | **Hindsight** (Vectorize) — Cloud | `retain`/`recall`/`reflect` + auto-consolidation + freshness. The load-bearing wall. |
| **Agent host** | **OpenClaw** + official Hindsight plugin | Self-hosted agent runtime; integrated as a selectable backend behind `AgentClient`. |
| **Reasoning LLM** | **OpenAI `gpt-4o`** (fallback `gpt-4o-mini`) | Strong function-calling + structured JSON; retry/fallback on error. |
| **Backend** | **FastAPI (Python)** | Orchestration + the 3 endpoints; computes confidence + provenance. |
| **Frontend** | **Next.js 15 · TypeScript · Tailwind · shadcn/ui** | Single-screen inspectable console; talks to FastAPI over HTTP/JSON. |
| **Deploy** | **Vercel** · FastAPI hosted alongside | One-command web app; local backup for demo safety. |
| **Seed corpus** | 11 realistic incidents across 5 patterns | Proves the beats; the rate-limit pattern repeats so consolidation produces a real *weakening* trend. |

---

## 10. The seed corpus → demo-beat map

| Beat | Incidents | Mechanic |
|---|---|---|
| Closed loop | INC-001 → INC-011 | retain outcome → next recall sharper |
| Failure memory | INC-003 (restart = FAIL), INC-004 (LRU = SUCCESS) | `avoid: ["restart the pods"]` |
| Weakening trend | INC-005…008 (4 successes) → INC-009/010 (2 failures post-migration) | freshness `weakening` → confidence collapse |
| Infra-change driver | 2026-05-15 Envoy migration | makes the legacy gateway shed a no-op |

---

## 11. What's real (and our honest engineering calls)

We optimized for a **truthful, reproducible demo** over a maximal feature checklist —
the documented failure mode for strong builds is a *flat* demo, so we protected it.

- **Memory is real.** The Hindsight Cloud bank is populated with all 11 seed incidents;
  live recall returns real, query-relevant results that drive the diagnosis.
- **The Diagnostician's reasoning is real.** It recalls from Hindsight and reasons with
  live `gpt-4o`, producing cited, ordered remediation steps.
- **Confidence + provenance are real and computed**, not LLM-asserted, and enforced.
- **The Recorder writes to real memory.** Resolving an incident retains a real Experience
  Fact to the Hindsight bank, observable in the logs.
- **OpenClaw is integrated as a first-class, selectable agent host**; for live-demo
  reliability we run the equivalent in-process Diagnostician as the default — a swappable
  choice the architecture was built to allow.
- **Every request is observable.** The backend logs `[LIVE flow]` / `[MOCK data]` /
  `[BASELINE]` per diagnosis and warns loudly on any silent fallback.

---

## 12. Running it

```bash
# ── Backend (FastAPI) — from the project root ──────────────────────
python -m venv .venv && .venv\Scripts\Activate.ps1        # Windows
pip install -r backend/requirements.txt
copy .env.example .env                                     # add OPENAI + HINDSIGHT keys
python -m scripts.configure_bank                           # set §6 persona on the bank
python -m scripts.prewarm                                  # retain the 11 seeds
uvicorn app.main:app --app-dir backend --port 8000 --reload

# ── Frontend (Next.js) — separate terminal ─────────────────────────
cd frontend
npm install
npm run dev                                                # → http://localhost:3000
```

The frontend's API routes call FastAPI via `BACKEND_URL` (default `localhost:8000`) and
**fall back to mock data automatically** if the backend is unreachable. The
`USE_MOCK_AGENT` / `USE_MOCK_HINDSIGHT` flags flip each tier between live and mock — so
the whole product runs with **zero credentials** for development and goes fully live by
flipping two flags.

---

## 13. Quality & observability

- **17-test suite** (`backend/tests/test_backend.py`) — deterministic by default (forces
  mocks, zero cost), with the live OpenAI path behind an opt-in flag. Covers the
  confidence formula, freshness/weakening logic, provenance enforcement, the agent JSON
  contract, and all three endpoints.
- **Structured logging** of live-vs-mock flow per request, with fallback warnings.
- **Resilience:** OpenAI retry → `gpt-4o-mini`; Hindsight/agent → mock fallback; per-call
  Hindsight client lifecycle (no leaked sessions, multi-loop safe).

---

## 14. Project structure

```
solver-squad-incidentmind/
├── frontend/                       # Next.js 15 console (incident UI)
│   ├── app/api/{diagnose,outcome}/ # routes → proxy + adapt FastAPI → Scenario
│   ├── components/                 # incident · agent · recommendation · memory
│   └── hooks/ · services/ · types/ # diagnosis pipeline + data contracts
├── backend/                        # FastAPI orchestration
│   └── app/
│       ├── routers/                # diagnose · outcome · memory  (the 3 endpoints)
│       ├── core/                   # confidence · assemble · retain_text
│       └── integration/            # agent/ · memory/ · llm/ · openclaw/  (isolated SDKs)
├── data/aftermath-seed.json        # 11 seed incidents (5 patterns)
├── scripts/                        # configure_bank · prewarm
├── openclaw/                       # SRE agent persona (SOUL.md / AGENTS.md) + setup
└── ARCHITECTURE.md · SCAFFOLD.md · backend/SETUP.md · SMOKE.md
```

---

## 15. Roadmap

- **Postmortem agent** — drafts a markdown/Notion writeup on resolve (a tangible artifact
  a real team would pay for).
- **Triage agent** — normalizes raw PagerDuty/Datadog alerts into structured incidents.
- **Operator feedback (👍/👎)** retained as Experience Facts — the agent learns which of
  *its own* recommendations land.
- **"Pin as Runbook"** → promote a recurring incident to a curated Hindsight mental model
  checked before recall.

---

## 16. In one sentence

> **AfterMath turns every outage into institutional memory — an on-call agent that cites
> its evidence, distrusts decaying fixes, refuses its own past mistakes, and gets
> measurably faster every time it's used. Without memory, it's a chatbot. With Hindsight,
> it's an SRE that never stops learning.**
