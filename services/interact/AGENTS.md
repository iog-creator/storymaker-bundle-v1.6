# Purpose
Interaction service for user engagement and feedback.

# Entrypoints & Commands
- Run dev: `uvicorn services.interact.main:app --port 8004 --reload`
- Health: `curl $INTERACT_BASE/api/v1/health`

# Interfaces
- Public API: `/api/v1/interact/*`
- Envelope: v1.2 (status,data,error,meta,proof)
- Provider: depends on use case

# Constraints
- Envelope v1.2 required
- Include `X-Request-Id` echo
- Proof SHA256 validation

# Gotchas
- Service may be disabled in some configurations
- Check health before use

# Pointers
- SSOT: `../../docs/SSOT/ssot.v1.2.yaml`
