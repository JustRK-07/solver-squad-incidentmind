"""OpenAI baseline — the dumb control (BUILD_PLAN.md §8, §11).

baseline_diagnosis() is the useMemory=false branch: raw gpt-4o, NO retrieval, NO
memory — generic advice so the toggle is dramatic. It is ALWAYS verified=False /
confidence=0: with no recalled evidence there is nothing to ground a score on.

Resilience (§11): retry once, then fall back to gpt-4o-mini on error. If OPENAI_API_KEY
is unset, returns a static placeholder so the toggle still renders.

This module is the ONLY place the OpenAI SDK is imported.
"""

from __future__ import annotations

import json
import os

from app.models import DiagnosisResult, IncidentInput

_PRIMARY = os.getenv("OPENAI_MODEL", "gpt-4o")
_FALLBACK = os.getenv("OPENAI_FALLBACK_MODEL", "gpt-4o-mini")

_SYSTEM = (
    "You are a generic incident chatbot with NO memory of past incidents and no "
    "runbooks. Give brief, generic first-aid advice. You cannot cite anything."
)
_USER = (
    "Service: {service}\nSymptom: {symptom}\n\n"
    'Reply with ONLY JSON: {{"root_cause": "...", "recommended_fix": "...", "rationale": "..."}}'
)


def _result(root_cause: str, fix: str, rationale: str) -> DiagnosisResult:
    return DiagnosisResult(
        root_cause=root_cause,
        recommended_fix=fix,
        avoid=[],
        supporting_incident_ids=[],
        confidence=0,
        confidence_band="low",
        freshness_warning=None,
        verified=False,            # no memory ⇒ never verified (the whole point)
        evidence=[],
        rationale=rationale,
    )


async def baseline_diagnosis(incident: IncidentInput) -> DiagnosisResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _result(
            f"(baseline, no memory) Possible cause for: {incident.symptom}",
            "Generic first steps: check logs, restart the service, scale up, page the owner.",
            "No OPENAI_API_KEY set — static baseline placeholder.",
        )

    from openai import AsyncOpenAI  # imported lazily so the mock path needs no SDK

    client = AsyncOpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": _USER.format(service=incident.service, symptom=incident.symptom)},
    ]

    last_err: Exception | None = None
    for model in (_PRIMARY, _PRIMARY, _FALLBACK):  # retry primary once, then fallback
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            data = json.loads(resp.choices[0].message.content or "{}")
            return _result(
                data.get("root_cause", "Unknown."),
                data.get("recommended_fix", "No fix proposed."),
                data.get("rationale", "Baseline (no memory).") + f" [model={model}]",
            )
        except Exception as e:  # noqa: BLE001 — retry/fallback
            last_err = e

    return _result(
        f"(baseline error) {incident.symptom}",
        "Check logs, restart, scale, escalate.",
        f"OpenAI baseline failed after retries: {last_err}",
    )
