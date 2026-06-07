"""OpenAI baseline — the dumb control (BUILD_PLAN.md §8, §11).

baseline_diagnosis() is the useMemory=false branch: raw gpt-4o, NO retrieval, NO
memory. It deliberately produces generic flailing advice so the toggle is dramatic.
Retry once -> fallback to gpt-4o-mini on a function-calling error (§11).

This module is the ONLY place the OpenAI SDK is imported.
"""

from __future__ import annotations

import os

from app.models import DiagnosisResult, IncidentInput

_PRIMARY = os.getenv("OPENAI_MODEL", "gpt-4o")
_FALLBACK = os.getenv("OPENAI_FALLBACK_MODEL", "gpt-4o-mini")


async def baseline_diagnosis(incident: IncidentInput) -> DiagnosisResult:
    """No-memory completion. Always verified=False, confidence=0 — it has no proof.

    TODO (Integration tier):
      - construct AsyncOpenAI() from OPENAI_API_KEY
      - prompt for a generic root cause + fix (no citations available)
      - retry once, then fall back to _FALLBACK on error
    """
    # Placeholder so the toggle path renders before OpenAI is wired.
    return DiagnosisResult(
        root_cause=f"(baseline, no memory) Possible cause for: {incident.symptom}",
        recommended_fix="Generic first steps: check logs, restart the service, scale up, page the owner.",
        avoid=[],
        supporting_incident_ids=[],
        confidence=0,
        confidence_band="low",
        freshness_warning=None,
        verified=False,
        evidence=[],
        rationale="No memory used — this is the baseline control with no prior incidents to cite.",
    )
