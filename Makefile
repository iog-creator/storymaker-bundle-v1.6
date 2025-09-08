
# === Environment Wrapper (AgentPM Integration) ===
RUN_WRAP := scripts/run.sh

# === StoryMaker Core Setup ===
setup:
	pipx install uv || true
	pipx install pre-commit || true
	pre-commit install || true
	corepack enable || true
	corepack prepare pnpm@9.0.0 --activate || true
	@echo 'Setup complete'

# === User-Friendly Bootstrap ===
.PHONY: start stop status help
start:
	@bash scripts/bootstrap.sh start

stop:
	@bash scripts/bootstrap.sh stop

status:
	@bash scripts/bootstrap.sh status

help:
	@echo "StoryMaker - AI-Powered Creative Writing Platform"
	@echo ""
	@echo "Quick Start:"
	@echo "  make start     - Start StoryMaker (one command)"
	@echo "  make status    - Check if everything is running"
	@echo "  make stop      - Stop all services"
	@echo ""
	@echo "Development:"
	@echo "  make setup     - Install development tools"
	@echo "  make test      - Run tests"
	@echo "  make restart   - Restart services"
	@echo ""
	@echo "Advanced:"
	@echo "  make verify-all - Run full verification suite"
	@echo "  make logs      - View service logs"
	@echo ""
	@echo "For new users, just run: make start"

# === Auto-configure Real Services ===
setup-real:
	@echo "🔧 Auto-configuring real services (disabling mock mode)..."
	@bash scripts/auto_setup_real_services.sh
	@echo "✅ Real services configured automatically"

# === Infrastructure ===
db.up:
	docker compose up -d db redis minio

db.migrate:
	uv venv --clear && uv pip install psycopg[binary] && POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} uv run python scripts/db_migrate.py sql/001_init.sql

api.up:
	$(MAKE) setup-real
	$(MAKE) db.migrate
	uv venv --clear && uv pip install -r requirements-dev.txt
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6380} bash scripts/start_service.sh worldcore 8000 "uv run uvicorn services.worldcore.main:app --port 8000 --reload"
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6380} bash scripts/start_service.sh narrative 8001 "uv run uvicorn services.narrative.main:app --port 8001 --reload"
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6380} bash scripts/start_service.sh screenplay 8002 "uv run uvicorn services.screenplay.main:app --port 8002 --reload"
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6380} bash scripts/start_service.sh media 8003 "uv run uvicorn services.media.main:app --port 8003 --reload"
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} REDIS_URL=$${REDIS_URL:-redis://localhost:6380} bash scripts/start_service.sh interact 8004 "uv run uvicorn services.interact.main:app --port 8004 --reload"

.PHONY: api.down api.restart
api.down:
	@echo "Stopping services on 8000-8004 if present..."
	@bash scripts/kill_by_port.sh 8000 || true
	@bash scripts/kill_by_port.sh 8001 || true
	@bash scripts/kill_by_port.sh 8002 || true
	@bash scripts/kill_by_port.sh 8003 || true
	@bash scripts/kill_by_port.sh 8004 || true

api.restart: api.down api.up

seed.world:
	POSTGRES_DSN=$${POSTGRES_DSN:-postgresql://story:story@localhost:5432/storymaker} uv run python -m services.worldcore.seed docs/seeds/*.json

test:
	pytest -q

# === AgentPM Integration (Local-First AI) ===
.PHONY: config-check lms-ping lms-chat verify-lms preflight verify-preflight

config-check:
	@$(RUN_WRAP) bash -lc 'echo "env ok"'

lms-ping:
	@$(RUN_WRAP) python3 scripts/lm_api.py models | jq

lms-chat:
	@$(RUN_WRAP) python3 scripts/lm_api.py chat --prompt "ping" | jq

verify-lms:
	@$(RUN_WRAP) python3 scripts/lm_api.py models | jq -e '.status=="success"' >/dev/null && \
	echo "OK: LM Studio integration working" || (echo "FAIL: LM Studio integration"; exit 1)

preflight:
	@$(RUN_WRAP) bash scripts/preflight_gate.sh | jq

verify-preflight:
	@$(RUN_WRAP) bash scripts/preflight_gate.sh | jq -e '.status=="success"' >/dev/null && \
	echo "OK: preflight" || (echo "FAIL: preflight"; exit 1)

# === Verification & Quality Gates ===
.PHONY: verify-live verify-all

verify-live:
	@$(RUN_WRAP) bash scripts/verify_live_simple.sh | jq -e '.status=="success"' >/dev/null && \
	echo "OK: verify-live" || (echo "FAIL: verify-live"; exit 1)

verify-all:
	@echo "=== STORYMAKER VERIFICATION ==="
	@echo "1. Config check..."
	@$(MAKE) config-check
	@echo "2. LM Studio check..."
	@$(MAKE) verify-lms
	@echo "3. Preflight check..."
	@$(MAKE) verify-preflight
	@echo "4. Live verification..."
	@$(MAKE) verify-live
	@echo "✅ ALL VERIFICATIONS PASSED"

# === Envelope System ===
.PHONY: envelope-guard-ok envelope-guard-bad

envelope-guard-ok:
	@echo '{"status":"success","data":{},"error":{"message":""},"meta":{"smoke_score":0.0}}' \
	| bash tools/single_envelope_guard.sh | jq -e '.status=="success"' >/dev/null && \
	echo "OK: guard passed object" || (echo "FAIL: guard"; exit 1)

envelope-guard-bad:
	@echo 'not json' | bash tools/single_envelope_guard.sh | jq -e '.status=="error"' >/dev/null && \
	echo "OK: guard rejected invalid input" || (echo "FAIL: guard bad"; exit 1)
