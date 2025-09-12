
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

setup.exec: ## one-time: ensure helper scripts are executable
	@chmod +x ci/json_hash.py || true
	@chmod +x ci/preflight_cross.sh || true
	@chmod +x ci/health_matrix.sh || true
	@chmod +x ci/test_canonicalizer.sh || true
	@chmod +x ci/weekly_sweep.sh || true
	@echo "exec bits ok"

# === User-Friendly Bootstrap ===
.PHONY: bootstrap start stop status help
bootstrap:
	@bash scripts/auto_bootstrap.sh

start:
	@bash scripts/bootstrap.sh start

stop:
	@bash scripts/bootstrap.sh stop

status:
	@bash scripts/bootstrap.sh status

help:
	@echo "StoryMaker - AI-Powered Creative Writing Platform"
	@echo ""
	@echo "First Time Setup:"
	@echo "  make bootstrap - Complete self-bootstrap (zero manual intervention)"
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
	@echo "  make graph-generate - Generate orchestration graph from Promptflow YAML"
	@echo "  make graph-verify   - Verify generated graph fingerprint"
	@echo ""
	@echo "For new users, just run: make bootstrap"

# === Web UI ===
.PHONY: webui.dev webui.build
webui.dev:
	cd apps/webui && npm install && npm run dev

webui.build:
	cd apps/webui && npm install && npm run typecheck && npm run build

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

# === Service Management (Fast Dev) ===
.PHONY: services.up services.down services.logs

services.up:
	@bash -lc 'source ci/_load_env.sh; \
	  (pgrep -f "services.worldcore.main" >/dev/null || uvicorn services.worldcore.main:app --port 8000 $${WORLDCORE_RELOAD:+--reload} >/tmp/worldcore.log 2>&1 &); \
	  (pgrep -f "services.narrative.main" >/dev/null || uvicorn services.narrative.main:app --port 8001 --reload >/tmp/narrative.log 2>&1 &); \
	  (pgrep -f "services.orchestration.host" >/dev/null || uvicorn services.orchestration.host:app --port 8700 --reload >/tmp/orch.log 2>&1 &); \
	  echo "services started (8000, 8001, 8700)";'

services.down:
	@pkill -f "services.worldcore.main" || true
	@pkill -f "services.narrative.main" || true
	@pkill -f "services.orchestration.host" || true
	@sleep 1; echo "services stopped"

services.logs:
	@echo "--- worldcore ---"; tail -n 100 /tmp/worldcore.log || true
	@echo "--- narrative ---"; tail -n 100 /tmp/narrative.log || true
	@echo "--- orch ---";     tail -n 100 /tmp/orch.log || true

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

# --- AgentPM rules & proofs hardening ---
.PHONY: rules-sync proofs-guard rules-guard verify-narrative verify-lms verify-all ci-perms guards verify

ci-perms:
	chmod +x ci/*.sh

rules-sync:
	chmod +x scripts/sync_rules.sh
	./scripts/sync_rules.sh

proofs-guard:
	@bash ci/proofs_path_guard.sh

rules-guard:
	@bash ci/rules_presence_guard.sh

guards: ssot.guards
	@echo "✅ guards: all rails green"

# === Proof-Grade Verification Guards ===
.PHONY: proof-guards proof-envelope proof-embedding proof-rerank proof-integrity proof-isolation proof-fresh-shell proof-soak

proof-guards: ci-perms
	@echo "🔍 Running proof-grade verification guards..."
	@bash -c 'source ci/_load_env.sh; ./ci/envelope_conformance_guard.sh && ./ci/embedding_dim_guard.sh && ./ci/rerank_monotonic_guard.sh && ./ci/proof_integrity_guard.sh && ./ci/provider_isolation_guard.sh && ./ci/fresh_shell_env_guard.sh && ./ci/soak_and_concurrency_guard.sh'
	@echo "✅ All proof-grade guards passed!"

proof-envelope:
	@bash -c 'source ci/_load_env.sh; ./ci/envelope_conformance_guard.sh'

proof-embedding:
	@bash -c 'source ci/_load_env.sh; ./ci/embedding_dim_guard.sh'

proof-rerank:
	@bash -c 'source ci/_load_env.sh; ./ci/rerank_monotonic_guard.sh'

proof-integrity:
	@bash -c 'source ci/_load_env.sh; ./ci/proof_integrity_guard.sh'

proof-isolation:
	@bash -c 'source ci/_load_env.sh; ./ci/provider_isolation_guard.sh'

proof-fresh-shell:
	@bash -c 'source ci/_load_env.sh; ./ci/fresh_shell_env_guard.sh'

proof-soak:
	@bash -c 'source ci/_load_env.sh; ./ci/soak_and_concurrency_guard.sh'

.PHONY: rules-emit
rules-emit:
	@python3 scripts/mdc_to_cursor_rules.py

verify: rules-emit guards
	@echo "All guards passed."

.PHONY: smoke-provider-split
smoke-provider-split: guards
	./scripts/smoke_provider_split.sh

.PHONY: proofs-lint
proofs-lint: guards
	./scripts/proofs_lint.sh

verify-narrative:
	@bash scripts/verify_narrative.sh

verify-lms:
	@bash scripts/verify_lms.sh

# Ensure both proofs exist and rules are emitted before live verify
verify-all: rules-emit rules-guard proofs-guard
	@echo "=== STORYMAKER VERIFICATION ==="
	@echo "1. Config check..."
	@bash -c 'source .env && $(MAKE) config-check'
	@echo "2. LM Studio check..."
	@bash -c 'source .env && $(MAKE) verify-lms'
	@echo "3. Preflight check..."
	@bash -c 'source .env && $(MAKE) verify-preflight'
	@echo "4. Live verification..."
	@bash -c 'source .env && $(MAKE) verify-live'
	@echo "5. Narrative proof..."
	@bash -c 'source .env && $(MAKE) verify-narrative'
	@echo "6. SSOT v1.2 self-test..."
	@bash -c 'source .env && ./ci/ssot_v1_2_self_test.sh'
	@echo "7. Proof-grade verification guards..."
	@bash -c 'source .env && $(MAKE) proof-guards'
	@echo "✅ ALL VERIFICATIONS PASSED"

# === Orchestration (Promptflow → LangGraph) ===
.PHONY: graph-generate graph-verify

PF_YAML=examples/flows/outline.flow.dag.yaml
LG_OUT=services/orchestration/generated/outline_graph.py

graph-generate:
	@python3 -m tools.pf_langgraph.gen --in $(PF_YAML) --out $(LG_OUT)

graph-verify:
	@python3 -m tools.pf_langgraph.verify --yaml examples/flows/outline.flow.dag.yaml --py services/orchestration/generated/outline_graph.py

.PHONY: graph-serve
graph-serve: graph-generate
	@echo "Serving generated graph at http://127.0.0.1:8700 (CTRL+C to stop)"
	@python3 - <<'PY'
	import uvicorn, os
	os.environ.setdefault("PYTHONPATH",".")
	uvicorn.run("services.orchestration.host:app", host="127.0.0.1", port=8700, reload=True)
	PY

.PHONY: graph-dev
# Launch LangGraph Studio (visual live graph); requires: pip install -U "langgraph-cli[inmem]"
graph-dev: graph-generate
	@echo "Opening LangGraph Studio at http://127.0.0.1:8123"
	@langgraph dev

.PHONY: graph-diagram
# Render Mermaid diagram from the Promptflow YAML
graph-diagram:
	@python3 tools/pf_langgraph/diagram.py examples/flows/outline.flow.dag.yaml docs/diagrams/outline.mmd.md
	@echo "Mermaid: docs/diagrams/outline.mmd.md"

.PHONY: mock-serve
mock-serve:
	@echo "Mock services at http://127.0.0.1:8900"
	@PYTHONPATH=. python3 scripts/mock_story_services.py

.PHONY: graph-e2e-ok
# End-to-end happy path against mock services (approved=True)
graph-e2e-ok: graph-generate
	@PYTHONPATH=. python3 scripts/test_graph_e2e.py

.PHONY: graph-e2e-fail
# End-to-end failure path (force gate to false via env), should not hit approve node
graph-e2e-fail: graph-generate
	@PYTHONPATH=. python3 scripts/test_graph_e2e.py fail

.PHONY: graph-test-parallel
# Test parallel execution and race conditions
graph-test-parallel: graph-generate
	@PYTHONPATH=. python3 tests/test_graph_parallel.py

# === Envelope System ===
.PHONY: envelope-guard-ok envelope-guard-bad

envelope-guard-ok:
	@echo '{"status":"success","data":{},"error":{"message":""},"meta":{"smoke_score":0.0}}' \
	| bash tools/single_envelope_guard.sh | jq -e '.status=="success"' >/dev/null && \
	echo "OK: guard passed object" || (echo "FAIL: guard"; exit 1)

envelope-guard-bad:
	@echo 'not json' | bash tools/single_envelope_guard.sh | jq -e '.status=="error"' >/dev/null && \
	echo "OK: guard rejected invalid input" || (echo "FAIL: guard bad"; exit 1)

.PHONY: webui-test
webui-test:
	@cd apps/webui && npx playwright install --with-deps && npx playwright test

# --- SSOT / Models (render + guard) ---
.PHONY: ssot.env.render ssot.env.check
ssot.env.render:
	@bash tools/env_from_models.sh

ssot.env.check:
	@bash ci/guards/models_guard.sh

# --- SSOT docs sync (pointer stubs) ---
.PHONY: ssot.sync.docs
ssot.sync.docs:
	@bash tools/ssot_docs_sync.sh

# --- Script duplication guard ---
.PHONY: scripts.unique
scripts.unique:
	@bash ci/guards/scripts_uniqueness_guard.sh

# --- Python venv discipline ---
.PHONY: venv.ensure venv.shell py.run
venv.ensure:
	@bash tools/venv_lock.sh

venv.shell: venv.ensure
	@bash -lc 'source .venv/bin/activate && echo "🐍 In .venv:" $${VIRTUAL_ENV} && $$SHELL'

py.run: venv.ensure
	@.venv/bin/python -c "import sys; print('Python:', sys.version.split()[0]); print('Exec:', sys.executable)"

.PHONY: venv.check
venv.check:
	@bash ci/guards/venv_guard.sh

# --- Cursor rules (emit + check) ---
.PHONY: rules.emit rules.check rules.clean
rules.emit:
	@bash tools/rules_emit.sh

rules.check:
	@bash ci/guards/rules_presence_guard.sh

rules.clean:
	@rm -rf .cursor/rules && mkdir -p .cursor/rules && echo "cleaned .cursor/rules"

# Optional aggregator if you use it in CI:
.PHONY: ssot.guards
ssot.guards: venv.check ssot.env.check scripts.unique rules.check
	@bash ci/guards/rules_no_md_guard.sh
	@echo "✅ ssot.guards ok"

# === Cross-Workspace Management ===
WORK_MAIN := $(PWD)
WORK_AGENTPM := $(WORK_MAIN)/.agentpm_workspace

.PHONY: workspaces.verify workspaces.guards workspaces.services.up workspaces.services.down guards.proof guards.health guards.health.matrix guards.canon guards.health.watch

workspaces.verify: ## Run guards in both workspaces (fresh shell)
	@bash -lc 'set -euo pipefail; \
	  cd "$(WORK_MAIN)";        make guards; \
	  cd "$(WORK_AGENTPM)";     make guards; \
	  echo "✅ both workspaces verified"'

workspaces.guards: workspaces.verify

guards.proof:
	@bash -lc 'set -euo pipefail; ./ci/proof_integrity_guard.sh'

guards.health:
	@bash -lc 'set -euo pipefail; REQ_OK=$${REQ_OK:-3} ORCH_HEALTH_OVERRIDE=$${ORCH_HEALTH_OVERRIDE:-} ./ci/preflight_cross.sh'

guards.health.matrix:
	@bash -lc 'set -euo pipefail; REQ_OK=$${REQ_OK:-3} ORCH_HEALTH_OVERRIDE=$${ORCH_HEALTH_OVERRIDE:-} ./ci/health_matrix.sh'

guards.canon:
	@bash -lc 'set -euo pipefail; chmod +x ci/test_canonicalizer.sh || true; ./ci/test_canonicalizer.sh'

guards.canon.lint:
	@bash -lc 'set -euo pipefail; echo "[lint] canonicalizer must be ci/json_hash.py only"; if rg -n "jq -S|-c .*del\\(.proof\\)" ci --glob "!*proof_integrity_guard.sh" --glob "!*drift_detection.sh" | tee /dev/stderr | grep .; then echo "::error ::found jq-based canonicalization in ci/ (use ci/json_hash.py)"; exit 1; fi; if ! rg -n "ci/json_hash\\.py" ci | grep .; then echo "::error ::no references to ci/json_hash.py in ci/"; exit 1; fi; echo "[lint] ok"'

guards.health.watch:
	@bash -lc 'while true; do clear; date; make -s guards.health.matrix || true; sleep 2; done'

guards.sweep:
	@bash -lc 'set -euo pipefail; ./ci/full_sweep.sh'

.PHONY: verify.canon
verify.canon:
	@bash -lc 'set -euo pipefail; \
	  make guards.canon.lint; \
	  make guards.canon; \
	  make guards.proof'
