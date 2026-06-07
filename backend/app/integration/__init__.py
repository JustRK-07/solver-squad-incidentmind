"""API INTEGRATION tier (BUILD_PLAN.md §3).

Boundary rule: ALL vendor SDKs (OpenClaw, Hindsight, OpenAI) live exclusively
under this package. Routers/core import these interfaces — never an SDK directly.
This is what makes the build mock-able and demo-safe.
"""
