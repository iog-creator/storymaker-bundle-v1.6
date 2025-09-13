# StoryMaker — AGENTS.md (Index)

This repo uses **directory-scoped AGENTS.md** files. The nearest file guides agents for that area.

## Map
- `services/narrative/AGENTS.md` — creative (Groq)
- `services/worldcore/AGENTS.md` — QA/Retrieval (LM Studio)
- `services/orchestration/AGENTS.md` — graph host
- `apps/webui/AGENTS.md` — frontend
- `ci/AGENTS.md` — guards
- `docs/AGENTS.md` — SSOT/docs

## Global Defaults
- Envelope v1.2 + `proof.sha256` required
- Provider split enforced (Groq vs LM Studio)
- `/api/v1/*` endpoints only

## Quick Start
```bash
# Bootstrap everything
make bootstrap

# Start all services
make start

# Run all guards
make guards

# Full verification
make verify-all

# Live monitoring dashboard
make ui.live
```

## SSOT v1.2 Requirements
- **Envelope v1.2 mandatory** - all responses must include `status`, `data`, `error`, `meta`, `proof`
- **Proof SHA256 validation** - `proof.sha256` must match canonicalized response
- **Provider isolation** - Groq for creative, LM Studio for QA/retrieval
- **Model lock** - exact model IDs required and validated
- **QA validation** - non-empty analysis required, `latency_ms > 0`

## Environment Setup
```bash
# Groq (Creative Generation)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# LM Studio (QA & Retrieval)
OPENAI_API_BASE=http://127.0.0.1:1234/v1
OPENAI_API_KEY=lm-studio
CHAT_MODEL_PRIMARY=qwen/qwen3-8b
CHAT_MODEL_REASON=qwen/qwen3-4b-thinking-2507
RERANKER_MODEL=qwen.qwen3-reranker-0.6b
EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
EMBEDDING_DIMS=1024

# Production Controls
DISABLE_MOCKS=1
MOCK_LMS=0
```

## Live Monitoring Dashboard

The live dashboard provides real-time visual monitoring of all StoryMaker systems:

```bash
# Launch live dashboard
make ui.live
# Press 'q' to exit
```

**Dashboard Features:**
- **8 monitoring tiles** with 1-second refresh
- **Color-coded status**: Green (healthy), Yellow (warnings), Red (errors)
- **Live file watching** with blinking indicators on changes
- **Real-time guard execution** showing pass/fail status
- **Service health checks** for LM Studio and Groq
- **Proof statistics** and document change tracking

**Monitored Systems:**
- LM Studio (health + model info)
- Groq (environment validation)
- AgentPM (SSOT document changes)
- StoryMaker (implementation status)
- SSOT Rules (.mdc file count)
- Envelopes & Proofs (statistics + age)
- Docs Autosync (canonicalization status)
- Rerank & QA Guards (live execution results)