# Purpose
Narrative service scribe utilities for content generation.

# Entrypoints & Commands
- Import as module: `from services.narrative.scribe import ...`
- No direct execution

# Interfaces
- Scribe classes for different content types
- Content generation utilities

# Constraints
- Groq provider only
- Envelope v1.2 format
- Proof SHA256 validation

# Gotchas
- Handle empty responses gracefully
- Validate content quality

# Pointers
- Parent: `../AGENTS.md`
- SSOT: `../../../docs/SSOT/ssot.v1.2.yaml`
