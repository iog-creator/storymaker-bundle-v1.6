# ASBUILT.md - StoryMaker + AgentPM System

## System Architecture (As Built)

### Current Implementation Status
- **StoryMaker Services**: All 5 services operational (worldcore, narrative, screenplay, media, interact)
- **Orchestration Service**: Port 8700, coordinates full story generation flow
- **WebUI**: React/Vite frontend on port 5173, fully functional with real-time flow execution
- **AgentPM Integration**: Fully integrated with self-bootstrap capabilities
- **AI Providers**: Groq (creative) + LM Studio (embeddings/rerank)
- **Database**: PostgreSQL with proper schema
- **Infrastructure**: Docker Compose with Redis, MinIO

### Deployment Configuration
- **Environment**: Production-ready with fail-closed guards
- **Proofs**: Canonical path `docs/proofs/agentpm/`
- **Rules**: SSOT rules synced to `.cursor/rules/`
- **Verification**: Complete test suite with dual provider evidence

### Key Components
1. **Self-Bootstrap**: `make bootstrap` for zero manual intervention
2. **Quality Gates**: 6 CI guards enforcing production standards
3. **Provider Split**: Groq for creative, LM Studio for embeddings
4. **Mock Controls**: `DISABLE_MOCKS=1`, `MOCK_LMS=0` enforced
5. **SSOT Compliance**: All documentation under `docs/SSOT/`
6. **API Key Protection**: Real keys in .env.local, dummy keys in .env for git
7. **Environment Loading**: All scripts source .env before execution
8. **Verification-First**: AgentPM verification as source of truth
9. **WebUI Integration**: Full orchestration flow with real-time story generation
10. **Orchestration Layer**: LangGraph-based flow coordination between services

### WebUI & Orchestration Integration
- **Frontend**: React/Vite application with drag-and-drop story beats
- **Flow Runner**: Real-time story generation with premise input
- **Orchestration**: LangGraph-based flow coordination on port 8700
- **Service Communication**: RESTful APIs between WebUI → Orchestration → Backend Services
- **Real-time Updates**: Live status updates and progress indicators
- **QA Integration**: Automatic trope budget and promise/payoff analysis
- **Approval Workflow**: Automated story approval based on QA results

### Operational Status
- ✅ All services verified and operational
- ✅ Both AI providers generating valid proofs
- ✅ Complete verification suite passing
- ✅ Production-ready with fail-closed architecture
- ✅ WebUI fully functional with orchestration integration
- ✅ End-to-end story generation flow operational

## Runtime (v1.2)

- **Services & Ports**
  - WorldCore (QA/Retrieval): `:8000`
  - Narrative (Creative): `:8001`
  - Orchestration: `:8700`
  - WebUI: `:5173`
- **Public API**: `/api/v1/*` only (legacy routes emit `Deprecation` + `Sunset`).

## Evidence & Proofs

- All endpoints emit envelope v1.2 and write proofs to `docs/proofs/agentpm/...`.
- `proof.sha256` equals the canonicalized API response hash.
- Retrieval evidence: embeddings (`dims=1024`) and reranker (descending scores).

## CI/Guards (As-Built)

- `model_lock_guard.sh` (exact model IDs)
- `retrieval_smoke_guard.sh` (dims=1024 + sorted rerank)
- `envelope_conformance_guard.sh` (role/provider/model + non-empty payloads)
- `proof_integrity_guard.sh` (response vs proof hash)
- `provider_isolation_guard.sh` (fail-closed on wrong provider)
- `fresh_shell_env_guard.sh` (env auto-load)
- Included in `make verify-all`

## PR-005X — SSOT v1.2 Lock-In + Stability Guards

- **Changes**
  - Locked all model IDs (Groq + Qwen family)
  - Standardized `/api/v1/*` endpoints
  - Enforced envelope v1.2 with `proof.sha256`
  - Added guards: model-lock, retrieval-smoke, proof-integrity, rerank-monotonic, soak-concurrency, provider-isolation, fresh-shell-env
- **Evidence**
  - Narrative proof: envelope v1.2 with provider `groq`
  - QA trope proof: provider `lm-studio`, non-empty data
  - Embedding proof: `dims=1024`
  - Rerank proof: scores sorted
- **Result**
  - All guards pass
  - Fresh shell environment validated
  - Services stable under soak/concurrency
