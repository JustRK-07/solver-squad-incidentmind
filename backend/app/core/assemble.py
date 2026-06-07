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

    freshness_warning = None
    if obs.freshness == "weakening":
        freshness_warning = "This fix is weakening — verify before applying."
    elif obs.freshness == "stale":
        freshness_warning = "Evidence is stale — confirm it still holds."

    return DiagnosisResult(
        root_cause=reflect.root_cause,
        recommended_fix=reflect.recommended_fix,
        avoid=reflect.avoid,
        supporting_incident_ids=reflect.supporting_incident_ids,
        confidence=conf.score,
        confidence_band=conf.band,
        freshness_warning=freshness_warning,
        verified=conf.verified,
        evidence=evidence,
        rationale=reflect.rationale,
    )
