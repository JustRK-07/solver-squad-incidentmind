"""Pydantic models — the API contract (BUILD_PLAN.md §4).

These MIRROR the TypeScript DTOs in frontend/lib/types.ts. The two must stay in
sync by hand: when you change a field here, change it there. Field names are
camelCase on the wire (alias) so the Next.js frontend consumes them unchanged.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class _Camel(BaseModel):
    """Base: serialize/accept camelCase to match the TS frontend."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class Outcome(str, Enum):
    success = "success"
    failure = "failure"


Freshness = Literal["stable", "strengthening", "weakening", "stale"]
ConfidenceBand = Literal["high", "medium", "low"]


# ── Incoming ──────────────────────────────────────────────────────────────────
class IncidentInput(_Camel):
    service: str
    symptom: str


class DiagnoseRequest(_Camel):
    input: IncidentInput
    use_memory: bool = True


class OutcomeReport(_Camel):
    incident_input: IncidentInput
    applied_fix: str
    outcome: Outcome
    mttr_minutes: int


class OutcomeRequest(_Camel):
    outcome_report: OutcomeReport


# ── Outgoing ──────────────────────────────────────────────────────────────────
class EvidenceItem(_Camel):
    incident_id: str
    date: str
    outcome: Outcome
    freshness: Optional[Freshness] = None
    snippet: str


class DiagnosisResult(_Camel):
    root_cause: str
    recommended_fix: str
    avoid: list[str] = Field(default_factory=list)
    supporting_incident_ids: list[str] = Field(default_factory=list)
    confidence: int                       # 0–100, COMPUTED (core/confidence.py)
    confidence_band: ConfidenceBand
    freshness_warning: Optional[str] = None
    verified: bool
    evidence: list[EvidenceItem] = Field(default_factory=list)
    rationale: str


class ObservationView(_Camel):
    pattern: str
    successes: int
    failures: int
    freshness: Freshness
    days_since_last_evidence: int
    mttr_trend: list[int] = Field(default_factory=list)


# ── Internal (not serialized to the UI) ───────────────────────────────────────
class IncidentRecord(BaseModel):
    """A seed/resolved incident. snake_case to match aftermath-seed.json."""

    id: str
    service: str
    symptom: str
    root_cause: str
    fix: str
    outcome: Outcome
    mttr_minutes: int
    date: str
    lesson: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    retain_text: str


class ReflectResult(BaseModel):
    """Agent reasoning BEFORE confidence is computed."""

    root_cause: str
    recommended_fix: str
    avoid: list[str] = Field(default_factory=list)
    supporting_incident_ids: list[str] = Field(default_factory=list)
    rationale: str


class ObservationMeta(BaseModel):
    """Consolidated memory metadata feeding the confidence formula (§5)."""

    pattern: str
    n: int                                # proof count
    successes: int
    failures: int
    freshness: Freshness
    days_since_last_evidence: int
