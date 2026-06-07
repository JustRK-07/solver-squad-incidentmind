"""RealHindsightClient — wraps the hindsight-client SDK (BUILD_PLAN.md §3).

ALL Hindsight SDK calls are isolated in THIS file (retain / recall). Memory is the
source of truth; we read the structured fields (incident_id, outcome, date,
mttr_minutes) we set in retain() metadata back out of recall() results, then reduce
them to observation metadata via the shared observation.py math.

Env (Cloud, promo MEMHACK6):
    HINDSIGHT_BASE_URL   e.g. https://api.hindsight.vectorize.io
    HINDSIGHT_API_KEY    bearer token
    HINDSIGHT_BANK_ID    the bank to read/write
"""

from __future__ import annotations

import os
import re
from typing import Any

from hindsight_client import Hindsight

from app.integration.memory.observation import (
    build_evidence,
    build_observation_view,
    compute_observation_meta,
)
from app.integration.memory.seed_mirror import cluster_for, record_by_date, record_by_id
from app.models import EvidenceItem, ObservationMeta, ObservationView

_INC_RE = re.compile(r"INC-\d+")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class RealHindsightClient:
    def __init__(self) -> None:
        # Store config only — the SDK client is built PER CALL. An aiohttp session
        # binds to the event loop it's created on; caching one across requests breaks
        # under multiple loops ("Event loop is closed") and leaks unclosed sessions.
        self._base_url = os.environ["HINDSIGHT_BASE_URL"]  # raises if unset -> selector falls back to Mock
        self._bank = os.environ["HINDSIGHT_BANK_ID"]
        self._api_key = os.getenv("HINDSIGHT_API_KEY")
        self._timeout = float(os.getenv("HINDSIGHT_TIMEOUT", "30"))

    def _client(self) -> Hindsight:
        return Hindsight(base_url=self._base_url, api_key=self._api_key, timeout=self._timeout)

    async def retain(self, text: str, metadata: dict[str, Any]) -> None:
        meta = {k: str(v) for k, v in (metadata or {}).items()}  # SDK needs str values
        client = self._client()
        try:
            await client.aretain(bank_id=self._bank, content=text, metadata=meta)
        finally:
            await client.aclose()

    async def _recall_records(self, query: str) -> list[dict]:
        """Live Hindsight recall → identify the matching pattern → its full history.

        Hindsight recall fuses semantic + temporal relevance, so the ranked TOP
        result reliably names the right incident, but the noisy tail can't be counted
        for confidence. So we use recall to pick the single best-matching incident
        (position-weighted across the ranked facts), then return that incident's whole
        pattern cluster from the seed mirror. Result: recall is genuinely Hindsight-
        driven, while confidence/freshness are computed over a clean, query-appropriate
        incident history.
        """
        client = self._client()
        try:
            resp = await client.arecall(bank_id=self._bank, query=query, budget="mid")
        finally:
            await client.aclose()

        # Position-weighted vote: which seed incident does this recall point at?
        score: dict[str, float] = {}
        for rank, r in enumerate(resp.results):
            text = getattr(r, "text", "") or ""
            ids: set[str] = {m for m in _INC_RE.findall(text) if record_by_id(m)}
            ids |= {rec["id"] for d in _DATE_RE.findall(text) if (rec := record_by_date(d))}
            for inc_id in ids:
                score[inc_id] = score.get(inc_id, 0.0) + 1.0 / (rank + 1)

        if not score:
            return []
        top_incident = max(score, key=score.get)         # always the right primary
        return cluster_for(top_incident)                  # its full pattern history

    async def get_observations(
        self, pattern: str
    ) -> tuple[ObservationMeta, list[EvidenceItem]]:
        records = await self._recall_records(pattern)
        meta = compute_observation_meta(pattern, records)
        return meta, build_evidence(records, meta.freshness)

    async def get_observation_view(self, pattern: str) -> ObservationView:
        records = await self._recall_records(pattern)
        return build_observation_view(pattern, records)
