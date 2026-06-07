"""The confidence formula — THE DIFFERENTIATOR (BUILD_PLAN.md §5).

Confidence is COMPUTED from memory metadata, never asked of the LLM.

    n  = supporting prior incidents (proof count)
    s  = successes, f = failures
    successRatio    = s / (s + f)
    evidenceFactor  = min(1, n / 3)                       # 3+ = full weight
    freshnessFactor = {stable:1.0, strengthening:1.0, weakening:0.5, stale:0.6}
    recencyFactor   = clamp(1 - daysSinceLastEvidence/90, 0.4, 1.0)

    confidence = round(100 * successRatio * evidenceFactor * freshnessFactor * recencyFactor)
    band: >=70 high · 40-69 medium · <40 low
    verified = (n >= 1); if n == 0 -> forced LOW + UNVERIFIED

The money shot: Auth 429 collapses 96 (HIGH, stable) -> 32 (LOW, weakening).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models import ConfidenceBand, ObservationMeta

_FRESHNESS_FACTOR = {
    "stable": 1.0,
    "strengthening": 1.0,
    "weakening": 0.5,
    "stale": 0.6,
}


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class Confidence:
    score: int
    band: ConfidenceBand
    verified: bool


def compute_confidence(obs: ObservationMeta) -> Confidence:
    if obs.n == 0:
        return Confidence(score=0, band="low", verified=False)

    success_ratio = obs.successes / (obs.successes + obs.failures)
    evidence_factor = min(1.0, obs.n / 3)
    freshness_factor = _FRESHNESS_FACTOR[obs.freshness]
    recency_factor = _clamp(1 - obs.days_since_last_evidence / 90, 0.4, 1.0)

    score = round(100 * success_ratio * evidence_factor * freshness_factor * recency_factor)
    band: ConfidenceBand = "high" if score >= 70 else "medium" if score >= 40 else "low"
    return Confidence(score=score, band=band, verified=True)
