# Architecture — agent backends & the OpenClaw integration

This documents how IncidentMind uses **OpenClaw** and **Hindsight**, and why the live
demo runs the in-process agent. It exists so the codebase matches the submission.

## The pluggable agent seam

Everything that reasons about an incident sits behind ONE interface — `AgentClient`
([base.py](backend/app/integration/agent/base.py)) — so the agent host is swappable
without touching the API, the confidence math, or the frontend. Three interchangeable
backends implement it:

| Backend | File | What it is | Used for |
|---|---|---|---|
| **HindsightAgent** | [hindsight_agent.py](backend/app/integration/agent/hindsight_agent.py) | In-process: **Hindsight recall → OpenAI gpt-4o reasoning → §6 JSON**. | **Live demo primary** (reliability) |
| **OpenClawAgent** | [openclaw_agent.py](backend/app/integration/agent/openclaw_agent.py) | Drives the **OpenClaw** agent host (`openclaw agent --json`) with the **Hindsight plugin**. | Selectable agent host (`AGENT_BACKEND=openclaw`) |
| **MockAgent** | [mock_agent.py](backend/app/integration/agent/mock_agent.py) | Canned seed responses (the demo beats). | Offline / network-flake safety |

Selected at runtime in [agent/__init__.py](backend/app/integration/agent/__init__.py):

```
USE_MOCK_AGENT=true            -> MockAgent
USE_MOCK_AGENT=false +
  AGENT_BACKEND=openclaw       -> OpenClawAgent   (OpenClaw host)
  AGENT_BACKEND=hindsight      -> HindsightAgent  (default)
```

Any failure constructing the real backend falls back to MockAgent, so the demo never
hard-fails.

## How OpenClaw is integrated (what's real)

- **Agent host:** `OpenClawAgent` shells out to the OpenClaw CLI and parses its JSON
  envelope into our `ReflectResult`. OpenClaw runs the agent; the **Hindsight plugin**
  wires `retain`/`recall`/`reflect` into it natively.
- **Persona:** the cautious-senior-SRE agent is defined by workspace files OpenClaw
  injects into the system prompt — [openclaw/sre-workspace/SOUL.md](openclaw/sre-workspace/SOUL.md)
  and [AGENTS.md](openclaw/sre-workspace/AGENTS.md) (disposition + the §6 directives +
  the JSON output contract).
- **Bank config:** missions / disposition / directives are applied to the shared
  Hindsight bank via [openclaw/config.py](backend/app/integration/openclaw/config.py)
  and [scripts/configure_bank.py](scripts/configure_bank.py).
- **Setup:** [openclaw/README.md](openclaw/README.md) + [backend/SETUP.md](backend/SETUP.md).

## Why HindsightAgent is the live primary (the honest reason)

OpenClaw is a self-hosted Node runtime (gateway + plugins). On stage that adds moving
parts and variability — a heavy default toolset can trip OpenAI's per-minute limits,
and a separate process is one more thing to fail live. The build plan's North Star is
**"protect the demo"** and the agent boundary was designed to be swappable for exactly
this reason.

So we run the **same reasoning loop in-process** (`HindsightAgent`): Hindsight does the
recall, OpenAI gpt-4o does the reflection over the recalled incidents, and we get an
identical `DiagnosisResult` with cited provenance and a computed confidence score. It's
faster, has no extra runtime, and degrades to mocks gracefully. OpenClaw remains a
first-class, selectable backend — not removed, one env var away.

## What is unchanged regardless of backend

- **Memory = Hindsight** (`retain`/`recall`/`reflect`) is the source of truth in every path.
- **Confidence is computed** from memory metadata in [core/confidence.py](backend/app/core/confidence.py) — never asked of the LLM.
- **Provenance (§6)** — every citation must trace to a recalled incident; enforced in
  [core/assemble.py](backend/app/core/assemble.py) + the agent parser.
- The API contract, the frontend, and the demo beats are identical across backends.

---

### Suggested submission wording

> IncidentMind is built on **OpenClaw** (agent host) + **Hindsight** (agent memory).
> The diagnosis agent — a cautious senior SRE persona with the Hindsight plugin wiring
> `retain`/`recall`/`reflect` — sits behind a pluggable `AgentClient` interface. For
> live-demo reliability we run an equivalent **in-process agent** (Hindsight recall +
> OpenAI reasoning) as the primary, with the **OpenClaw**-hosted agent selectable via a
> single flag (`AGENT_BACKEND=openclaw`) and a mock backend for offline safety. Memory
> is Hindsight in every path; confidence is computed from memory metadata, and every
> recommendation cites the past incidents it came from.
