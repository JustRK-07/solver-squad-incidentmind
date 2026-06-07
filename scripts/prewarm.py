"""Pre-warm the Hindsight bank (BUILD_PLAN.md §3, §12).

retain() all seed incidents BEFORE the demo so async consolidation produces
observations + freshness trends. NEVER rely on live consolidation on stage.

Run from the project root:  python -m scripts.prewarm
(Works against the mock too — flip USE_MOCK_HINDSIGHT in .env.)
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))  # use the same `app.*` imports as the server

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from app.integration.memory import get_memory  # noqa: E402

SEED_PATH = ROOT / "data" / "aftermath-seed.json"


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
                "mttr_minutes": inc["mttr_minutes"],
            },
        )
        print(f"retained {inc['id']} ({inc['outcome']})")
    print(f"\nDone — {len(seed['incidents'])} incidents retained. Let consolidation run.")


if __name__ == "__main__":
    asyncio.run(main())
