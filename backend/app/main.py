"""FastAPI app entrypoint (BUILD_PLAN.md §2 backend tier).

Run locally:  uvicorn app.main:app --reload --port 8000
The Next.js frontend points NEXT_PUBLIC_API_BASE at this service.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import diagnose, memory, outcome

load_dotenv()

app = FastAPI(title="IncidentMind API", version="0.1.0")

# Frontend (Next.js) runs on a different origin during dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagnose.router, prefix="/api", tags=["diagnose"])
app.include_router(outcome.router, prefix="/api", tags=["outcome"])
app.include_router(memory.router, prefix="/api", tags=["memory"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
