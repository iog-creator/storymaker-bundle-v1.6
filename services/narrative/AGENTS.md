# Purpose
FastAPI service for **creative generation only** (Groq 70B). Emits outline beats.

# Entrypoints & Commands
- Run dev: `uvicorn services.narrative.main:app --port 8001 --reload`
- Health: `curl $NARRATIVE_BASE/api/v1/health`
- Outline: `curl -H 'Content-Type: application/json' -d '{"world_id":"w","premise":"p","structure":"harmon_8"}' $NARRATIVE_BASE/api/v1/narrative/outline`

# Interfaces
- Public API: `/api/v1/narrative/outline`
- Envelope: v1.2 (status,data,error,meta,proof)
- Provider: `groq`, Model: `llama-3.3-70b-versatile`
- Proofs: write to `docs/proofs/agentpm/...` with `proof.sha256`

# Constraints
- **Never** call LM Studio from here (provider isolation).
- Fail-closed: if Groq not ready → return 503 `UNHEALTHY_DEPENDENCY`.
- Include `X-Request-Id` echo.

# Gotchas
- Import `timezone` for UTC timestamps.
- Reject empty beats or boilerplate; return 502 `BAD_OUTPUT_SHAPE`.

# Pointers
- Parent SSOT: `../../docs/SSOT/ssot.v1.2.yaml`
- SSOT contract: `../../docs/SSOT/MASTER_PLAN.md`
