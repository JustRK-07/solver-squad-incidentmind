"""Seed mirror — the relational index behind live recall (BUILD_PLAN.md §D1).

Hindsight is the memory/recall truth, but its recall returns natural-language
*facts* with recency-fused ranking — great for picking the relevant pattern, noisy
for counting per-incident outcomes. So we let live recall pick the matching pattern
(its top result), then read that pattern's clean history from here to compute
confidence + freshness. This is the "relational mirror" role from the plan, served
by the seed JSON instead of Postgres for the hackathon.

A "pattern" = incidents sharing the same primary tag (tags[0]): e.g. rate-limit
(INC-005..010), memory (INC-003/004), database (INC-001/011), tls (INC-002).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_SEED_PATH = Path(__file__).resolve().parents[4] / "data" / "aftermath-seed.json"


def _record(inc: dict) -> dict:
    return {
        "id": inc["id"],
        "outcome": inc["outcome"],
        "date": inc["date"],
        "mttr_minutes": inc["mttr_minutes"],
        "snippet": inc.get("lesson") or inc["fix"],
    }


@lru_cache
def _load() -> dict:
    incidents = json.loads(_SEED_PATH.read_text(encoding="utf-8"))["incidents"]
    by_id, by_date, pattern_of, clusters = {}, {}, {}, {}
    for inc in incidents:
        rec = _record(inc)
        by_id[inc["id"]] = rec
        by_date[inc["date"]] = rec                       # seed dates are unique
        pattern = (inc.get("tags") or ["misc"])[0]       # primary tag = the pattern
        pattern_of[inc["id"]] = pattern
        clusters.setdefault(pattern, []).append(rec)
    return {"by_id": by_id, "by_date": by_date, "pattern_of": pattern_of, "clusters": clusters}


def record_by_id(inc_id: str) -> dict | None:
    return _load()["by_id"].get(inc_id)


def record_by_date(date: str) -> dict | None:
    return _load()["by_date"].get(date)


def cluster_for(inc_id: str) -> list[dict]:
    """All incidents sharing the given incident's primary pattern (its history)."""
    data = _load()
    pattern = data["pattern_of"].get(inc_id)
    return list(data["clusters"].get(pattern, []))
