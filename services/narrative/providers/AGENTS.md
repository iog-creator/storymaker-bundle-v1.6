# Purpose
Narrative service provider implementations.

# Entrypoints & Commands
- Import as module: `from services.narrative.providers import ...`
- No direct execution

# Interfaces
- Provider classes for different AI services
- Groq provider implementation

# Constraints
- Provider isolation enforced
- Groq only for creative generation
- No LM Studio calls

# Gotchas
- Handle API failures gracefully
- Implement proper retry logic

# Pointers
- Parent: `../AGENTS.md`
- SSOT: `../../../docs/SSOT/ssot.v1.2.yaml`
