"""Memory selector: Real (Hindsight) vs Mock (BUILD_PLAN.md §3, §11).

env flag picks the adapter; try/except falls back to Mock so the demo never
hard-fails when Hindsight flakes.
"""

from __future__ import annotations

import os
from functools import lru_cache

from app.integration.memory.base import HindsightClient


@lru_cache
def get_memory() -> HindsightClient:
    if os.getenv("USE_MOCK_HINDSIGHT", "true").lower() == "true":
        from app.integration.memory.mock_hindsight import MockHindsightClient

        return MockHindsightClient()
    try:
        from app.integration.memory.real_hindsight import RealHindsightClient

        return RealHindsightClient()
    except Exception:  # noqa: BLE001 — demo-safe fallback
        from app.integration.memory.mock_hindsight import MockHindsightClient

        return MockHindsightClient()
