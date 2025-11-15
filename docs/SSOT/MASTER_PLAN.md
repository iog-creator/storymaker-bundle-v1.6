# MASTER_PLAN.md — StoryMaker + AgentPM (v1.6 FINAL)

## 📖 Purpose

This document is the **Single Source of Truth (SSOT)** for the StoryMaker system with AgentPM integration.  
It defines the **canonical architecture**, **phases**, **acceptance criteria**, and **rebuild instructions**.  

If the system drifts or fails, **rebuilding from this plan must reproduce the intended state**.

> **Conceptual North Star**: see `docs/STORYMAKER_MASTER_PLAN.md` for roles, flows, and provider responsibilities.

---

## 1. Canonical Architecture (Locked)

## AI Roles & Providers (SSOT v1.2)

- **Creative (Narrative/Prose)** → **Groq**
  - Model: `llama-3.3-70b-versatile` (locked)
- **Verifier / Planner (AgentPM chat)** → **LM Studio**
  - Primary Chat: `qwen/qwen3-8b` (locked)
  - Reasoning Chat: `qwen/qwen3-4b-thinking-2507` (locked)
- **Retrieval**
  - Embeddings: `text-embedding-qwen3-embedding-0.6b` (locked, `dims=1024`)
  - Reranker: `qwen.qwen3-reranker-0.6b` (locked)

### Services
- **WorldCore**: Canon, propose/approve, entity graph  
- **Narrative**: Creative generation + trope/promise/payoff checks  
- **Screenplay**: Formatting, dialogue pacing, export (FDX/Fountain)  
- **Media**: Image generation, watermark metadata  
- **Interact**: NPC sessions, chat/WS layer

### Infrastructure
- **Postgres 17.5** (required, no fallback)  
- **Redis 7** (caching, ephemeral state)  
- **MinIO** (S3-compatible storage)  

## API Contract

- All public endpoints are under **`/api/v1/*`**.
- Envelope **v1.2** is mandatory for **every** success/error:
  ```json
  { "status": "ok"|"error",
    "data": { ... } | null,
    "error": { "code": "...", "message": "...", "details": {...} } | null,
    "meta": { "api_version":"v1.2","request_id":"uuid","provider":"groq|lm-studio|system",
              "model":"string","role":"creative|qa|retrieval|system","latency_ms":123,"created_at":"ISO-8601" },
    "proof": { "id":"uuid","path":"docs/proofs/agentpm/YYYY/MM/DD/ID.json","written":true,
               "sha256":"<hash of canonicalized response>" }
  }
```

## Guardrails

* **Provider Split**

  * Narrative → Groq only; QA/Retrieval → LM Studio only. Crossing providers is a **hard failure**.
* **Model Lock**

  * Exact IDs above are **required**; validated in CI.
* **Retrieval Invariants**

  * Embeddings must return `dims=1024`; reranker results must be sorted descending.
* **Proof Discipline**

  * Proof file must be a canonicalized byte-for-byte copy of the API response; guard compares `sha256`.
* **Fail-Closed Readiness**

  * `/api/v1/health` and `/api/v1/healthz` return **503** until Groq + LM Studio warmups succeed and DB is reachable.  

---

## 2. Phases

### Phase 1 — Core APIs (✅ Complete)
- WorldCore minimal API (`/propose`, `/approve`, `/canon/entity/:id`, `/graph`, `/health`)  
- Narrative outline endpoint with **ledger** + **trope budget**  
- Guards libraries (temporal, Allen)  
- Interact NPC WebSocket (`PROPOSE_FACT` fallback)  
- Screenplay/Media stubs with Envelope artifacts  
- CI gates wired; OpenAPI YAML and examples checked in  

### Phase 2 — AI & Content Generation (✅ Complete)
- Groq client: Creative only (no embeddings/rerank)  
- LM Studio client: Embeddings (Qwen 1024D), rerank, planning  
- `.env` locked: `GROQ_API_KEY`, `GROQ_MODEL=llama-3.3-70b-versatile`  
- Narrative tests: `provider:"groq"`, fail-fast if key missing  
- Verification: `make verify-all` produces LM Studio + Groq proofs  

### Phase 3 — Web UI (⏳ Pending)
- apps/webui scaffold (React/Tailwind)  
- Expose Narrative (Groq) + WorldCore (approve/canon)  
- Embed/retrieve flow (LM Studio)  
- Canvas view for story beats and canon entities  

### Phase 4 — Testing & QA (⏳ Pending)
- Expand acceptance tests to full suite  
- Add latency SLOs: Narrative p95 ≤ 3s, Embedding p95 ≤ 300ms  
- Add retrieval accuracy gates (flat-curve guard, rerank precision ≥0.75)  
- Manual acceptance checklist (writers' validation)

### Phase 5 — Deployment (⏳ Pending)
- Docker Compose bundle (Postgres, Redis, MinIO, services, webui)  
- Production env config (`DISABLE_MOCKS=1`)  
- CI/CD pipeline: verify-all → build → deploy  
- Documentation freeze; SSOT snapshot  

---

## Acceptance (Green Criteria)

* Narrative outline returns envelope v1.2 with `meta.provider:"groq"` and model `llama-3.3-70b-versatile`.
* QA and Retrieval endpoints return envelope v1.2 with `meta.provider:"lm-studio"`.
* `/api/v1/search/embed` returns `meta.embedding_dims == 1024`.
* Proofs saved only under `docs/proofs/agentpm/...` and `proof.sha256` matches API response.
* All guards pass under `make verify-all`, including:
  - env_config, no-mocks, provider-split, proofs-path, SSOT presence, rules presence
  - model-lock, retrieval-smoke, proof-integrity
  - rerank-monotonic (scores descending)
  - soak-and-concurrency (≥100 sequential + concurrent calls)
  - provider-isolation (fail-closed if provider misused)
  - fresh-shell-env (no manual sourcing required)  

---

## 4. Self-Bootstrap Instructions (Zero Manual Intervention)

### **One-Command Bootstrap**
```bash
git clone <repo>
cd storymaker-bundle-v1.6-unified-full
make bootstrap
```

The `make bootstrap` target handles **everything** automatically:
- Environment setup and validation
- Infrastructure startup (Docker services)
- LM Studio integration verification
- AgentPM workspace initialization
- Rules sync and enforcement
- Proofs path unification
- Complete system verification

### **Detailed Bootstrap Process**

1. **Environment Auto-Setup**
   ```bash
   # Automatically copies .env.example → .env
   # Validates required environment variables
   # Sets up AgentPM workspace structure
   ```

2. **Infrastructure Auto-Start**
   ```bash
   # Starts Docker services (Postgres, Redis, MinIO)
   # Waits for services to be ready
   # Validates database connectivity
   ```

3. **LM Studio Integration**
   ```bash
   # Detects LM Studio installation
   # Validates model availability (Qwen + embeddings)
   # Confirms API endpoint accessibility
   ```

4. **AgentPM Workspace Bootstrap**
   ```bash
   # Creates canonical proofs directory
   # Sets up workspace symlinks
   # Syncs SSOT rules to Cursor
   # Enforces all guardrails
   ```

5. **System Verification**
   ```bash
   # Runs complete verification suite
   # Generates both LM Studio and Groq proofs
   # Validates all quality gates
   # Confirms system is production-ready
   ```

### **Post-Bootstrap Usage**
```bash
# Start all services
make start

# Run verification
make verify-all

# Check status
make status
```

### **Troubleshooting**
If bootstrap fails, the system provides clear error messages and recovery steps:
- Missing dependencies → Installation instructions
- Service failures → Diagnostic commands
- Configuration issues → Environment validation
- Integration problems → Manual override options

---

## 5. Lessons Learned

- Never allow mocks in production — **fail-closed** required  
- Keep Groq = creative only; LM Studio = embeddings/rerank  
- Preserve SSOT: archive old docs, but MASTER_PLAN must always exist  
- Proofs are mandatory for audit and debugging  
- String audits should run in CI to prevent HF/mocks drift
- **API Key Protection**: Never commit real API keys to git; use .env.local for secrets
- **Environment Loading**: All verification scripts must source .env before running
- **AgentPM Verification**: Always use `make verify-all` as source of truth, never assume
- **Git Clean Safety**: API keys must be backed up outside repository before cleanup operations  

---

## 6. Next Steps

- Implement Phase 3 (Web UI) following this plan  
- Tighten acceptance tests with latency and accuracy gates  
- Finalize deployment profile and CI/CD integration  
