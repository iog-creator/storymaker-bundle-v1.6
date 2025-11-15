# Purpose
LangGraph host that coordinates Narrative → QA/Retrieval.

# Entrypoints & Commands
- Run dev: `uvicorn services.orchestration.host:app --port 8700 --reload`
- Health: `GET /api/v1/healthz`
- Flow: `POST /api/v1/run { "premise": "..." }`

# Interfaces
- Calls downstream **only via** `/api/v1/*`
- Propagates `X-Request-Id` to all calls
- Envelope v1.2 + proof

# Constraints
- **Do not** bypass v1 routes.
- Refuse to run if any downstream is not healthy.

# Gotchas
- Legacy `/run` exists only for deprecation headers; do not use.

# Pointers
- SSOT: `../../docs/SSOT/ssot.v1.2.yaml`
