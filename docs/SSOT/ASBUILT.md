# ASBUILT.md - StoryMaker + AgentPM System

## System Architecture (As Built)

### Current Implementation Status
- **StoryMaker Services**: All 5 services operational (worldcore, narrative, screenplay, media, interact)
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

### Operational Status
- ✅ All services verified and operational
- ✅ Both AI providers generating valid proofs
- ✅ Complete verification suite passing
- ✅ Production-ready with fail-closed architecture
