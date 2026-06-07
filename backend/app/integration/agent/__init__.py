"""Agent selector: Real (OpenClaw) vs Mock (BUILD_PLAN.md §3).

Picks the adapter from an env flag, with try/except fallback to Mock so the demo
never hard-fails.
"""

from __future__ import annotations

import os
from functools import lru_cache

from app.integration.agent.base import AgentClient


@lru_cache
def get_agent() -> AgentClient:
    if os.getenv("USE_MOCK_AGENT", "true").lower() == "true":
        from app.integration.agent.mock_agent import MockAgent

        return MockAgent()
    try:
        from app.integration.agent.openclaw_agent import OpenClawAgent

        return OpenClawAgent()
    except Exception:  # noqa: BLE001 — demo-safe fallback
        from app.integration.agent.mock_agent import MockAgent

        return MockAgent()
