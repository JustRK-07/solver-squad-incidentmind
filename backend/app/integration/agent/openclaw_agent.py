"""OpenClawAgent — real diagnosis agent (BUILD_PLAN.md §2, §5).

OpenClaw-hosted reasoning agent + Hindsight plugin (does the reflect) + OpenAI.
The Hindsight plugin performs recall/reflect natively; this adapter just calls the
hosted agent and maps its structured response into a ReflectResult.

TODO (Integration tier, hour 0–4):
  - wire OPENCLAW_* env (base url, agent id, api key) from openclaw/config.py
  - call the hosted agent with DIAGNOSIS_SCHEMA (structured output)
  - enforce the provenance rule (§6): supporting ids ⊆ recalled ids
"""

from __future__ import annotations

from app.integration.agent.base import AgentClient
from app.models import IncidentInput, ReflectResult


class OpenClawAgent(AgentClient):
    def __init__(self) -> None:
        # TODO: read OpenClaw config + construct the SDK client here (isolated).
        raise NotImplementedError("Wire OpenClaw + Hindsight plugin — see openclaw/config.py")

    async def diagnose(self, incident: IncidentInput) -> ReflectResult:  # pragma: no cover
        raise NotImplementedError
