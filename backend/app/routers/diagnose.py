"""POST /api/diagnose (BUILD_PLAN.md §8).

    if not use_memory: return baseline (raw OpenAI, NO retrieval — the dumb control)
    else:              agent.diagnose -> getObservations -> assembleResult (computes confidence)

The use_memory=false branch deliberately skips OpenClaw/Hindsight entirely so the
ON/OFF toggle is dramatic.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.assemble import assemble_result
from app.integration.agent import get_agent
from app.integration.llm.openai_client import baseline_diagnosis
from app.integration.memory import get_memory
from app.models import DiagnoseRequest, DiagnosisResult

router = APIRouter()


@router.post("/diagnose", response_model=DiagnosisResult, response_model_by_alias=True)
async def diagnose(req: DiagnoseRequest) -> DiagnosisResult:
    if not req.use_memory:
        # Raw OpenAI, no retrieval — the baseline control.
        return await baseline_diagnosis(req.input)

    agent = get_agent()
    memory = get_memory()

    reflect = await agent.diagnose(req.input)
    obs, evidence = await memory.get_observations(req.input.symptom)
    return assemble_result(reflect, obs, evidence)
