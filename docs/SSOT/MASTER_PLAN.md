# MASTER_PLAN.md — StoryMaker + AgentPM (v1.6 FINAL)

## 📖 Purpose

This document is the **Single Source of Truth (SSOT)** for the StoryMaker system with AgentPM integration.  
It defines the **canonical architecture**, **phases**, **acceptance criteria**, and **rebuild instructions**.  

If the system drifts or fails, **rebuilding from this plan must reproduce the intended state**.

---

## 1. Canonical Architecture (Locked)

### AI Roles
- **Groq 70B (`llama-3.3-70b-versatile`)** → **Creative generation ONLY**  
  (Prose, dialogue, rewrites, narrative scenes)
- **LM Studio (local Qwen models)** → **Everything else**  
  (Embeddings [1024-dim], reranking, QA, structure, planning)

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

### Guardrails
- **Envelope System v1.1**: All responses = `{status, data, error, meta}`  
- **Proof Capture**: Every operation logs JSON envelope in `docs/proofs/`  
- **Quality Gates**: Preflight, commit hygiene, SSOT presence, verify-all  
- **Mocks**: ❌ Disabled (fail-closed; `MOCK_LMS=0` enforced)  
- **HF References**: ❌ Removed; Groq API only  

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

## 3. Acceptance Criteria

### Global
- DB fail-fast: `/health` returns ok only if DB reachable  
- Envelope-only responses, no raw output  
- Proofs in `docs/proofs/agentpm/` for every verification step  
- No mocks, no HF references  

### Groq
- Service refuses to start without `GROQ_API_KEY`  
- Requests fail if model is not 70B (`llama-3.3-70b-versatile`)  
- Narrative responses always include `"provider":"groq"`  

### LM Studio
- Embeddings = 1024-dim Qwen vectors  
- Reranking functional with chat reranker  
- `make verify-lms` confirms connection to `http://127.0.0.1:1234/v1`  

### AgentPM
- `make verify-all` passes: config-check, preflight, live, narrative proof  
- Preflight gates: commit hygiene, SSOT presence, envelope validation  
- Proof envelopes show both Groq + LM Studio evidence  

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

---

## 6. Next Steps

- Implement Phase 3 (Web UI) following this plan  
- Tighten acceptance tests with latency and accuracy gates  
- Finalize deployment profile and CI/CD integration  
