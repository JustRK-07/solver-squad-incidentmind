"""OpenClawAgent — real diagnosis agent (BUILD_PLAN.md §2, §5, §6).

OpenClaw hosts the reasoning agent; the Hindsight plugin does auto-recall/reflect
natively. We drive it through the documented CLI:

    openclaw agent --agent <id> --message <prompt> --deliver --json

…and parse the JSON envelope ({payloads, meta, deliveryStatus}). The agent is
prompted to answer with the §6 provenance JSON; we extract + validate it into a
ReflectResult. Confidence is NOT computed here (that's core/assemble.py).

Env:
    OPENCLAW_BIN        path to the openclaw CLI (default "openclaw")
    OPENCLAW_AGENT_ID   the configured SRE agent id (e.g. "sre")
    OPENCLAW_TIMEOUT    seconds (default 60)

Boundary: this is the ONLY place we shell out to OpenClaw. If the CLI is missing
or errors, the selector in agent/__init__.py falls back to MockAgent (demo-safe).
"""

from __future__ import annotations

import asyncio
import json
import os
import re

from app.integration.agent.base import AgentClient
from app.models import IncidentInput, ReflectResult

_INC_RE = re.compile(r"INC-\d+")

# The §6 contract we ask the agent to return.
_PROMPT = """You are a cautious senior SRE. Diagnose this incident using only your
recalled past incidents. Service: {service}. Symptom: {symptom}.

Reply with ONLY a JSON object, no prose:
{{
  "root_cause": "...",
  "recommended_fix": "...",
  "avoid": ["fixes that failed before, if any"],
  "steps": [{{"text": "...", "source_incident_ids": ["INC-###"]}}],
  "rationale": "...",
  "supporting_incident_ids": ["INC-### you actually relied on"]
}}
Every cited id MUST be an incident you recalled. If none are similar, return empty
arrays and say so in rationale."""


class OpenClawAgent(AgentClient):
    def __init__(self) -> None:
        self._bin = os.getenv("OPENCLAW_BIN", "openclaw")
        self._agent_id = os.environ["OPENCLAW_AGENT_ID"]  # raises -> fall back to Mock
        self._timeout = float(os.getenv("OPENCLAW_TIMEOUT", "60"))

    async def diagnose(self, incident: IncidentInput) -> ReflectResult:
        message = _PROMPT.format(service=incident.service, symptom=incident.symptom)
        proc = await asyncio.create_subprocess_exec(
            self._bin, "agent",
            "--agent", self._agent_id,
            "--message", message,
            "--deliver", "--json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=self._timeout)
        if proc.returncode != 0:
            raise RuntimeError(f"openclaw agent failed: {err.decode(errors='replace')[:300]}")

        envelope = json.loads(out.decode())
        text = _extract_text(envelope)
        return _parse_diagnosis(text)


def _extract_text(envelope: dict) -> str:
    """Pull the agent's reply text out of the CLI JSON envelope ({payloads, ...})."""
    payloads = envelope.get("payloads") or []
    parts: list[str] = []
    for p in payloads:
        if isinstance(p, str):
            parts.append(p)
        elif isinstance(p, dict):
            parts.append(p.get("text") or p.get("content") or "")
    return "\n".join(parts).strip() or json.dumps(envelope)


def _parse_diagnosis(text: str) -> ReflectResult:
    """Extract the JSON object the agent returned (tolerates ```json fences / prose)."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    data = json.loads(match.group(0)) if match else {}

    # §6: collect cited ids from steps + supporting list; keep only INC-shaped ids.
    cited: list[str] = list(data.get("supporting_incident_ids") or [])
    for step in data.get("steps") or []:
        cited += step.get("source_incident_ids") or []
    supporting = sorted({i for i in cited if _INC_RE.fullmatch(i)})

    fix = data.get("recommended_fix") or " ".join(
        s.get("text", "") for s in data.get("steps") or []
    )
    return ReflectResult(
        root_cause=data.get("root_cause", "Unknown — agent returned no root cause."),
        recommended_fix=fix or "No fix proposed.",
        avoid=[a for a in (data.get("avoid") or []) if a],
        supporting_incident_ids=supporting,
        rationale=data.get("rationale", ""),
    )
