# Purpose
AI service utilities and providers.

# Entrypoints & Commands
- Import as module: `from services.ai import ...`
- No direct execution

# Interfaces
- Provider classes for different AI services
- Utility functions for AI operations

# Constraints
- Provider isolation enforced
- Groq for creative, LM Studio for QA/retrieval

# Gotchas
- Do not mix providers in same service
- Handle API failures gracefully

# Pointers
- SSOT: `../../docs/SSOT/ssot.v1.2.yaml`
