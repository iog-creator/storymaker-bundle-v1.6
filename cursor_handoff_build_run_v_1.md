# Cursor Handoff — Build & Run (v1.6)

This is the **single source of truth** for spinning up StoryMaker locally with Cursor (or any coding agent that reads `AGENTS.md`). It is aligned with **StoryMaker SRS v1.1** and our **OpenAPI 3.1**. **Postgres 17 is REQUIRED** (no in-memory fallback). `make api.up` **auto-runs DB migration** before services start.

---

## 0) Preflight

- OS: macOS 13+ / Linux
- Tools: Python 3.11+, Node 20+, pnpm 9+, Docker, **Postgres 17**, **Redis 7**, **MinIO**
- Clone repo → open in Cursor
- Copy `.env.example` → `.env`, set `POSTGRES_DSN`

> Health gate: `GET http://localhost:8000/health` must return `{ data: { ok: true } }` **only** when DB is reachable.

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
  sql/001_init.sql
  scripts/db_migrate.py
  AGENTS.md
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
```

---

## 3) Makefile (core targets)

```
setup: ## install hooks and toolchains
	pipx install uv || true
	pipx install pre-commit || true
	pre-commit install
	corepack enable || true
	corepack prepare pnpm@9.0.0 --activate || true

# start infra
db.up:
	docker compose up -d db redis minio

# apply schema (runs automatically inside api.up)
db.migrate:
	uv venv && uv pip install psycopg[binary] && \
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} \
	uv run python scripts/db_migrate.py sql/001_init.sql

# run all FastAPI services (dev) — MIGRATES FIRST
api.up:
	$(MAKE) db.migrate
	uv venv && uv pip install -r requirements-dev.txt
	uv run uvicorn services.worldcore.main:app --port 8000 --reload &
	uv run uvicorn services.narrative.main:app --port 8001 --reload &
	uv run uvicorn services.screenplay.main:app --port 8002 --reload &
	uv run uvicorn services.media.main:app --port 8003 --reload &
	uv run uvicorn services.interact.main:app --port 8004 --reload &

# web ui
web.dev:
	cd apps/webui && pnpm install && pnpm dev

# seed canon (propose+approve → CANON)
seed.world:
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} \
	uv run python -m services.worldcore.seed docs/seeds/*.json

test:
	pytest -q
```

---

## 4) First Run (happy path)

1. `make setup`  →  `make db.up`
2. `export POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker`
3. `make api.up`  (auto-migrates DB, starts services :8000..:8004)
4. `make seed.world`  (loads demo seeds; ends in **CANON**)
5. (optional) `make -C apps/webui dev` or `make web.dev`
6. Verify health:
   ```bash
   curl -s localhost:8000/health | jq
   ```
7. Propose → Approve (idempotent):
   ```bash
   curl -s localhost:8000/propose -H 'content-type: application/json' \
     -d '{"id":"p_harbor","type":"Place","name":"Harbor of Lumen","status":"DRAFT","traits":{},"world_id":"w_eldershore"}' | jq
   # copy the "cid" → approve twice
   curl -s localhost:8000/approve -H 'content-type: application/json' -d '{"cid":"<CID>"}' | jq
   curl -s localhost:8000/approve -H 'content-type: application/json' -d '{"cid":"<CID>"}' | jq  # same pointer
   ```

---

## 5) Acceptance Tests (v1.6)

- **DB Health Gate** → `/health` returns `{ok:true}` only when DB reachable.
- **Idempotent Approval** → double-approve same CID → identical pointer.
- **Temporal Guards** → unit tests pass (`services/guards/{temporal,allen_lite}.py`).
- **Promise/Payoff** → orphans/extraneous flagged by `/narrative/outline`.
- **Trope Budget** → clichés over threshold yield `issues: [{type: "trope_budget"}]`.
- **Screenplay Export** → `/screenplay/export` returns artifact envelope (FDX/Fountain).
- **NPC Session (WS)** → unknown/invent prompts return `PROPOSE_FACT`; canon not mutated.
- **Visual Generate** → returns watermark metadata `{present:true}`.

---

## 6) Cursor Agent Rules (how to behave)

- Obey **SRS v1.1** and root **AGENTS.md**.
- **DB is mandatory**; fail fast if not reachable.
- Never mutate canon directly; only via `/approve` after a proposal.
- Always emit a single **Envelope** (`status/data/error/meta`).
- Run style gates (Vale/Proselint/LanguageTool) before large text proposals.
- Prefer **Harmon-8** or **Kishōtenketsu** to diversify beats by default.

---

## 7) Troubleshooting

- **401/404/422/429** → see OpenAPI examples under `docs/openapi/examples/`.
- **DB connection** → verify `POSTGRES_DSN` and `docker compose ps` for `db`.
- **Health** → `/health` must be `ok:true` only if DB reachable.
- **FDX** → if a tool fails to open it, validate Fountain source and slugs.

---

## 8) Deliverables for PR #0001 (scaffold)

- WorldCore minimal API (`/propose`, `/approve`, `/canon/entity/:id`, `/graph`, `/health`).
- Narrative outline endpoint with **ledger** + **trope budget** issues surfaced.
- Guards libraries present and tested (`temporal`, `allen_lite`).
- Interact NPC WebSocket with **PROPOSE_FACT** behavior for unknowns.
- Screenplay/Media stubs returning Envelope artifacts + watermark meta.
- WebUI canvas demo present and running.
- CI gates wired; OpenAPI YAML and examples included.

**Done = merged when all acceptance tests pass and OpenAPI lint has zero errors.**

