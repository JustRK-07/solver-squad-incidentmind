"""compose_retain_text() -> first-person Experience Fact (BUILD_PLAN.md §8).

Must match the shape of `retain_text` in aftermath-seed.json so consolidation
groups new outcomes with the seeded corpus. See any seed record for the template:

    "On {date} the {service} {symptom}. I applied: {fix}. Outcome: {OUTCOME},
     resolved in {mttr} minutes."
"""

from __future__ import annotations

from app.models import Outcome, OutcomeReport


def compose_retain_text(report: OutcomeReport) -> str:
    verb = "resolved in" if report.outcome == Outcome.success else "but it FAILED after"
    return (
        f"The {report.incident_input.service} had: {report.incident_input.symptom} "
        f"I applied: {report.applied_fix}. "
        f"Outcome: {report.outcome.value.upper()}, {verb} {report.mttr_minutes} minutes."
    )
