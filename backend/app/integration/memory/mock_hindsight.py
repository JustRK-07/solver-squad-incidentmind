"""MockHindsightClient — canned from the seed (BUILD_PLAN.md §3, §11).

Reads data/aftermath-seed.json and derives observation metadata so the confidence
formula and freshness beats work end-to-end without a live bank. retain() appends
to an in-memory list so the live-learning beat (§9.5) still demos against the mock.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models import (
    EvidenceItem,
    Freshness,
    IncidentRecord,
    ObservationMeta,
    ObservationView,
    Outcome,
)

_SEED_PATH = Path(__file__).resolve().parents[4] / "data" / "aftermath-seed.json"


def _load_seed() -> list[IncidentRecord]:
    raw = json.loads(_SEED_PATH.read_text(encoding="utf-8"))
    return [IncidentRecord(**i) for i in raw["incidents"]]


class MockHindsightClient:
    """In-memory stand-in. NOTE: not ABC-subclassed to keep import light; it
    satisfies the HindsightClient protocol structurally."""

    def __init__(self) -> None:
        self._incidents = _load_seed()
        self._retained: list[str] = []

    async def retain(self, text: str, metadata: dict[str, Any]) -> None:
        self._retained.append(text)

    def _match(self, pattern: str) -> list[IncidentRecord]:
        # Naive keyword match — Real impl uses Hindsight recall (vector similarity).
        p = pattern.lower()
        hits = [i for i in self._incidents if any(w in i.symptom.lower() for w in p.split() if len(w) > 3)]
        return hits or self._incidents[:1]

    def _freshness(self, hits: list[IncidentRecord]) -> Freshness:
        # Weakening if recent records flipped to failure (the Auth-429 beat).
        recent = sorted(hits, key=lambda i: i.date)[-2:]
        if recent and all(i.outcome == Outcome.failure for i in recent):
            return "weakening"
        return "stable"

    async def get_observations(
        self, pattern: str
    ) -> tuple[ObservationMeta, list[EvidenceItem]]:
        hits = self._match(pattern)
        successes = sum(1 for i in hits if i.outcome == Outcome.success)
        failures = sum(1 for i in hits if i.outcome == Outcome.failure)
        freshness = self._freshness(hits)
        last_date = max(i.date for i in hits)
        # TODO: compute real days-since from `today` in seed meta.
        days_since = 30

        meta = ObservationMeta(
            pattern=pattern,
            n=len(hits),
            successes=successes,
            failures=failures,
            freshness=freshness,
            days_since_last_evidence=days_since,
        )
        evidence = [
            EvidenceItem(
                incident_id=i.id,
                date=i.date,
                outcome=i.outcome,
                freshness=freshness,
                snippet=i.lesson or i.fix,
            )
            for i in sorted(hits, key=lambda i: i.date, reverse=True)
        ]
        return meta, evidence

    async def get_observation_view(self, pattern: str) -> ObservationView:
        meta, _ = await self.get_observations(pattern)
        hits = self._match(pattern)
        return ObservationView(
            pattern=pattern,
            successes=meta.successes,
            failures=meta.failures,
            freshness=meta.freshness,
            days_since_last_evidence=meta.days_since_last_evidence,
            mttr_trend=[i.mttr_minutes for i in sorted(hits, key=lambda i: i.date)],
        )
