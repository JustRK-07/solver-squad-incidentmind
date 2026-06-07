"""POST /api/outcome (BUILD_PLAN.md §8).

    compose first-person Experience Fact -> retain (consolidation runs async)

This closes the learning loop: a reported outcome becomes recall-able memory for
the next incident.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.retain_text import compose_retain_text
from app.integration.memory import get_memory
from app.models import OutcomeRequest

router = APIRouter()


@router.post("/outcome")
async def outcome(req: OutcomeRequest) -> dict[str, bool]:
    report = req.outcome_report
    text = compose_retain_text(report)
    await get_memory().retain(
        text,
        metadata={
            "service": report.incident_input.service,
            "outcome": report.outcome.value,
        },
    )
    return {"ok": True}
