# Purpose
Utility scripts for development, testing, and deployment.

# Entrypoints & Commands
- Run individual scripts: `bash scripts/script_name.sh`
- All scripts: `make verify-all` (runs relevant scripts)

# Interfaces
- Bash scripts with `.sh` extension
- Python scripts for complex operations
- Environment variables from `.env`

# Constraints
- All scripts must be executable
- Source environment variables
- Use `set -euo pipefail` for safety

# Gotchas
- Scripts run in CI environment
- Must handle missing dependencies gracefully

# Pointers
- SSOT: `../docs/SSOT/ssot.v1.2.yaml`
