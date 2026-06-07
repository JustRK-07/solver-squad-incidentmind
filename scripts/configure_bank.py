"""Configure the Hindsight bank — the cautious-senior-SRE persona (BUILD_PLAN.md §6).

Creates (or updates) the bank with the reflect/retain/observations missions,
disposition, and directives. Idempotent: safe to re-run. Run BEFORE prewarm.

    python -m scripts.configure_bank

Note: the OpenClaw Hindsight plugin uses this SAME bank, so configuring it here
also shapes the agent's recall/reflect. Requires real Hindsight env (not the mock):
    HINDSIGHT_BASE_URL · HINDSIGHT_API_KEY · HINDSIGHT_BANK_ID
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from hindsight_client import Hindsight  # noqa: E402

from app.integration.openclaw.config import (  # noqa: E402
    DIRECTIVES,
    DISPOSITION,
    OBSERVATIONS_MISSION,
    REFLECT_MISSION,
    RETAIN_MISSION,
)


async def main() -> None:
    bank = os.environ["HINDSIGHT_BANK_ID"]
    client = Hindsight(
        base_url=os.environ["HINDSIGHT_BASE_URL"],
        api_key=os.getenv("HINDSIGHT_API_KEY"),
    )

    try:
        await client.acreate_bank(
            bank_id=bank,
            name="IncidentMind SRE",
            reflect_mission=REFLECT_MISSION,
            retain_mission=RETAIN_MISSION,
            observations_mission=OBSERVATIONS_MISSION,
            enable_observations=True,
            disposition_skepticism=DISPOSITION["skepticism"],
            disposition_literalism=DISPOSITION["literalism"],
            disposition_empathy=DISPOSITION["empathy"],
        )
        print(f"created bank '{bank}'")
    except Exception as e:  # noqa: BLE001 — already exists → update instead
        print(f"create_bank skipped ({type(e).__name__}); updating config")
        await client.aclose() if hasattr(client, "aclose") else None
        client = Hindsight(base_url=os.environ["HINDSIGHT_BASE_URL"], api_key=os.getenv("HINDSIGHT_API_KEY"))
        client.update_bank_config(
            bank_id=bank,
            reflect_mission=REFLECT_MISSION,
            retain_mission=RETAIN_MISSION,
            observations_mission=OBSERVATIONS_MISSION,
            enable_observations=True,
            disposition_skepticism=DISPOSITION["skepticism"],
            disposition_literalism=DISPOSITION["literalism"],
            disposition_empathy=DISPOSITION["empathy"],
        )

    for i, content in enumerate(DIRECTIVES):
        try:
            client.create_directive(bank_id=bank, name=f"directive-{i+1}", content=content, priority=i)
            print(f"directive {i+1}: {content[:50]}…")
        except Exception as e:  # noqa: BLE001
            print(f"directive {i+1} skipped ({type(e).__name__})")

    print("\nBank configured. Next: python -m scripts.prewarm")


if __name__ == "__main__":
    asyncio.run(main())
