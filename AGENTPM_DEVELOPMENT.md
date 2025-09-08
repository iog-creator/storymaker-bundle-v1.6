# AgentPM Development & Testing

## Overview

This repository serves as a **real-world testbed** for the AgentPM prototype system. StoryMaker is the application being used to validate AgentPM's capabilities in a production-like environment.

## What We're Building

**AgentPM** is a local-first AI project management system that provides:
- Quality gates and verification pipelines
- Envelope-based response validation
- Proof capture and audit trails
- SSOT (Single Source of Truth) documentation
- Local LM Studio integration (no cloud dependencies)

## Current Status

### ✅ Working Components
- **LM Studio Integration**: Real local AI models (22 models loaded)
- **Envelope System**: JSON envelope validation working
- **Proof Capture**: Envelopes being captured in `docs/proofs/agentpm/`
- **Quality Gates**: Preflight checks, SSOT presence, commit hygiene
- **Virtual Environment**: Python 3.13.3 venv properly configured
- **Service Integration**: All 5 StoryMaker services verified

### 🔧 Recent Fixes
- **JSON Formatting**: Fixed malformed JSON in `lmstudio_models_envelope.sh`
- **Bootstrap System**: Created user-friendly setup scripts
- **Health Checks**: Added comprehensive status monitoring
- **Error Handling**: Improved error messages and troubleshooting

## Testing AgentPM with StoryMaker

### Verification Pipeline
```bash
# Full AgentPM verification suite
make verify-all

# Individual components
make verify-lms        # LM Studio integration
make verify-preflight  # Quality gates
make verify-live       # Service health
```

### Envelope System Testing
```bash
# Test envelope validation
make envelope-guard-ok   # Should pass
make envelope-guard-bad  # Should fail gracefully
```

### Proof Capture
- **Location**: `docs/proofs/agentpm/`
- **Format**: JSON envelopes with status, data, error, meta
- **Examples**: 
  - `lms_chat_20250907_215507/` - LM Studio chat test
  - `preflight_20250907_215508/` - Preflight gate test

## AgentPM Architecture

### Core Components
1. **Environment Wrapper** (`scripts/run.sh`) - Loads .env and normalizes config
2. **LM Studio Client** (`scripts/lm_api.py`) - OpenAI-compatible API client
3. **Quality Gates** (`scripts/preflight_gate.sh`) - Multi-step verification
4. **Envelope System** (`tools/single_envelope_guard.sh`) - Response validation
5. **Proof Capture** - Automatic envelope storage with timestamps

### Integration Points
- **StoryMaker Services**: worldcore, narrative, screenplay, media, interact
- **Database**: PostgreSQL with proper migrations
- **AI Models**: Local LM Studio with embedding, chat, and reranking
- **Documentation**: SSOT structure with templates and rules

## Development Workflow

### 1. Make Changes
- Modify AgentPM scripts or configuration
- Update StoryMaker services if needed

### 2. Test Integration
```bash
# Quick health check
make status

# Full verification
make verify-all

# Test specific components
make verify-lms
make verify-preflight
```

### 3. Validate Proofs
- Check `docs/proofs/agentpm/` for new envelopes
- Verify envelope format and content
- Test envelope guard system

### 4. Debug Issues
```bash
# Check LM Studio
curl http://127.0.0.1:1234/v1/models

# Check services
make status

# View logs
docker compose logs
```

## Key Learnings

### What Works Well
- **Local-First**: No cloud dependencies, full privacy
- **Envelope System**: Consistent JSON format for all responses
- **Quality Gates**: Multi-step verification catches issues early
- **Proof Capture**: Automatic audit trail for all operations

### Areas for Improvement
- **Error Messages**: Need clearer guidance for common issues
- **Bootstrap**: Simplified setup process (✅ Fixed)
- **Documentation**: Better user guides (✅ Fixed)
- **Testing**: More comprehensive test coverage

## Next Steps

### Immediate
- [ ] Test AgentPM workflows with StoryMaker features
- [ ] Validate proof capture for different operation types
- [ ] Test envelope system with various response formats

### Short Term
- [ ] Add more quality gates
- [ ] Improve error handling and recovery
- [ ] Add performance monitoring

### Long Term
- [ ] Package AgentPM as standalone system
- [ ] Create integration templates for other projects
- [ ] Develop AgentPM CLI tools

## Debugging Guide

### Common Issues
1. **LM Studio Not Running**: Check port 1234, verify models loaded
2. **Database Connection**: Check Docker, verify POSTGRES_DSN
3. **Service Failures**: Check ports 8000-8004, view logs
4. **Envelope Errors**: Check JSON format, validate schema

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

## Success Metrics

- ✅ **Zero Cloud Dependencies**: All AI operations local
- ✅ **Consistent Envelopes**: All responses follow v1.1 format
- ✅ **Quality Gates**: Preflight checks catch issues
- ✅ **Proof Capture**: All operations audited
- ✅ **Service Health**: All StoryMaker services verified
- ✅ **User Experience**: Simple setup and clear error messages

This is a **working prototype** of AgentPM being validated in a real-world scenario with StoryMaker as the test application.
