#!/usr/bin/env bash
set -euo pipefail
bash -lc 'source ci/_load_env.sh; ci/model_lock_guard.sh && ci/retrieval_smoke_guard.sh'