# Purpose
Vite React app. Talks to Orchestration + WorldCore/Narrative.

# Entrypoints & Commands
- Dev: `npm run dev` (port 5173)
- Env:
  - `VITE_ORCHESTRATION_BASE=http://127.0.0.1:8700`
  - `${service}/api/v1/*` only

# Interfaces
- Health fallback: try `/api/v1/health`, then `/healthz`
- Show `X-Request-Id` on errors; display proofs count from `/api/proofs/count`

# Constraints
- Reject non-v1 endpoints; reject envelopes not v1.2.

# Gotchas
- Port 5173 is locked; do not switch to 5175.

# Pointers
- SSOT: `../../docs/SSOT/ssot.v1.2.yaml`
