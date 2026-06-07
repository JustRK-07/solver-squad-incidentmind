"""Shared observation math (BUILD_PLAN.md §5, §10).

Both the Mock and Real Hindsight clients reduce a set of recalled incident records
to the metadata the confidence formula needs. Keeping it here means the weakening /
freshness logic is defined ONCE and behaves identically on mock and live memory.

A "record" is a plain dict: {id, outcome, date(YYYY-MM-DD), mttr_minutes, snippet}.
"""

from __future__ import annotations

import os
from datetime import date

from app.models import (
    EvidenceItem,
    Freshness,
    ObservationMeta,
    ObservationView,
    Outcome,
)

# Demo determinism: pin "today" so recency is stable on stage (seed meta = 2026-06-07).
_TODAY = date.fromisoformat(os.getenv("DEMO_TODAY", "2026-06-07"))


def _parse(d: str) -> date:
    try:
        return date.fromisoformat(d[:10])
    except (ValueError, TypeError):
        return _TODAY


def compute_freshness(records: list[dict]) -> Freshness:
    """Trend by chronology (§10 weakening beat).

    - last two evidences both FAILURE -> weakening (the Auth-429 collapse)
    - newest evidence is stale (>60d) -> stale
    - otherwise -> stable (strengthening if a long unbroken success streak)
    """
    if not records:
        return "stale"
    chron = sorted(records, key=lambda r: _parse(r["date"]))
    recent = chron[-2:]
    if len(recent) >= 2 and all(r["outcome"] == Outcome.failure.value for r in recent):
        return "weakening"

    days_since = (_TODAY - _parse(chron[-1]["date"])).days
    if days_since > 60:
        return "stale"
    if len(chron) >= 4 and all(r["outcome"] == Outcome.success.value for r in chron):
        return "strengthening"
    return "stable"


def compute_observation_meta(pattern: str, records: list[dict]) -> ObservationMeta:
    successes = sum(1 for r in records if r["outcome"] == Outcome.success.value)
    failures = sum(1 for r in records if r["outcome"] == Outcome.failure.value)
    days_since = (
        min((_TODAY - _parse(r["date"])).days for r in records) if records else 9999
    )
    return ObservationMeta(
        pattern=pattern,
        n=len(records),
        successes=successes,
        failures=failures,
        freshness=compute_freshness(records),
        days_since_last_evidence=max(0, days_since),
    )


def build_evidence(records: list[dict], freshness: Freshness) -> list[EvidenceItem]:
    return [
        EvidenceItem(
            incident_id=r["id"],
            date=r["date"],
            outcome=Outcome(r["outcome"]),
            freshness=freshness,
            snippet=r.get("snippet", ""),
        )
        for r in sorted(records, key=lambda r: _parse(r["date"]), reverse=True)
    ]


def build_observation_view(pattern: str, records: list[dict]) -> ObservationView:
    meta = compute_observation_meta(pattern, records)
    trend = [
        int(r.get("mttr_minutes", 0))
        for r in sorted(records, key=lambda r: _parse(r["date"]))
    ]
    return ObservationView(
        pattern=pattern,
        successes=meta.successes,
        failures=meta.failures,
        freshness=meta.freshness,
        days_since_last_evidence=meta.days_since_last_evidence,
        mttr_trend=trend,
    )
