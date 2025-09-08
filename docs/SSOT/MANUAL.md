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

# Check system status
make status

# Run verification
make verify-all

# Run guards
make verify
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

### Environment Variables
- **Groq**: `GROQ_API_KEY`, `GROQ_MODEL=llama-3.3-70b-versatile`
- **LM Studio**: `OPENAI_API_BASE=http://127.0.0.1:1234/v1`
- **Database**: `DATABASE_URL`, `POSTGRES_DSN`
- **Mock Controls**: `DISABLE_MOCKS=1`, `MOCK_LMS=0`

### Proofs Location
All verification evidence must be in `docs/proofs/agentpm/` - this is enforced by CI guards.

### SSOT Rules
Rules are authored in `docs/SSOT/rules/*.mdc` and synced to `.cursor/rules/` by `make rules-sync`.
