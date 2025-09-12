# Purpose
Doc sources. SSOT is here.

# Entrypoints & Commands
- Validate schemas: `jq -e . docs/schemas/envelope.v1.2.schema.json`
- Link check (optional): `lychee docs/**/*.md`

# Interfaces
- Authoritative SSOT: `docs/SSOT/ssot.v1.2.yaml`
- Contracts: `docs/SSOT/MASTER_PLAN.md`, `docs/SSOT/VALIDATION_PROTOCOL.md`

# Constraints
- Proof examples must show `proof.sha256`.

# Gotchas
- SSOT files are authoritative; do not modify without validation.

# Pointers
- Master plan: `docs/SSOT/MASTER_PLAN.md`
