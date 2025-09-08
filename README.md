# AgentPM Prototype

**Local-First AI Project Management System**

AgentPM is a **fully functional** local-first AI project management system that provides quality gates, verification pipelines, and proof capture capabilities. This repository serves as the development and testing environment for the AgentPM prototype.

> **SSOT:** The canonical plan for StoryMaker + AgentPM lives at  
> `docs/SSOT/MASTER_PLAN.md` (v1.6 FINAL). Rebuilds must follow that document exactly.
>
> **AgentPM Rails:** Rules are authored in `docs/SSOT/rules/*.mdc` and are
> synced into `.cursor/rules/` by `make rules-sync`. Proofs are **only**
> written to `docs/proofs/agentpm/` (workspace proofs folder is a symlink).

**✅ INTEGRATION COMPLETE**: All AgentPM integration issues have been resolved. The system is now fully operational for both development and production use with comprehensive mock mode support.

**Note**: This repository uses StoryMaker as a testbed application for validating AgentPM capabilities, but StoryMaker itself is a separate, classified project.

### Architecture Guardrails (No Mocks)

* `DISABLE_MOCKS=1`, `MOCK_LMS=0` are enforced in env, runtime, and CI.
* Creative = **Groq** only; Embeddings/Rerank/Planning = **LM Studio** only.
* Verification MUST produce envelopes under `docs/proofs/agentpm/`.
* Guards hard-fail if any mock/fallback path is detected.

## 🚀 Quick Start (Zero Manual Intervention)

### **One-Command Bootstrap**
```bash
git clone https://github.com/iog-creator/storymaker-bundle-v1.6.git
cd storymaker-bundle-v1.6-unified-full
make bootstrap
```

**That's it!** The system handles everything automatically:
- ✅ Environment setup and validation
- ✅ Infrastructure startup (Docker services)
- ✅ LM Studio integration detection
- ✅ AgentPM workspace initialization
- ✅ Rules sync and enforcement
- ✅ Complete system verification

### **What the Bootstrap Does**

1. **Environment Auto-Setup**
   - Copies `.env.example` → `.env`
   - Validates required environment variables
   - Sets up AgentPM workspace structure

2. **Infrastructure Auto-Start**
   - Starts Docker services (Postgres, Redis, MinIO)
   - Waits for services to be ready
   - Validates database connectivity

3. **LM Studio Integration**
   - Detects LM Studio installation
   - Validates model availability
   - Confirms API endpoint accessibility

4. **AgentPM Workspace Bootstrap**
   - Creates canonical proofs directory
   - Sets up workspace symlinks
   - Syncs SSOT rules to Cursor
   - Enforces all guardrails

5. **System Verification**
   - Runs complete verification suite
   - Generates both LM Studio and Groq proofs
   - Validates all quality gates

### **Post-Bootstrap Usage**
```bash
# Start all services
make start

# Check status
make status

# Run verification
make verify-all
```

### Canonical proofs location (MANDATORY)
All verifier evidence and narrative proofs MUST live under:

```
docs/proofs/agentpm/
```

Anything outside this path fails the proofs guard.

### **Optional: LM Studio Setup**
For full AI capabilities, install LM Studio:
1. Download from [lmstudio.ai](https://lmstudio.ai)
2. Load Qwen chat + embedding models
3. Start server on port 1234

The system works without LM Studio but with limited AI features.

### Step 3: Use AgentPM
- **Testbed Application**: http://localhost:3000
- **API Endpoints**: http://localhost:8000-8004
- **Verification**: `make verify-all`

## 📖 What AgentPM Does

### Core Features
- **Local-First AI**: No cloud dependencies, full privacy
- **Quality Gates**: Multi-step verification and validation
- **Envelope System**: Consistent JSON response format
- **Proof Capture**: Automatic audit trail for all operations
- **LM Studio Integration**: Local AI models for all operations
- **Local-First AI**: All operations use local LM Studio models ✅
- **All Tests Pass**: Complete verification suite working ✅

### Testbed Application Services
- **Worldcore** (port 8000): World building, lore, and universe management
- **Narrative** (port 8001): Story generation, plot development, and pacing
- **Screenplay** (port 8002): Script formatting, dialogue, and scene structure
- **Media** (port 8003): Image generation and multimedia content
- **Interact** (port 8004): User interactions and chat interface

*Note: The testbed application is used to validate AgentPM capabilities but is a separate, classified project.*

## 🛠️ Common Commands

```bash
# AgentPM Verification
make verify-all     # Run all AgentPM verification checks
make config-check   # Check environment configuration
make verify-lms     # Test LM Studio integration
make verify-preflight # Run preflight quality gates

# System Management
make start          # Start everything
make status         # Check if services are running
make stop           # Stop all services
make restart        # Restart services
make help           # Show all commands

# AgentPM Status
scripts/bootstrap.sh status  # Check AgentPM status
scripts/run.sh bash -lc 'command'  # Run commands with AgentPM environment
```

## 🔧 Troubleshooting

### Quick Fixes
```bash
# Verify everything is working
make verify-all
# Expected: ✅ ALL VERIFICATIONS PASSED

# Check AgentPM status
scripts/bootstrap.sh status
# Expected: ✅ LM Studio running with X models
```

### "LM Studio not found" (Production Mode)
- Make sure LM Studio is running
- Check that the server is on port 1234
- Try: `curl http://127.0.0.1:1234/v1/models`

### "Database connection failed"
- Run: `make restart`
- Check Docker is running: `docker ps`

### "Services won't start"
- Check port conflicts: `make status`
- View logs: `docker compose logs`
- Restart: `make restart`

### AgentPM Issues
- **Environment wrapper fails**: Test `scripts/run.sh bash -lc 'echo "test"'`
- **Verification failures**: Run individual checks (`make config-check`, `make verify-lms`, etc.)

**For detailed troubleshooting**: See [AGENTPM_TROUBLESHOOTING.md](AGENTPM_TROUBLESHOOTING.md)

## 📚 Documentation

### For Users
- **[Quick Start Guide](QUICK_START.md)** - 5-minute setup guide
- **[User Guide](USER_GUIDE.md)** - Non-technical guide for writers and authors

### For Developers
- **[AgentPM Integration](AGENTPM_INTEGRATION.md)** - Complete integration status and usage
- **[AgentPM Development](AGENTPM_DEVELOPMENT.md)** - Prototype development status and testing
- **[AgentPM Troubleshooting](AGENTPM_TROUBLESHOOTING.md)** - Comprehensive troubleshooting guide
- **[AgentPM Pain Points](AGENTPM_PAIN_POINTS.md)** - Issues resolved and lessons learned
- **[Cursor Handoff](cursor_handoff_build_run_v_1.md)** - Complete development handoff
- **[API Documentation](docs/openapi/storymaker.core.yaml)** - Technical API docs
- **[Contributing Guide](CONTRIBUTING.md)** - For developers

## 🎯 For Developers

### Development Setup
```bash
make setup      # Install development tools
make test       # Run tests
make verify-all # Full verification suite
```

### Architecture
AgentPM uses a microservices architecture with:
- **FastAPI** services for each domain
- **PostgreSQL** for data persistence
- **Redis** for caching
- **LM Studio** for AI capabilities
- **Envelope System** for response validation
- **Quality Gates** for verification pipelines

## 📄 License

This project is licensed under a **Non-Commercial Personal Use License** - see the [LICENSE](LICENSE) file for details.

**Copyright (c) 2024 Bryon McCoy (mccoyb00@gmail.com)**

### License Summary:
- ✅ **Personal, non-commercial use** is permitted
- ❌ **Commercial use** is prohibited without explicit written agreement
- 📧 **Contact**: mccoyb00@gmail.com, 📞 203-989-0875, or 💼 [LinkedIn](https://www.linkedin.com/in/bryon-m-00979462) for commercial use permissions
- 📄 **Distribution**: This license must be included with all distributions

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### AgentPM Development
This repository serves as the development environment for the AgentPM prototype system. If you're interested in contributing to AgentPM development:
- Check [AGENTPM_DEVELOPMENT.md](AGENTPM_DEVELOPMENT.md) for current status
- Review [cursor_handoff_build_run_v_1.md](cursor_handoff_build_run_v_1.md) for development guidelines
- Run `make verify-all` to test the AgentPM system

## 🌟 AgentPM Features

- **Local-First AI**: No cloud dependencies, full privacy
- **Quality Gates**: Multi-step verification and validation
- **Envelope System**: Consistent JSON response format
- **Proof Capture**: Automatic audit trail for all operations
- **LM Studio Integration**: Local AI models for all operations
- **Bootstrap System**: One-command setup and health checks
- **User Documentation**: Clear guides for different user levels

---

**Need help?** Run `make help` or check the [Quick Start Guide](QUICK_START.md).### Canonical proofs location (MANDATORY)
All verifier evidence and narrative proofs MUST live under:

```
docs/proofs/agentpm/
```

Anything outside this path fails the proofs guard.
