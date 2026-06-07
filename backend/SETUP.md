# Backend Setup — installation & credentials

What it takes to go from the mock backend (zero creds) to fully live.

## 0. Install + run on mocks (no credentials)

```bash
# from solver-squad-incidentmind/
python -m venv .venv
.venv\Scripts\Activate.ps1                 # Windows PowerShell
pip install -r backend/requirements.txt
copy .env.example .env                       # mocks are ON by default
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

`GET http://localhost:8000/health` → `{"status":"ok"}`. The whole diagnose/outcome/
memory flow (incl. the weakening beat) works on mocks now — see `backend/SMOKE.md`.

## 1. Credentials checklist

| Service | Env vars | Where to get it | Needed for |
|---|---|---|---|
| **OpenAI** | `OPENAI_API_KEY` | platform.openai.com | baseline control + OpenClaw's reasoning |
| **Hindsight Cloud** | `HINDSIGHT_BASE_URL`, `HINDSIGHT_API_KEY`, `HINDSIGHT_BANK_ID` | hindsight.vectorize.io (promo **MEMHACK6** → $50) | `/api/memory`, prewarm, recall |
| **OpenClaw** | `OPENCLAW_BIN`, `OPENCLAW_AGENT_ID` | local Node CLI (below) | the `useMemory=true` agent path |

Paste them into `.env`, then flip the toggles you've wired:
`USE_MOCK_HINDSIGHT=false`, `USE_MOCK_AGENT=false`.

## 2. Hindsight Cloud (memory)

```bash
# after putting HINDSIGHT_* in .env:
python -m scripts.configure_bank      # sets §6 missions + disposition + directives
python -m scripts.prewarm             # retain the 11 seeds → let consolidation run
```

`configure_bank` is idempotent. Run it once, then `prewarm`. Never consolidate live
on stage — pre-warm during setup (§12).

## 3. OpenClaw (agent host — self-hosted CLI, not pip)

OpenClaw is a local-first runtime. There is NO OpenClaw service key or agent id to
obtain — `OPENCLAW_AGENT_ID` is just a local name you define in config (we use `sre`).

```powershell
# 3a. Install (Windows PowerShell). macOS/Linux: curl -fsSL https://openclaw.ai/install.sh | bash
iwr -useb https://openclaw.ai/install.ps1 | iex

# 3b. Onboard — pick model provider (OpenAI), paste OPENAI_API_KEY, set up the gateway
openclaw onboard --install-daemon

# 3c. Install the Hindsight memory plugin
openclaw plugins install @vectorize-io/hindsight-openclaw

# 3d. Configure the plugin in Cloud mode with your Hindsight token (hsk_...)
npx --package @vectorize-io/hindsight-openclaw hindsight-openclaw-setup --mode cloud --token hsk_your_token
#    point it at the SAME bank the backend uses:
openclaw config set plugins.entries.hindsight-openclaw.config.bankId my-agent-memory
```

Define the `sre` agent (config-driven — there is no `openclaw agent add`). Point its
workspace at this repo's persona files (`openclaw/sre-workspace/` → SOUL.md + AGENTS.md):

```powershell
openclaw config set 'agents.list[0]' '{\"id\":\"sre\",\"model\":\"openai/gpt-4o\",\"workspace\":\"C:/Users/KULDEEP SHINDE/OneDrive/Documents/Desktop/Incident-Mind/solver-squad-incidentmind/openclaw/sre-workspace\",\"default\":true}' --json
```
(Model id uses OpenClaw's `provider/model` form: `openai/gpt-4o`. Or edit `openclaw.json`
directly if the JSON quoting fights PowerShell.)

```powershell
# 3e. Start the gateway, then sanity-check the EXACT call the backend makes
openclaw gateway
openclaw gateway status
openclaw agent --agent sre --message "ping" --deliver --json
```

The backend shells out to `openclaw agent --agent $OPENCLAW_AGENT_ID --message <prompt>
--deliver --json` and parses the JSON envelope. Run it on the same machine as FastAPI
(or put `openclaw` on PATH / set `OPENCLAW_BIN`).

> The bank persona (§6) is configured both via `scripts/configure_bank.py` (Hindsight
> SDK) AND the plugin above — they share the one `my-agent-memory` bank, so running both
> is fine and keeps memory consistent.

## 4. Go-live order

1. `.env` filled → `USE_MOCK_HINDSIGHT=false` → `configure_bank` → `prewarm`.
2. OpenClaw running + agent id set → `USE_MOCK_AGENT=false`.
3. Restart uvicorn. Re-run `backend/SMOKE.md`. If a real service errors, the selector
   silently falls back to its mock — check logs to confirm you're actually live.
