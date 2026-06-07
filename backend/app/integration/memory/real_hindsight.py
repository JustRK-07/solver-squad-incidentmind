"""RealHindsightClient — wraps the Hindsight SDK (BUILD_PLAN.md §3).

ALL Hindsight SDK method names are isolated in THIS file. If the SDK renames
recall/reflect/retain, only this file changes.

TODO (Integration tier, hour 0–4):
  - construct the SDK client from HINDSIGHT_* env (api key, bank id, base url)
  - retain(): call sdk.retain(text, metadata)
  - get_observations(): recall similar incidents, read consolidated observation
    (successes/failures/freshness/recency), map hits -> EvidenceItem
  - get_observation_view(): map the observation -> ObservationView (+ mttr_trend)
  - on any error, the selector in __init__.py falls back to the Mock
"""

from __future__ import annotations

from typing import Any

from app.integration.memory.base import HindsightClient
from app.models import EvidenceItem, ObservationMeta, ObservationView


class RealHindsightClient(HindsightClient):
    def __init__(self) -> None:
        # TODO: read HINDSIGHT_* env + construct the SDK client (isolated here).
        raise NotImplementedError("Wire Hindsight SDK — HINDSIGHT_API_KEY / bank id")

    async def retain(self, text: str, metadata: dict[str, Any]) -> None:  # pragma: no cover
        raise NotImplementedError

    async def get_observations(
        self, pattern: str
    ) -> tuple[ObservationMeta, list[EvidenceItem]]:  # pragma: no cover
        raise NotImplementedError

    async def get_observation_view(self, pattern: str) -> ObservationView:  # pragma: no cover
        raise NotImplementedError
