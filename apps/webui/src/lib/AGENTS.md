# Purpose
Utility functions and API clients for WebUI.

# Entrypoints & Commands
- Import utilities in components
- No direct execution

# Interfaces
- Export utility functions
- API client functions
- Type definitions

# Constraints
- All API calls must use `/api/v1/*` endpoints
- Handle envelope v1.2 format
- Include error handling

# Gotchas
- API calls must include `X-Request-Id` header
- Handle proof validation

# Pointers
- Parent: `../AGENTS.md`
- SSOT: `../../../docs/SSOT/ssot.v1.2.yaml`
