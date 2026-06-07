"""HindsightClient interface (BUILD_PLAN.md §2, §3).

The ONE interface everything touching Hindsight goes through. SDK method names
are isolated in the Real impl; the Mock is canned from the seed. Demo-safe: the
selector falls back to Mock if Hindsight is down/rate-limited (§11).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.models import EvidenceItem, ObservationMeta, ObservationView


class HindsightClient(ABC):
    @abstractmethod
    async def retain(self, text: str, metadata: dict[str, Any]) -> None:
        """Store a first-person Experience Fact. Consolidation runs async."""
        ...

    @abstractmethod
    async def get_observations(
        self, pattern: str
    ) -> tuple[ObservationMeta, list[EvidenceItem]]:
        """Return consolidated metadata (for confidence) + the cited evidence rows."""
        ...

    @abstractmethod
    async def get_observation_view(self, pattern: str) -> ObservationView:
        """Return the UI-facing freshness + MTTR-trend view for GET /api/memory."""
        ...
