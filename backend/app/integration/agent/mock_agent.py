"""MockAgent — canned responses from the seed (BUILD_PLAN.md §3).

Lets the frontend + backend run end-to-end before OpenClaw is wired, and keeps
the demo alive if the network flakes. The Auth-429 case returns the weakening /
failure-memory beat so the toggle path can be demoed against the mock.
"""

from __future__ import annotations

from app.integration.agent.base import AgentClient
from app.models import IncidentInput, ReflectResult


class MockAgent(AgentClient):
    async def diagnose(self, incident: IncidentInput) -> ReflectResult:
        symptom = incident.symptom.lower()

        # Auth 429 weakening beat (INC-005→010).
        if "429" in symptom or "auth" in incident.service.lower():
            return ReflectResult(
                root_cause=(
                    "Login 429 cascade during a surge. Historically fixed by shedding at the "
                    "legacy gateway — but post the 2026-05-15 Envoy migration that shed rule is a no-op."
                ),
                recommended_fix="Configure load shedding at Envoy (not the legacy gateway); warm token cache; jittered backoff.",
                avoid=["shed load at the legacy gateway (no-op since the Envoy migration)"],
                supporting_incident_ids=["INC-005", "INC-006", "INC-007", "INC-009", "INC-010"],
                rationale="4 prior successes, then 2 failures after the Envoy migration → playbook is weakening.",
            )

        # OOMKill failure-memory beat (INC-003 fail → INC-004 success).
        if "oom" in symptom or "crashloop" in symptom:
            return ReflectResult(
                root_cause="Unbounded in-memory cache leaking until OOMKill.",
                recommended_fix="Bound the cache with an LRU, set memory request/limit, fix the leak, add an 80% memory alert.",
                avoid=["just restart the pods (masks the leak — failed in INC-003)"],
                supporting_incident_ids=["INC-003", "INC-004"],
                rationale="Restart failed (INC-003); the LRU fix succeeded (INC-004).",
            )

        # Default: DB pool exhaustion (INC-001).
        return ReflectResult(
            root_cause="Connection pool exhaustion from a slow query with no statement timeout.",
            recommended_fix="Raise the pool, add a statement_timeout, add backpressure / circuit breaker.",
            avoid=[],
            supporting_incident_ids=["INC-001"],
            rationale="Matches INC-001 (Payments API 503s, DB connections pinned).",
        )
