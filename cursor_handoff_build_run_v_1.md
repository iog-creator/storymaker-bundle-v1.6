# Cursor Handoff — Build & Run (v1.6) + AgentPM Prototype

This is the **single source of truth** for spinning up StoryMaker locally with Cursor (or any coding agent that reads `AGENTS.md`). It is aligned with **StoryMaker SRS v1.1** and our **OpenAPI 3.1**. **Postgres 17 is REQUIRED** (no in-memory fallback). `make api.up` **auto-runs DB migration** before services start.

## 🚀 AgentPM Prototype Status

**This repository serves as a real-world testbed for the AgentPM prototype system.** StoryMaker is the application being used to validate AgentPM's capabilities in a production-like environment.

### AgentPM Core Features (✅ WORKING)
- **Local-First AI**: LM Studio integration with 22 models loaded
- **Quality Gates**: Preflight checks, SSOT presence, commit hygiene
- **Envelope System**: JSON v1.1 format validation and proof capture
- **Embedding Pipeline**: Qwen 1024-dimensional vectors (corrected from Nomic 768)
- **Reranking System**: Chat-based relevance scoring
- **Proof Capture**: Automatic audit trail in `docs/proofs/agentpm/`

### Quick AgentPM Start
```bash
# One-command setup (includes AgentPM verification)
make start

# Check AgentPM system health
make status

# Run full AgentPM verification suite
make verify-all
```

### AgentPM Documentation
- `AGENTPM_DEVELOPMENT.md` - Prototype development status and testing
- `QUICK_START.md` - 5-minute setup guide for new users
- `USER_GUIDE.md` - Non-technical user guide for writers

---

## 0) Preflight

- OS: macOS 13+ / Linux
- Tools: Python 3.11+, Node 20+, pnpm 9+, Docker, **Postgres 17**, **Redis 7**, **MinIO**
- **LM Studio**: Required for AgentPM (download from lmstudio.ai, load chat model, start server on port 1234)
- Clone repo → open in Cursor
- Copy `.env.example` → `.env`, set `POSTGRES_DSN`

> Health gate: `GET http://localhost:8000/health` must return `{ data: { ok: true } }` **only** when DB is reachable.
> AgentPM gate: `make verify-all` must pass all quality gates (LM Studio, preflight, live verification).

---

## 1) Directory Layout (expected)

```
storymaker/
  apps/webui/
  services/{worldcore,narrative,screenplay,guards,media,interact}/
  docs/
    openapi/storymaker.core.yaml
    openapi/examples/*.json
    seeds/{eldershore.json,angels.json}
    SSOT/
    proofs/agentpm/          # AgentPM proof capture
  sql/001_init.sql
  scripts/
    db_migrate.py
    bootstrap.sh             # AgentPM bootstrap system
    lm_api.py               # LM Studio client
    preflight_gate.sh       # AgentPM quality gates
    run.sh                  # Environment wrapper
  tools/
    single_envelope_guard.sh # AgentPM envelope validation
  .agentpm_workspace/       # AgentPM prototype (gitignored)
  AGENTS.md
  AGENTPM_DEVELOPMENT.md    # AgentPM prototype status
  QUICK_START.md           # User-friendly setup guide
  USER_GUIDE.md            # Non-technical user guide
  README.md
```

---

## 2) .env.example (copy → .env)

```
POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker
REDIS_URL=redis://localhost:6379
S3_ENDPOINT=http://localhost:9000
S3_BUCKET=storymaker
S3_ACCESS_KEY=story
S3_SECRET_KEY=storysecret
OAUTH_ISSUER=http://localhost:8000
# AgentPM Configuration
MOCK_LMS=0
OPENAI_API_BASE=http://127.0.0.1:1234/v1
EMBEDDING_DIMS=1024
OPENAI_API_KEY=dummy-key
DATABASE_URL=postgresql://story:story@localhost:5432/storymaker
CHAT_MODEL=llama-3.2-3b-instruct
EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
```

---

## 3) Makefile (core targets)

```
# AgentPM User-Friendly Commands
start: ## One-command setup (includes AgentPM verification)
	@bash scripts/bootstrap.sh start

stop: ## Stop all services
	@bash scripts/bootstrap.sh stop

status: ## Check system health (includes AgentPM)
	@bash scripts/bootstrap.sh status

help: ## Show all commands
	@echo "StoryMaker - AI-Powered Creative Writing Platform"
	@echo "Quick Start: make start | make status | make stop"

# AgentPM Verification Suite
verify-all: ## Run full AgentPM verification
	@echo "=== STORYMAKER VERIFICATION ==="
	@$(MAKE) config-check
	@$(MAKE) verify-lms
	@$(MAKE) verify-preflight
	@$(MAKE) verify-live
	@echo "✅ ALL VERIFICATIONS PASSED"

verify-lms: ## Test LM Studio integration
	@$(RUN_WRAP) python3 scripts/lm_api.py models | jq -e '.status=="success"' >/dev/null && \
	echo "OK: LM Studio integration working" || (echo "FAIL: LM Studio integration"; exit 1)

verify-preflight: ## Test AgentPM quality gates
	@$(RUN_WRAP) bash scripts/preflight_gate.sh | jq -e '.status=="success"' >/dev/null && \
	echo "OK: preflight" || (echo "FAIL: preflight"; exit 1)

verify-live: ## Test service health
	@$(RUN_WRAP) bash scripts/verify_live_simple.sh | jq -e '.status=="success"' >/dev/null && \
	echo "OK: verify-live" || (echo "FAIL: verify-live"; exit 1)

# Legacy StoryMaker Commands
setup: ## install hooks and toolchains
	pipx install uv || true
	pipx install pre-commit || true
	pre-commit install
	corepack enable || true
	corepack prepare pnpm@9.0.0 --activate || true

db.up: ## start infrastructure
	docker compose up -d db redis minio

api.up: ## run all FastAPI services (dev) — MIGRATES FIRST
	$(MAKE) setup-real
	$(MAKE) db.migrate
	uv venv --clear && uv pip install -r requirements-dev.txt
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6379} bash scripts/start_service.sh worldcore 8000 "uv run uvicorn services.worldcore.main:app --port 8000 --reload"
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6379} bash scripts/start_service.sh narrative 8001 "uv run uvicorn services.narrative.main:app --port 8001 --reload"
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6379} bash scripts/start_service.sh screenplay 8002 "uv run uvicorn services.screenplay.main:app --port 8002 --reload"
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6379} bash scripts/start_service.sh media 8003 "uv run uvicorn services.media.main:app --port 8003 --reload"
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6379} bash scripts/start_service.sh interact 8004 "uv run uvicorn services.interact.main:app --port 8004 --reload"

api.down: ## stop all services
	@echo "Stopping services on 8000-8004 if present..."
	@bash scripts/kill_by_port.sh 8000 || true
	@bash scripts/kill_by_port.sh 8001 || true
	@bash scripts/kill_by_port.sh 8002 || true
	@bash scripts/kill_by_port.sh 8003 || true
	@bash scripts/kill_by_port.sh 8004 || true

api.restart: api.down api.up ## restart all services

seed.world: ## seed canon (propose+approve → CANON)
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} uv run python -m services.worldcore.seed docs/seeds/*.json

test: ## run tests
	pytest -q
```

---

## 4) First Run (happy path)

### AgentPM + StoryMaker Setup
1. **Start LM Studio**: Load chat model, start server on port 1234
2. **One-command setup**: `make start` (includes AgentPM verification)
3. **Verify everything**: `make status` (shows LM Studio, DB, services)
4. **Run AgentPM tests**: `make verify-all` (quality gates, preflight, live)

### Legacy StoryMaker Setup (if needed)
1. `make setup`  →  `make db.up`
2. `export POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker`
3. `make api.up`  (auto-migrates DB, starts services :8000..:8004)
4. `make seed.world`  (loads demo seeds; ends in **CANON**)
5. (optional) `make -C apps/webui dev` or `make web.dev`

### Verification Commands
```bash
# AgentPM system health
make status

# Full AgentPM verification suite
make verify-all

# Individual AgentPM components
make verify-lms        # LM Studio integration
make verify-preflight  # Quality gates
make verify-live       # Service health

# StoryMaker health
curl -s localhost:8000/health | jq
```

### Test StoryMaker API
```bash
# Propose → Approve (idempotent)
curl -s localhost:8000/propose -H 'content-type: application/json' \
  -d '{"id":"p_harbor","type":"Place","name":"Harbor of Lumen","status":"DRAFT","traits":{},"world_id":"w_eldershore"}' | jq
# copy the "cid" → approve twice
curl -s localhost:8000/approve -H 'content-type: application/json' -d '{"cid":"<CID>"}' | jq
curl -s localhost:8000/approve -H 'content-type: application/json' -d '{"cid":"<CID>"}' | jq  # same pointer
```

---

## 5) Acceptance Tests (v1.6)

### StoryMaker Core Tests
- **DB Health Gate** → `/health` returns `{ok:true}` only when DB reachable.
- **Idempotent Approval** → double-approve same CID → identical pointer.
- **Temporal Guards** → unit tests pass (`services/guards/{temporal,allen_lite}.py`).
- **Promise/Payoff** → orphans/extraneous flagged by `/narrative/outline`.
- **Trope Budget** → clichés over threshold yield `issues: [{type: "trope_budget"}]`.
- **Screenplay Export** → `/screenplay/export` returns artifact envelope (FDX/Fountain).
- **NPC Session (WS)** → unknown/invent prompts return `PROPOSE_FACT`; canon not mutated.
- **Visual Generate** → returns watermark metadata `{present:true}`.

### AgentPM Prototype Tests
- **LM Studio Integration** → `make verify-lms` passes (22 models loaded).
- **Quality Gates** → `make verify-preflight` passes (LM models, chat, SSOT, commit hygiene).
- **Envelope System** → JSON v1.1 format validation working.
- **Proof Capture** → Envelopes stored in `docs/proofs/agentpm/`.
- **Embedding Pipeline** → Qwen 1024-dimensional vectors working.
- **Reranking System** → Chat-based relevance scoring functional.
- **Service Health** → All 5 StoryMaker services verified.
- **Bootstrap System** → One-command setup working (`make start`).

---

## 6) Cursor Agent Rules (how to behave)

### StoryMaker Rules
- Obey **SRS v1.1** and root **AGENTS.md**.
- **DB is mandatory**; fail fast if not reachable.
- Never mutate canon directly; only via `/approve` after a proposal.
- Always emit a single **Envelope** (`status/data/error/meta`).
- Run style gates (Vale/Proselint/LanguageTool) before large text proposals.
- Prefer **Harmon-8** or **Kishōtenketsu** to diversify beats by default.

### AgentPM Development Rules
- **This is AgentPM prototype development** - StoryMaker is the testbed.
- Always use **real services** (no mocks) - `MOCK_LMS=0`.
- Use **LM Studio CLI** the same way as Gemini CLI for LLM commands.
- Run commands through `scripts/run.sh bash -lc` to load environment.
- Activate AgentPM virtual environment: `source .agentpm_workspace/agentpmvenv/bin/activate`.
- All operations must return **envelope format** with proper JSON structure.
- Test AgentPM workflows with `make verify-all` before making changes.
- Capture proofs in `docs/proofs/agentpm/` for all operations.

---

## 7) Troubleshooting

### StoryMaker Issues
- **401/404/422/429** → see OpenAPI examples under `docs/openapi/examples/`.
- **DB connection** → verify `POSTGRES_DSN` and `docker compose ps` for `db`.
- **Health** → `/health` must be `ok:true` only if DB reachable.
- **FDX** → if a tool fails to open it, validate Fountain source and slugs.

### AgentPM Issues
- **LM Studio not found** → Check port 1234, verify models loaded, restart LM Studio.
- **Preflight failures** → Run `make verify-lms` and `make verify-preflight` individually.
- **Envelope errors** → Check JSON format, validate schema with `make envelope-guard-ok`.
- **Service failures** → Run `make status` to check all components.
- **Environment issues** → Use `scripts/run.sh bash -lc` to load proper environment.
- **Virtual environment** → Activate with `source .agentpm_workspace/agentpmvenv/bin/activate`.

### Debug Commands
```bash
# Check everything
make status

# Test individual components
make verify-lms
make verify-preflight
make verify-live

# View detailed logs
docker compose logs -f

# Check envelope format
make envelope-guard-ok
make envelope-guard-bad
```

---

## 8) Deliverables for PR #0001 (scaffold)

### StoryMaker Core
- WorldCore minimal API (`/propose`, `/approve`, `/canon/entity/:id`, `/graph`, `/health`).
- Narrative outline endpoint with **ledger** + **trope budget** issues surfaced.
- Guards libraries present and tested (`temporal`, `allen_lite`).
- Interact NPC WebSocket with **PROPOSE_FACT** behavior for unknowns.
- Screenplay/Media stubs returning Envelope artifacts + watermark meta.
- WebUI canvas demo present and running.
- CI gates wired; OpenAPI YAML and examples included.

### AgentPM Prototype (✅ COMPLETED)
- **Local-First AI Integration**: LM Studio with 22 models loaded and verified.
- **Quality Gates System**: Preflight checks, SSOT presence, commit hygiene.
- **Envelope System**: JSON v1.1 format validation and proof capture.
- **Embedding Pipeline**: Qwen 1024-dimensional vectors (corrected from Nomic).
- **Reranking System**: Chat-based relevance scoring functional.
- **Bootstrap System**: One-command setup (`make start`) with comprehensive health checks.
- **User Documentation**: Clear guides for different user levels.
- **Proof Capture**: Automatic audit trail in `docs/proofs/agentpm/`.
- **Service Integration**: All 5 StoryMaker services verified as testbed.

**Done = merged when all acceptance tests pass and OpenAPI lint has zero errors.**
**AgentPM = prototype validated in real-world scenario with StoryMaker.**

