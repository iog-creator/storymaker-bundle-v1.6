# MANUAL.md - StoryMaker + AgentPM Operations Manual

## Quick Start

### Self-Bootstrap (Zero Manual Intervention)
```bash
git clone <repo>
cd storymaker-bundle-v1.6-unified-full
make bootstrap
```

### Post-Bootstrap Operations
```bash
# Start all services
make start

# Start WebUI (if not auto-started)
./start_webui_with_timeout.sh

# Start orchestration service
make graph-serve

# Check system status
./check_system_status.sh

# Run verification
make verify-all

# Run guards
make verify
```

## WebUI Operations

### Starting WebUI
```bash
# Start WebUI with proper environment
./start_webui_with_timeout.sh

# Check WebUI status
curl -I http://localhost:5173/

# View WebUI logs
tail -f /tmp/webui.log
```

### WebUI Features
- **Story Flow Runner**: Enter premise, generate complete story outline
- **Real-time Generation**: Live progress updates during story creation
- **QA Analysis**: Automatic trope budget and promise/payoff analysis
- **Drag & Drop**: Reorder story beats with visual interface
- **Scene Cards**: Convert beats to detailed scene cards (WHO/WHERE/WHEN/GOAL)

### Orchestration Service
```bash
# Start orchestration service
make graph-serve

# Test orchestration endpoint
curl -X POST http://localhost:8700/run \
  -H "Content-Type: application/json" \
  -d '{"premise": "A heist story about a team of misfits"}'
```

## Service Management

### Starting Services
```bash
make start          # Start all services
make api.up         # Start API services only
docker compose up -d # Start infrastructure only
```

### Stopping Services
```bash
make stop           # Stop all services
make api.down       # Stop API services only
docker compose down # Stop infrastructure only
```

### Service Status
```bash
make status         # Overall system status
scripts/bootstrap.sh status  # Detailed status
docker compose ps   # Container status
```

## Verification & Testing

### Full Verification Suite
```bash
make verify-all     # Complete verification
make verify         # Run all guards
```

### Individual Components
```bash
make verify-lms     # LM Studio integration
make verify-narrative # Groq creative generation
make verify-preflight # Quality gates
make verify-live    # End-to-end testing
```

### Guard System
```bash
make guards         # Run all CI guards
make ci-perms       # Set guard permissions
make rules-sync     # Sync SSOT rules to Cursor
```

## Troubleshooting

### Common Issues
1. **Bootstrap fails**: Check Docker is running, run `make bootstrap` again
2. **LM Studio not found**: Install LM Studio, load models, start server
3. **Services won't start**: Check ports 8000-8004, run `make restart`
4. **Verification fails**: Run individual tests to isolate issue

### Recovery Procedures
```bash
# Complete reset
make stop
docker compose down
make bootstrap

# Service restart
make restart

# Database reset (WARNING: deletes data)
docker compose down -v
docker compose up -d db redis minio
```

## Configuration

## Quick Start (v1.2)

1. Copy `.env.example` → `.env` and set required vars (Groq + LM Studio).
2. Start dev runner:
   ```bash
   scripts/dev_up.sh
   ```

3. Verify:

   ```bash
   make verify-all
   ```

   * Includes: env, no-mocks, provider-split, proofs-path, SSOT/rules presence, model-lock, retrieval-smoke, self-test.

## Verification

Run:

```bash
make verify-all
```

This runs all guards:

* env\_config\_guard
* no\_mocks\_guard
* provider\_split\_guard
* proofs\_path\_guard
* ssot\_guard
* rules\_presence\_guard
* model\_lock\_guard
* retrieval\_smoke\_guard
* proof\_integrity\_guard
* rerank\_monotonic\_guard
* soak\_and\_concurrency\_guard
* provider\_isolation\_guard
* fresh\_shell\_env\_guard

All must pass for compliance.

## Troubleshooting

- **Model lock failure** → ensure LM Studio exposes all Qwen IDs.
- **Retrieval smoke failure** → embeddings must be `dims=1024`; check `EMBEDDING_MODEL`.
- **Proof integrity failure** → proof file must exactly match API response (`proof.sha256`).
- **Rerank monotonic failure** → scores must be strictly descending; check reranker model.
- **Soak failure** → service instability; restart and inspect logs.
- **Provider isolation failure** → Narrative may only use Groq; QA/Retrieval may only use LM Studio.
- **QA empty analysis failure** → QA endpoints must return non-empty data; check LM Studio models.
- **QA latency zero failure** → `latency_ms` must be > 0; indicates stub/mock response.
- **Legacy route failure** → all public endpoints must be under `/api/v1/*`; check for unversioned routes.

### Environment Variables
- **Groq**: `GROQ_API_KEY`, `GROQ_MODEL=llama-3.3-70b-versatile`
- **LM Studio**: `OPENAI_API_BASE=http://127.0.0.1:1234/v1`
- **Database**: `DATABASE_URL`, `POSTGRES_DSN`
- **Mock Controls**: `DISABLE_MOCKS=1`, `MOCK_LMS=0`

### Proofs Location
All verification evidence must be in `docs/proofs/agentpm/` - this is enforced by CI guards.

### SSOT Rules
Rules are authored in `docs/SSOT/rules/*.mdc` and synced to `.cursor/rules/` by `make rules-sync`.

## Automation Usage
For CI/scripts: Always use `pmagent preflight --json`.
- Assert exit code == 0.
- Parse stdout as JSON (Content-Type: application/json implied; pipe to jq '.status == "ok"').
- On fail: exit 1 + stderr diagnostics; stdout is still valid envelope (for error inspection).
- Example: `pmagent preflight --json | jq -e '.status == "ok"' || exit 1`
