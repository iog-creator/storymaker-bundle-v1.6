# Deprecated utilities (do not use)

## Canonicalization
- **jq-based canonicalization in ci/json_hash.sh** (removed)
  - **Use:** `ci/json_hash.py` only
  - **Reason:** Caused hash drift due to different canonicalization output
  - **Replaced:** Shell wrapper now delegates to Python canonicalizer

## Migration
All code must use `ci/json_hash.py` as the single source of truth for proof hashing.
