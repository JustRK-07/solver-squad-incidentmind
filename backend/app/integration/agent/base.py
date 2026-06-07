"""AgentClient interface (BUILD_PLAN.md §2, §3).

The single boundary the backend calls for diagnosis reasoning. The real impl runs
inside OpenClaw with the Hindsight plugin; the mock returns canned seed responses.
Swappable without touching routers/core.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import IncidentInput, ReflectResult


class AgentClient(ABC):
    @abstractmethod
    async def diagnose(self, incident: IncidentInput) -> ReflectResult:
        """Reason over recalled memory and return a root-cause hypothesis + fix.

        Confidence is NOT computed here — that happens in core/assemble.py.
        """
        ...
