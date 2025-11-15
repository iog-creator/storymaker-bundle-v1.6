# Purpose
WorldCore service API endpoints and handlers.

# Entrypoints & Commands
- Import as module: `from services.worldcore.api import ...`
- No direct execution

# Interfaces
- FastAPI route handlers
- API endpoint definitions
- Request/response models

# Constraints
- LM Studio provider only
- Envelope v1.2 format
- Proof SHA256 validation

# Gotchas
- Handle API failures gracefully
- Implement proper error handling

# Pointers
- Parent: `../AGENTS.md`
- SSOT: `../../../docs/SSOT/ssot.v1.2.yaml`
