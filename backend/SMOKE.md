# Backend smoke tests

Run from `backend/` with the server up (`uvicorn app.main:app --port 8000 --app-dir backend`).
All pass on mocks (zero credentials). Re-run after flipping to real services.

## Health
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

## Diagnose — memory ON (weakening beat)
```bash
curl -s http://localhost:8000/api/diagnose -H "content-type: application/json" \
  -d '{"input":{"service":"Auth Service","symptom":"login 429 cascade during a surge"},"useMemory":true}'
# confidence ~32 LOW · confidenceBand "low" · verified true · freshnessWarning set
# avoid: ["shed load at the legacy gateway ..."] · supportingIncidentIds: INC-005..010
```

## Diagnose — memory OFF (baseline control)
```bash
curl -s http://localhost:8000/api/diagnose -H "content-type: application/json" \
  -d '{"input":{"service":"Auth Service","symptom":"login 429 cascade"},"useMemory":false}'
# confidence 0 · verified false · supportingIncidentIds [] — the dumb control
```

## Diagnose — failure memory beat
```bash
curl -s http://localhost:8000/api/diagnose -H "content-type: application/json" \
  -d '{"input":{"service":"Recommendation Worker","symptom":"pods OOMKilled in CrashLoopBackOff"},"useMemory":true}'
# avoid: ["just restart the pods ..."] · cites INC-003 (fail) + INC-004 (LRU fix)
```

## Memory trend
```bash
curl -s "http://localhost:8000/api/memory?pattern=429%20cascade%20surge"
# successes/failures + freshness "weakening" + mttrTrend [...]
```

## Outcome (closed loop)
```bash
curl -s http://localhost:8000/api/outcome -H "content-type: application/json" \
  -d '{"outcomeReport":{"incidentInput":{"service":"Auth Service","symptom":"429"},"appliedFix":"Envoy shedding","outcome":"success","mttrMinutes":12}}'
# {"ok":true}
```

## Interactive docs
FastAPI auto-generates Swagger at `http://localhost:8000/docs`.
