"""HindsightAgent — the Python-direct diagnosis agent (BUILD_PLAN.md §2, §5, §6).

Part II §5 explicitly allows reasoning via "Hindsight reflect OR OpenAI over the
recalled incidents." This adapter takes the second route and runs the agent entirely
in-process — no OpenClaw runtime required:

    recall (via the memory layer) → OpenAI gpt-4o reasons over the hits → §6 JSON
    → ReflectResult (provenance validated against the recalled ids).

It honors the SAME AgentClient interface as MockAgent / OpenClawAgent, so the
diagnose route, confidence math, and frontend are unchanged. Recall goes through
get_memory(), so it works on the seed mock OR live Hindsight identically.

Env: OPENAI_API_KEY (required) · OPENAI_MODEL (gpt-4o) · OPENAI_FALLBACK_MODEL (gpt-4o-mini)
Resilience (§11): retry primary once, then fall back to mini.
"""

from __future__ import annotations

import json
import os

from app.integration.agent.base import AgentClient
from app.integration.agent.openclaw_agent import _parse_diagnosis  # shared §6 JSON parser
from app.integration.memory import get_memory
from app.integration.openclaw.config import DIRECTIVES, REFLECT_MISSION
from app.models import IncidentInput, ReflectResult

_PRIMARY = os.getenv("OPENAI_MODEL", "gpt-4o")
_FALLBACK = os.getenv("OPENAI_FALLBACK_MODEL", "gpt-4o-mini")

_SYSTEM = (
    "You are a cautious senior SRE (skepticism 4/5, literalism 5/5, terse). "
    f"Mission: {REFLECT_MISSION}\nDirectives:\n- " + "\n- ".join(DIRECTIVES)
)

_CONTRACT = (
    "Return ONLY a JSON object, no prose:\n"
    '{"root_cause":"...","recommended_fix":"...","avoid":["fixes that failed before"],'
    '"steps":[{"text":"...","source_incident_ids":["INC-###"]}],'
    '"supporting_incident_ids":["INC-### you relied on"],"rationale":"..."}\n'
    "Cite ONLY incident ids from the recalled list. If none are similar, return empty "
    "arrays and say so in rationale."
)


class HindsightAgent(AgentClient):
    def __init__(self) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY required for HindsightAgent")

    async def diagnose(self, incident: IncidentInput) -> ReflectResult:
        # 1. Recall similar past incidents through the memory layer (mock or live).
        _, evidence = await get_memory().get_observations(incident.symptom)
        recalled = "\n".join(
            f"- {e.incident_id} | {e.date} | {e.outcome.value} | {e.snippet}"
            for e in evidence
        ) or "(no similar past incidents recalled)"

        user = (
            f"Incident — Service: {incident.service}. Symptom: {incident.symptom}.\n\n"
            f"Recalled past incidents (your memory):\n{recalled}\n\n{_CONTRACT}"
        )

        # 2. Reason with OpenAI (retry once → fallback model).
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        messages = [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user},
        ]
        last_err: Exception | None = None
        for model in (_PRIMARY, _PRIMARY, _FALLBACK):
            try:
                resp = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                reflect = _parse_diagnosis(resp.choices[0].message.content or "{}")
                # §6: keep only citations that were actually recalled.
                recalled_ids = {e.incident_id for e in evidence}
                if recalled_ids:
                    reflect.supporting_incident_ids = [
                        i for i in reflect.supporting_incident_ids if i in recalled_ids
                    ]
                return reflect
            except Exception as e:  # noqa: BLE001 — retry/fallback
                last_err = e

        raise RuntimeError(f"HindsightAgent OpenAI call failed: {last_err}")
