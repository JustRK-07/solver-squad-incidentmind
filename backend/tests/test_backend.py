"""One file that exercises ALL backend functionality (BUILD_PLAN.md).

Deterministic by default: forces the mock agent + mock Hindsight BEFORE importing
the app, so the whole suite runs offline with zero cost and stable assertions.
The one test that hits real OpenAI is gated behind RUN_LIVE_OPENAI=1.

Run:   cd backend ; python -m pytest tests/ -v
Live:  cd backend ; $env:RUN_LIVE_OPENAI=1 ; python -m pytest tests/ -v
"""

from __future__ import annotations

import asyncio
import os

# ── force deterministic config BEFORE importing app (load_dotenv won't override) ──
os.environ["USE_MOCK_AGENT"] = "true"
os.environ["USE_MOCK_HINDSIGHT"] = "true"
os.environ["DEMO_TODAY"] = "2026-06-07"

import pytest
from fastapi.testclient import TestClient

from app.core.assemble import assemble_result
from app.core.confidence import compute_confidence
from app.core.retain_text import compose_retain_text
from app.integration.agent.openclaw_agent import _extract_text, _parse_diagnosis
from app.integration.memory.observation import compute_freshness, compute_observation_meta
from app.main import app
from app.models import (
    EvidenceItem,
    IncidentInput,
    ObservationMeta,
    Outcome,
    OutcomeReport,
    ReflectResult,
)

client = TestClient(app)


def _diagnose(service: str, symptom: str, use_memory: bool = True) -> dict:
    r = client.post(
        "/api/diagnose",
        json={"input": {"service": service, "symptom": symptom}, "useMemory": use_memory},
    )
    assert r.status_code == 200, r.text
    return r.json()


# ── API: health ───────────────────────────────────────────────────────────────
def test_health():
    assert client.get("/health").json() == {"status": "ok"}


# ── API: diagnose — weakening beat (the money shot) ─────────────────────────────
def test_diagnose_weakening_beat():
    d = _diagnose("Auth Service", "login 429 cascade during a surge")
    assert d["confidenceBand"] == "low"
    assert d["confidence"] < 40                       # collapsed from the stable era
    assert d["freshnessWarning"]                      # warns instead of blindly recommending
    assert d["avoid"]                                 # surfaces the dead legacy playbook
    assert {"INC-009", "INC-010"} & set(d["supportingIncidentIds"])
    assert d["verified"] is True


# ── API: diagnose — failure memory beat ─────────────────────────────────────────
def test_diagnose_failure_memory_beat():
    d = _diagnose("Recommendation Worker", "pods OOMKilled in CrashLoopBackOff")
    assert "INC-003" in d["supportingIncidentIds"]    # the failed restart
    assert "INC-004" in d["supportingIncidentIds"]    # the real LRU fix
    assert d["avoid"]                                  # do-not-restart


# ── API: diagnose — baseline (memory OFF) is the dumb control ────────────────────
def test_diagnose_baseline_unverified():
    d = _diagnose("Auth Service", "login 429 cascade", use_memory=False)
    assert d["verified"] is False
    assert d["confidence"] == 0
    assert d["supportingIncidentIds"] == []           # nothing to cite without memory


# ── API: memory trend ───────────────────────────────────────────────────────────
def test_memory_endpoint():
    m = client.get("/api/memory", params={"pattern": "429 cascade surge"}).json()
    assert m["freshness"] == "weakening"
    assert m["failures"] >= 1 and m["successes"] >= 1
    assert len(m["mttrTrend"]) >= 2                    # drives the sparkline


# ── API: outcome (closed loop) ──────────────────────────────────────────────────
def test_outcome_endpoint():
    body = {
        "outcomeReport": {
            "incidentInput": {"service": "Auth Service", "symptom": "429"},
            "appliedFix": "Envoy shedding",
            "outcome": "success",
            "mttrMinutes": 12,
        }
    }
    assert client.post("/api/outcome", json=body).json() == {"ok": True}


# ── unit: confidence formula (§5) ───────────────────────────────────────────────
def test_confidence_novel_forced_low():
    c = compute_confidence(ObservationMeta(pattern="x", n=0, successes=0, failures=0,
                                           freshness="stable", days_since_last_evidence=0))
    assert c.verified is False and c.band == "low" and c.score == 0


def test_confidence_weakening_collapse():
    c = compute_confidence(ObservationMeta(pattern="auth-429", n=6, successes=4, failures=2,
                                           freshness="weakening", days_since_last_evidence=4))
    assert c.score == 32 and c.band == "low"          # the 96→32 collapse


def test_confidence_high_when_proven_fresh():
    c = compute_confidence(ObservationMeta(pattern="db", n=3, successes=3, failures=0,
                                           freshness="stable", days_since_last_evidence=2))
    assert c.band == "high" and c.score >= 70


# ── unit: freshness trend (§10) ─────────────────────────────────────────────────
def test_freshness_weakening_on_recent_failures():
    recs = [
        {"id": "A", "outcome": "success", "date": "2026-05-05", "mttr_minutes": 25},
        {"id": "B", "outcome": "failure", "date": "2026-05-28", "mttr_minutes": 130},
        {"id": "C", "outcome": "failure", "date": "2026-06-03", "mttr_minutes": 90},
    ]
    assert compute_freshness(recs) == "weakening"


def test_freshness_stale_when_old():
    recs = [{"id": "A", "outcome": "success", "date": "2026-01-01", "mttr_minutes": 30}]
    assert compute_freshness(recs) == "stale"


def test_observation_counts():
    recs = [
        {"id": "A", "outcome": "success", "date": "2026-05-05", "mttr_minutes": 25},
        {"id": "B", "outcome": "failure", "date": "2026-06-03", "mttr_minutes": 90},
    ]
    meta = compute_observation_meta("p", recs)
    assert meta.n == 2 and meta.successes == 1 and meta.failures == 1


# ── unit: retain text matches the seed Experience-Fact shape (§8) ───────────────
def test_retain_text_composition():
    report = OutcomeReport(incident_input=IncidentInput(service="Auth Service", symptom="429 cascade"),
                           applied_fix="Envoy shedding", outcome=Outcome.success, mttr_minutes=12)
    text = compose_retain_text(report)
    assert "Auth Service" in text and "Envoy shedding" in text
    assert "SUCCESS" in text and "12" in text


# ── unit: assemble enforces §6 provenance (no uncited evidence) ─────────────────
def test_assemble_filters_uncited_ids():
    reflect = ReflectResult(root_cause="rc", recommended_fix="fix", avoid=[],
                            supporting_incident_ids=["INC-001", "INC-999"], rationale="r")
    obs = ObservationMeta(pattern="p", n=1, successes=1, failures=0,
                          freshness="stable", days_since_last_evidence=5)
    evidence = [EvidenceItem(incident_id="INC-001", date="2026-04-02",
                             outcome=Outcome.success, snippet="s")]
    result = assemble_result(reflect, obs, evidence)
    assert result.supporting_incident_ids == ["INC-001"]   # INC-999 was never recalled → dropped


# ── unit: agent JSON contract parser (shared by OpenClaw + Hindsight agents) ────
def test_diagnosis_parser_drops_bogus_ids():
    envelope = {"payloads": [{"text": '```json\n{"root_cause":"rc","recommended_fix":"f",'
                              '"avoid":["x"],"steps":[{"text":"s","source_incident_ids":["INC-009","nope"]}],'
                              '"supporting_incident_ids":["INC-009","INC-010"],"rationale":"r"}\n```'}]}
    reflect = _parse_diagnosis(_extract_text(envelope))
    assert reflect.root_cause == "rc"
    assert reflect.supporting_incident_ids == ["INC-009", "INC-010"]   # "nope" filtered out
    assert reflect.avoid == ["x"]


# ── unit: selector returns the mock under forced-mock env ───────────────────────
def test_selectors_use_mock():
    from app.integration.agent import get_agent
    from app.integration.memory import get_memory
    assert type(get_agent()).__name__ == "MockAgent"
    assert type(get_memory()).__name__ == "MockHindsightClient"


# ── LIVE (opt-in): real gpt-4o reasoning over seed recall ───────────────────────
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_OPENAI") != "1" or not os.getenv("OPENAI_API_KEY"),
    reason="set RUN_LIVE_OPENAI=1 (and OPENAI_API_KEY) to hit real OpenAI",
)
def test_hindsight_agent_live_openai():
    from app.integration.agent.hindsight_agent import HindsightAgent

    agent = HindsightAgent()  # uses mock Hindsight recall (seed) + real OpenAI
    reflect = asyncio.run(agent.diagnose(IncidentInput(service="Auth Service",
                                                       symptom="login 429 cascade during a surge")))
    assert reflect.recommended_fix
    # every cited id must be a recalled seed incident (§6)
    assert all(i.startswith("INC-") for i in reflect.supporting_incident_ids)
