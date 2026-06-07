"""MockHindsightClient — canned from the seed (BUILD_PLAN.md §3, §11).

Reads data/aftermath-seed.json. Uses the SAME observation math as the real client
(observation.py) so freshness/confidence behave identically on mock and live memory.
retain() appends to an in-memory list so the live-learning beat (§9.5) still demos.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.integration.memory.observation import (
    build_evidence,
    build_observation_view,
    compute_observation_meta,
)
from app.models import EvidenceItem, ObservationMeta, ObservationView

_SEED_PATH = Path(__file__).resolve().parents[4] / "data" / "aftermath-seed.json"


def _record(inc: dict) -> dict:
    return {
        "id": inc["id"],
        "outcome": inc["outcome"],
        "date": inc["date"],
        "mttr_minutes": inc["mttr_minutes"],
        "snippet": inc.get("lesson") or inc["fix"],
    }


class MockHindsightClient:
    def __init__(self) -> None:
        raw = json.loads(_SEED_PATH.read_text(encoding="utf-8"))
        self._incidents: list[dict] = raw["incidents"]
        self._retained: list[str] = []

    async def retain(self, text: str, metadata: dict[str, Any]) -> None:
        self._retained.append(text)

    def _match(self, pattern: str) -> list[dict]:
        p = pattern.lower()
        words = [w for w in p.split() if len(w) > 3]
        hits = [
            _record(i)
            for i in self._incidents
            if any(w in i["symptom"].lower() for w in words)
        ]
        return hits or [_record(self._incidents[0])]

    async def get_observations(
        self, pattern: str
    ) -> tuple[ObservationMeta, list[EvidenceItem]]:
        records = self._match(pattern)
        meta = compute_observation_meta(pattern, records)
        return meta, build_evidence(records, meta.freshness)

    async def get_observation_view(self, pattern: str) -> ObservationView:
        return build_observation_view(pattern, self._match(pattern))
