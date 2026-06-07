"""Pre-warm the Hindsight bank (BUILD_PLAN.md §3, §12).

retain() all seed incidents BEFORE the demo so async consolidation produces
observations + freshness trends. NEVER rely on live consolidation on stage.

Usage:  python -m scripts.prewarm
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

# Run from the project root so `app` is importable: python -m scripts.prewarm
from backend.app.integration.memory import get_memory

SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "aftermath-seed.json"


async def main() -> None:
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    memory = get_memory()
    for inc in seed["incidents"]:
        await memory.retain(
            inc["retain_text"],
            metadata={
                "incident_id": inc["id"],
                "service": inc["service"],
                "outcome": inc["outcome"],
                "date": inc["date"],
            },
        )
        print(f"retained {inc['id']} ({inc['outcome']})")
    print(f"\nDone — {len(seed['incidents'])} incidents retained. Let consolidation run.")


if __name__ == "__main__":
    asyncio.run(main())
