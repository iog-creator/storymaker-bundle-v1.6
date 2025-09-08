# AgentPM Troubleshooting Guide

## ✅ SYSTEM STATUS: FULLY FUNCTIONAL

**Current Status**: All AgentPM integration issues have been resolved. The system is fully operational for both development and production use.

## Quick Health Check

```bash
# Self-bootstrap (if not already done)
make bootstrap
# Expected: 🎉 Bootstrap Complete! System is production-ready

# Verify everything is working
make verify-all
# Expected: ✅ ALL VERIFICATIONS PASSED

# Check system status
scripts/bootstrap.sh status
# Expected: ✅ LM Studio running with X models
```

## Common Issues & Solutions

### 1. Bootstrap Issues

**Symptoms**: `make bootstrap` fails or system not properly initialized
**Solution**:
```bash
# Run bootstrap again (idempotent)
make bootstrap

# If still failing, check prerequisites
docker ps  # Docker should be running
curl -s http://127.0.0.1:1234/v1/models  # LM Studio should be accessible

# Manual environment setup if needed
cp .env.example .env
# Edit .env with your settings
```

### 2. Environment Wrapper Issues

**Symptoms**: `scripts/run.sh` fails or hangs
**Solution**:
```bash
# Test environment wrapper
scripts/run.sh bash -lc 'echo "AgentPM working"'
# Expected: AgentPM working

# Check .env file exists
ls -la .env
# Should show the file exists

# Check file permissions
chmod +x scripts/run.sh
```

### 3. Verification Failures

**Symptoms**: `make verify-all` fails on specific checks
**Solution**:
```bash
# Run individual checks to isolate issue
make config-check
make verify-lms
make verify-preflight
make verify-live

# Check specific script
scripts/run.sh bash scripts/preflight_gate.sh | jq
```

### 4. LM Studio Connection Issues (Production Mode)

**Symptoms**: LM Studio integration fails
**Solution**:
```bash
# Check if LM Studio is running
curl -s http://127.0.0.1:1234/v1/models

# If not running, either:
# Option 1: Start LM Studio and load a model
# Option 2: Switch to mock mode
echo "MOCK_LMS=1" >> .env
```

### 5. Database Connection Issues

**Symptoms**: Services fail to start or connect to database
**Solution**:
```bash
# Check Docker containers
docker compose ps

# Start database if needed
docker compose up -d db redis minio

# Check database connection
scripts/run.sh bash -lc 'env | grep DATABASE_URL'
```

### 6. Service Port Conflicts

**Symptoms**: Services fail to start on ports 8000-8004
**Solution**:
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :8001
lsof -i :8002
lsof -i :8003
lsof -i :8004

# Kill processes if needed
scripts/kill_by_port.sh 8000
scripts/kill_by_port.sh 8001
# etc.

# Or restart all services
make api.restart
```

### 7. JSON/Envelope Format Issues

**Symptoms**: Envelope validation fails
**Solution**:
```bash
# Test envelope system
make envelope-guard-ok
make envelope-guard-bad

# Check specific envelope
echo '{"status":"success","data":{},"error":{"message":""},"meta":{"smoke_score":0.0}}' | tools/single_envelope_guard.sh
```

### 8. Script Permission Issues

**Symptoms**: Permission denied errors
**Solution**:
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x tools/*.sh

# Check permissions
ls -la scripts/
ls -la tools/
```

## Debug Commands

### System Status
```bash
# Overall status
scripts/bootstrap.sh status

# Individual service checks
curl -s http://localhost:8000/health
curl -s http://localhost:8001/health
curl -s http://localhost:8002/health
curl -s http://localhost:8003/health
curl -s http://localhost:8004/health
```

### Environment Debugging
```bash
# Check environment variables
scripts/run.sh bash -lc 'env | grep -E "(OPENAI|DATABASE|SSOT|MOCK_LMS)"'

# Test environment loading
scripts/run.sh bash -lc 'echo "Environment loaded successfully"'
```

### Log Analysis
```bash
# Docker logs
docker compose logs

# Service logs (if running)
tail -f logs/worldcore.log
tail -f logs/narrative.log
# etc.
```

### AgentPM Specific
```bash
# Test individual components
scripts/run.sh bash scripts/lmstudio_models_envelope.sh
scripts/run.sh bash scripts/lmstudio_chat_smoke.sh
scripts/run.sh bash scripts/ssot_presence.sh
scripts/run.sh bash scripts/commit_hygiene_check.sh

# Test with sample input
echo "PR-1234: Test commit" | scripts/commit_hygiene_check.sh --stdin
```

## Recovery Procedures

### Complete Reset
```bash
# Stop all services
make stop
docker compose down

# Clean up ports
for port in 8000 8001 8002 8003 8004; do
    scripts/kill_by_port.sh $port || true
done

# Restart everything
make start
```

### Mock Mode Reset
```bash
# Ensure mock mode is enabled
echo "MOCK_LMS=1" > .env.tmp
grep -v MOCK_LMS .env >> .env.tmp
mv .env.tmp .env

# Test
make verify-all
```

### Database Reset
```bash
# Stop database
docker compose down

# Remove volumes (WARNING: This will delete all data)
docker compose down -v

# Restart database
docker compose up -d db redis minio

# Run migrations
make db.migrate
```

## Prevention Tips

1. **Always run bootstrap first** - `make bootstrap` handles everything automatically
2. **Run verification before making changes** - `make verify-all`
3. **Check status regularly** - `scripts/bootstrap.sh status`
4. **Use environment wrapper** - `scripts/run.sh bash -lc 'command'`
5. **Keep documentation updated** - Update docs when making changes

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs** - Look for error messages in output
2. **Run individual tests** - Isolate the failing component
3. **Verify environment** - Ensure all variables are set correctly
4. **Check file permissions** - Make sure scripts are executable
5. **Review recent changes** - What was modified recently?

## Success Indicators

You know AgentPM is working correctly when:

- ✅ `make verify-all` returns "ALL VERIFICATIONS PASSED"
- ✅ `scripts/bootstrap.sh status` shows proper mode (mock or LM Studio)
- ✅ `scripts/run.sh bash -lc 'echo "test"'` works without errors
- ✅ All envelope tests pass (`make envelope-guard-ok`)
- ✅ Services respond to health checks on ports 8000-8004

**Remember**: The system is designed to work in mock mode by default, so you don't need LM Studio for basic development and testing.

