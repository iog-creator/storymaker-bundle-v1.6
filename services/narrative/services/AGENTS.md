# Purpose
Narrative service business logic and orchestration.

# Entrypoints & Commands
- Import as module: `from services.narrative.services import ...`
- No direct execution

# Interfaces
- Service classes for narrative operations
- Business logic functions

# Constraints
- Groq provider only
- Envelope v1.2 format
- Proof SHA256 validation

# Gotchas
- Handle API failures gracefully
- Implement proper error handling

# Pointers
- Parent: `../AGENTS.md`
- SSOT: `../../../docs/SSOT/ssot.v1.2.yaml`
