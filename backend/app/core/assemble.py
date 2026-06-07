"""reflect + observations -> DiagnosisResult (BUILD_PLAN.md §3, §8).

Confidence is computed HERE — the join point where reasoning meets memory
metadata. The agent/LLM never sees the confidence number.
"""

from __future__ import annotations

from app.core.confidence import compute_confidence
from app.models import (
    DiagnosisResult,
    EvidenceItem,
    ObservationMeta,
    ReflectResult,
)


def assemble_result(
    reflect: ReflectResult,
    obs: ObservationMeta,
    evidence: list[EvidenceItem],
) -> DiagnosisResult:
    conf = compute_confidence(obs)

    # §6 (non-negotiable): a citation may not reference an incident that was not
    # recalled. Filter the agent's ids down to the recalled evidence set.
    recalled_ids = {e.incident_id for e in evidence}
    supporting = [i for i in reflect.supporting_incident_ids if i in recalled_ids]
    if not supporting:
        supporting = reflect.supporting_incident_ids  # nothing recalled yet → keep as-is

    freshness_warning = None
    if obs.freshness == "weakening":
        freshness_warning = "This fix is weakening — verify before applying."
    elif obs.freshness == "stale":
        freshness_warning = "Evidence is stale — confirm it still holds."

    return DiagnosisResult(
        root_cause=reflect.root_cause,
        recommended_fix=reflect.recommended_fix,
        avoid=reflect.avoid,
        supporting_incident_ids=supporting,
        confidence=conf.score,
        confidence_band=conf.band,
        freshness_warning=freshness_warning,
        verified=conf.verified,
        evidence=evidence,
        rationale=reflect.rationale,
    )
