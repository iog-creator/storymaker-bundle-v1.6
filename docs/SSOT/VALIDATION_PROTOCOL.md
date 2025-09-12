# VALIDATION_PROTOCOL.md - StoryMaker + AgentPM Validation

## Validation Framework

### Core Principles
1. **Fail-Closed**: System fails safely when components are missing or misconfigured
2. **Dual Provider Evidence**: Both Groq and LM Studio must generate valid proofs
3. **Canonical Paths**: All evidence lives under `docs/proofs/agentpm/`
4. **SSOT Compliance**: All documentation under `docs/SSOT/` with rules synced to `.cursor/rules/`

### Validation Levels

#### Level 1: Environment Validation
- **Guard**: `ci/env_config_guard.sh`
- **Checks**: All required environment variables present
- **Required**: `GROQ_API_KEY`, `GROQ_MODEL`, `OPENAI_API_BASE`, `CHAT_MODEL`, `EMBEDDING_MODEL`, `EMBEDDING_DIMS`

#### Level 2: Mock Controls Validation
- **Guard**: `ci/no_mocks_env_guard.sh`
- **Checks**: `DISABLE_MOCKS=1`, `MOCK_LMS=0`
- **Purpose**: Ensure production mode, no fallback mocks

#### Level 3: Provider Split Validation
- **Guard**: `ci/provider_split_guard.sh`
- **Checks**: Groq for narrative, LM Studio for embeddings
- **Purpose**: Clear separation of creative vs retrieval providers

#### Level 4: Proofs Path Validation
- **Guard**: `ci/proofs_path_guard.sh`
- **Checks**: All proofs under `docs/proofs/agentpm/`
- **Purpose**: Prevent evidence drift to other locations

#### Level 5: SSOT Presence Validation
- **Guard**: `ci/ssot_guard.sh`
- **Checks**: Required SSOT files present
- **Required**: `MASTER_PLAN.md`, `ASBUILT.md`, `MANUAL.md`, `VALIDATION_PROTOCOL.md`

#### Level 6: Rules Presence Validation
- **Guard**: `ci/rules_presence_guard.sh`
- **Checks**: SSOT rules exist and synced to `.cursor/rules/`
- **Purpose**: Ensure Builder rails are active

### Level 7 — Model Lock
- Validate exact model IDs and embedding dims.
- Must match:  
  - Groq: `llama-3.3-70b-versatile`  
  - Chat: `qwen/qwen3-8b`  
  - Reasoning: `qwen/qwen3-4b-thinking-2507`  
  - Reranker: `qwen.qwen3-reranker-0.6b`  
  - Embeddings: `text-embedding-qwen3-embedding-0.6b` (dims=1024)

### Level 8 — Retrieval Smoke
- `/api/v1/search/embed` → length 1024, non-zero, different per text.
- `/api/v1/search/rerank` → scores sorted descending, provider=lm-studio.
- **QA endpoints validation**:
  - `/api/v1/qa/trope-budget` → `data.used > 0`, `data.notes` not empty, `latency_ms > 0`
  - `/api/v1/qa/promise-payoff` → `data.used > 0`, `data.notes` not empty, `latency_ms > 0`
  - **Fail if QA returns empty analysis** - "status:ok with empty data" prohibited

### Level 9 — Proof Integrity
- Proof files must be byte-for-byte canonical copies of responses.
- Compare `proof.sha256`.

#### Proof Hash Contract — `canon-v1`
Services MUST:
1) Compute `sha256` over the envelope **with `.proof` removed`, then JSON-dump with `sort_keys=True` and `separators=(",", ":")`.
2) Set `.proof.sha256` to that digest, `.proof.format="canon-v1"`, and `.proof.path` to the written proof file.
3) Write the **full** envelope (including `.proof`) with the same dump settings.
Guards SHALL recompute the digest by removing `.proof` and using the same dump settings for **both** the HTTP response and the proof file contents.

**Canonicalizer Discipline**: All proof hashing MUST use `ci/json_hash.py` as the single source of truth. No jq-based canonicalization is permitted. The `guards.canon.lint` target enforces this discipline and fails fast on any jq usage in guards or scripts.

#### Service Health Contract (guard-friendly)
Implement at least one health path per service. Recommended:
`/health` (simple 200), `/api/v1/health` (JSON payload), `/healthz` (k8s-style).
Preflight auto-detects orchestration's health path and passes if at least `REQ_OK`
endpoints are healthy (default 3). You may override with `ORCH_HEALTH_OVERRIDE`.

#### Preflight Ordering
Run tolerant health first; strict model checks are optional. Guards MUST NOT fail
before tolerant health completes. Enforce strict checks only with `PREFLIGHT_STRICT=1`.
WorldCore reload is disabled by default in `services.up`; set `WORLDCORE_RELOAD=1` if needed.

### Level 10 — Stability & Isolation
- Rerank-monotonic: strict ordering
- Soak-and-concurrency: ≥100 requests pass
- Provider-isolation: fail-closed on wrong provider
- Fresh-shell-env: all guards green in new shell

> `make verify-all` must include Levels 1–10.

### Evidence Requirements

#### LM Studio Evidence
```json
{
  "ok": true,
  "meta": {
    "ts": "2025-09-08T20:39:02Z",
    "endpoint": "http://127.0.0.1:1234/v1"
  }
}
```

#### Groq Narrative Evidence
```json
{
  "ok": true,
  "provider": "groq",
  "model": "llama-3.3-70b-versatile",
  "draft": "SEED:\n1. **Premise**: A group of strangers wakes up...",
  "meta": {
    "ts": "2025-09-08T20:39:04Z",
    "endpoint": "narrative:8001"
  }
}
```

### Validation Commands

#### Full Validation Suite
```bash
make verify-all     # Complete verification with evidence generation
make verify         # Run all guards (no evidence generation)
```

#### Individual Validation
```bash
make verify-lms     # LM Studio integration test
make verify-narrative # Groq creative generation test
make verify-preflight # Quality gates test
make verify-live    # End-to-end integration test
```

#### Guard Validation
```bash
make guards         # Run all 6 CI guards
./ci/env_config_guard.sh
./ci/no_mocks_env_guard.sh
./ci/provider_split_guard.sh
./ci/proofs_path_guard.sh
./ci/ssot_guard.sh
./ci/rules_presence_guard.sh
```

### Success Criteria

#### System is Valid When:
1. ✅ All 6 CI guards pass
2. ✅ Both LM Studio and Groq generate valid proofs
3. ✅ All evidence is in canonical path `docs/proofs/agentpm/`
4. ✅ SSOT documentation is complete and rules are synced
5. ✅ Environment is properly configured with no mocks
6. ✅ Provider split is enforced (Groq=creative, LM Studio=embeddings)

#### System Fails When:
1. ❌ Any guard fails with specific error message
2. ❌ Evidence is generated outside canonical path
3. ❌ Mock mode is enabled in production
4. ❌ Required environment variables are missing
5. ❌ SSOT documentation is incomplete
6. ❌ Rules are not synced to Builder rails

### Continuous Validation

The system enforces validation at multiple levels:
- **Bootstrap**: Initial validation during system setup
- **Runtime**: Guards run before major operations
- **CI/CD**: Automated validation in deployment pipeline
- **Manual**: On-demand validation via `make verify`
