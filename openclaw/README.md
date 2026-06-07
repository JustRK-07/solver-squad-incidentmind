# OpenClaw — single-agent setup (`sre`)

We run **one** OpenClaw agent: the **SRE Diagnostician**. It's the only agent the
backend calls (`OPENCLAW_AGENT_ID=sre`). Decision rationale: the grading hook is
"memory visibly makes *the* agent better in 3 minutes" — told by one agent getting
sharper, not by a fleet. (Postmortem/triage/skeptic agents were considered and
deferred — see the agent-roster discussion.)

## The agent

| Field | Value |
|---|---|
| `id` | `sre` |
| `model` | `gpt-4o` (OpenAI) — fallback `gpt-4o-mini` |
| persona | `sre-workspace/SOUL.md` (cautious senior SRE, §6 disposition) |
| operating rules | `sre-workspace/AGENTS.md` (§6 directives + JSON output contract) |
| memory | Hindsight plugin → bank `incidentmind` (read + write) |
| tools/skills | none required for the demo (reasoning + memory only) |

## Setup

OpenClaw is a self-hosted CLI (no service key; the agent id is a local name you pick).

```powershell
# install (Windows). macOS/Linux: curl -fsSL https://openclaw.ai/install.sh | bash
iwr -useb https://openclaw.ai/install.ps1 | iex

openclaw onboard --install-daemon            # provider=OpenAI, paste OPENAI_API_KEY
openclaw plugins install @vectorize-io/hindsight-openclaw

# Hindsight plugin → Cloud mode, then point it at the bank the backend uses
npx --package @vectorize-io/hindsight-openclaw hindsight-openclaw-setup --mode cloud --token hsk_your_token
openclaw config set plugins.entries.hindsight-openclaw.config.bankId my-agent-memory

# define the `sre` agent (config-driven — there is NO `openclaw agent add`),
# workspace = this folder so SOUL.md / AGENTS.md become its system prompt
openclaw config set 'agents.list[0]' '{\"id\":\"sre\",\"model\":\"openai/gpt-4o\",\"workspace\":\"<absolute path to>/openclaw/sre-workspace\",\"default\":true}' --json

openclaw gateway                              # start it
openclaw agent --agent sre --message "ping" --deliver --json   # verify the backend's exact call
```

Then set `USE_MOCK_AGENT=false` + `OPENCLAW_AGENT_ID=sre` in `.env` and restart uvicorn.

> The bank persona (missions/disposition/directives) is also applied via
> `scripts/configure_bank.py` (Hindsight SDK). OpenClaw's plugin and that script share
> the one `incidentmind` bank — running both is fine and keeps memory consistent.

## How the backend talks to it
`backend/app/integration/agent/openclaw_agent.py` shells out to
`openclaw agent --agent sre --message <prompt> --deliver --json`, parses the
`{payloads,…}` envelope, and extracts the JSON contract from `AGENTS.md` into a
`ReflectResult`. If OpenClaw is unavailable, the selector falls back to `MockAgent`.
