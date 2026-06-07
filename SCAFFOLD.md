# IncidentMind — Scaffold Map

Baseline folder structure + stubs so every team member and copilot builds on the
same track. Read this first, then [BUILD_PLAN.md](BUILD_PLAN.md) for the full spec.
For the agent backends (OpenClaw vs in-process) and why, see [ARCHITECTURE.md](ARCHITECTURE.md).

> **One divergence from the plan:** the backend is **FastAPI (Python)**, not the
> Next.js/TS API routes described in BUILD_PLAN.md §1/§3. Everything else follows
> the plan. The three-tier boundary (Frontend · Backend · Integration) is intact.

## Layout

```
solver-squad-incidentmind/
├── frontend/                       # ── FRONTEND ── Next.js (App Router, TS) — UI only
│   ├── app/                        #   page.tsx · layout.tsx · globals.css (design tokens)
│   ├── components/                 #   IncidentForm · DiagnosisCard · EvidencePanel · ImpactBar
│   │                               #   + Part II: FlowCard · RecommendationCard · WhyMatchedCard
│   └── lib/                        #   api.ts (fetch → backend) · types.ts (SHARED DTOs)
│
├── backend/                        # ── BACKEND ── FastAPI orchestration + endpoints
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 #   FastAPI app + CORS + router wiring
│       ├── models.py               #   Pydantic models — MIRROR frontend/lib/types.ts
│       ├── routers/                #   diagnose.py · outcome.py · memory.py  (= §8 endpoints)
│       ├── core/                   #   confidence.py (§5) · assemble.py · retain_text.py
│       └── integration/            # ── API INTEGRATION ── all vendor SDKs isolated here
│           ├── agent/              #   AgentClient (base) · OpenClawAgent · MockAgent
│           ├── memory/             #   HindsightClient (base) · Real · Mock · selector
│           ├── llm/                #   openai_client.py (baseline control)
│           └── openclaw/           #   config.py (bank mission/disposition/directives §6)
│
├── data/aftermath-seed.json        # 11 seed incidents (expand → 15–25, §9.1)
├── scripts/prewarm.py              # retain all seeds → let consolidation run
└── .env.example                    # copy → .env, fill keys
```

## Boundary rules (what keeps it mock-able + demo-safe)

- **Frontend** imports only `frontend/lib`. Never calls a backend internal directly.
- **Backend routers/core** import only `integration/*` interfaces — never a vendor SDK.
- **All vendor SDKs** (OpenClaw, Hindsight, OpenAI) live exclusively under `backend/app/integration/`.
- **Confidence is computed** in `core/confidence.py` — never asked of the LLM (§5).
- **Mocks first:** `USE_MOCK_AGENT` / `USE_MOCK_HINDSIGHT` default `true`. The whole
  toggle path runs end-to-end on mocks before any real key is wired. Selectors fall
  back to Mock automatically if a real service throws (§11).
- **DTO sync:** `backend/app/models.py` and `frontend/lib/types.ts` describe the same
  wire contract (camelCase). Change one → change the other.

## Run it

```bash
# Backend (from solver-squad-incidentmind/)
python -m venv .venv && . .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000 --app-dir backend
python -m scripts.prewarm                          # pre-warm the bank (or the mock)

# Frontend (from frontend/)
npm install
npm run dev                                         # http://localhost:3000
```

## What's a stub vs done

- **Done (works on mocks):** types/models, confidence formula, assemble, retain_text,
  routers, MockAgent (3 demo beats), MockHindsight (reads the seed), UI components.
- **TODO (`raise NotImplementedError`):** `OpenClawAgent`, `RealHindsightClient`,
  `openai_client.baseline_diagnosis` real call. Each has a TODO block pointing at the
  BUILD_PLAN section. Wire these in the hour 0–4 integration window.

## Build order (hackathon clock, BUILD_PLAN.md §13 / Part II §9)

1. Toggle path first: `IncidentForm` → `/api/diagnose` → baseline vs MockAgent.
2. Wire real Hindsight + OpenClaw (replace the two TODO adapters).
3. Recommendation provenance + "why this matched" (Part II §6).
4. Resolve → retain loop (the before/after that wins).
