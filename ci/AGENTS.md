# Purpose
Guards and self-tests.

# Entrypoints & Commands
- Run all: `make verify-all`
- Key scripts: model_lock_guard.sh, retrieval_smoke_guard.sh, proof_integrity_guard.sh,
  qa_nonempty_guard.sh, provider_isolation_guard.sh, fresh_shell_env_guard.sh, no_legacy_routes_guard.sh

# Interfaces
- All guards must source `ci/_load_env.sh`
- Exit codes: 0=pass, 1=fail
- Output: GitHub Actions format (`::error ::`)

# Constraints
- All guards must **fail-closed** (`set -euo pipefail`).
- Always source `ci/_load_env.sh`.

# Gotchas
- Guards run in CI; must be executable and self-contained.

# Pointers
- SSOT: `../docs/SSOT/ssot.v1.2.yaml`
