"""GET /api/memory?pattern=... (BUILD_PLAN.md §8).

Returns the consolidated observation for a symptom pattern — drives the freshness
panel and the MTTR-over-time sparkline (A4).
"""

from __future__ import annotations

from fastapi import APIRouter

from app.integration.memory import get_memory
from app.models import ObservationView

router = APIRouter()


@router.get("/memory", response_model=ObservationView, response_model_by_alias=True)
async def memory(pattern: str) -> ObservationView:
    return await get_memory().get_observation_view(pattern)
