# Purpose
Screenplay service for script generation and formatting.

# Entrypoints & Commands
- Run dev: `uvicorn services.screenplay.main:app --port 8002 --reload`
- Health: `curl $SCREENPLAY_BASE/api/v1/health`

# Interfaces
- Public API: `/api/v1/screenplay/*`
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
