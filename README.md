# StoryMaker v1.6 + AgentPM Prototype

**AI-Powered Creative Writing Platform with Local-First AI Project Management**

StoryMaker helps authors, screenwriters, and content creators build rich narratives with AI assistance. It provides world-building tools, character development, plot generation, and screenplay formatting.

**This repository also serves as a real-world testbed for the AgentPM prototype system** - a local-first AI project management platform that provides quality gates, verification pipelines, and proof capture capabilities.

## 🚀 Quick Start (2 Minutes)

### Prerequisites
- **LM Studio** (download from [lmstudio.ai](https://lmstudio.ai))
- **Docker** (for database)
- **Git** (to clone this repo)

### Step 1: Start LM Studio
1. Open LM Studio
2. Load any chat model (e.g., `qwen/qwen3-4b-2507`)
3. Click "Start Server" (should show port 1234)

### Step 2: Start StoryMaker
```bash
git clone https://github.com/iog-creator/storymaker-bundle-v1.6.git
cd storymaker-bundle-v1.6-unified-full
make start
```

That's it! StoryMaker will automatically:
- ✅ Check LM Studio connection
- ✅ Start the database
- ✅ Start all services
- ✅ Verify everything works

### Step 3: Use StoryMaker
- **Web Interface**: http://localhost:3000
- **API Endpoints**: http://localhost:8000-8004

## 📖 What StoryMaker Does

### Core Services
- **Worldcore** (port 8000): World building, lore, and universe management
- **Narrative** (port 8001): Story generation, plot development, and pacing
- **Screenplay** (port 8002): Script formatting, dialogue, and scene structure
- **Media** (port 8003): Image generation and multimedia content
- **Interact** (port 8004): User interactions and chat interface

### Key Features
- **AI-Powered Writing**: Generate stories, characters, and dialogue
- **World Building**: Create rich, consistent fictional universes
- **Screenplay Formatting**: Industry-standard script formatting
- **Character Development**: Deep character creation and management
- **Plot Generation**: Intelligent story structure and pacing

## 🛠️ Common Commands

```bash
make start      # Start everything
make status     # Check if services are running
make stop       # Stop all services
make restart    # Restart services
make help       # Show all commands
```

## 🔧 Troubleshooting

### "LM Studio not found"
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

## 📚 Documentation

### For Users
- **[Quick Start Guide](QUICK_START.md)** - 5-minute setup guide
- **[User Guide](USER_GUIDE.md)** - Non-technical guide for writers and authors

### For Developers
- **[AgentPM Development](AGENTPM_DEVELOPMENT.md)** - Prototype development status and testing
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
StoryMaker uses a microservices architecture with:
- **FastAPI** services for each domain
- **PostgreSQL** for data persistence
- **Redis** for caching
- **LM Studio** for AI capabilities
- **AgentPM** for quality assurance

## 📄 License

This project is licensed under a **Non-Commercial Personal Use License** - see the [LICENSE](LICENSE) file for details.

**Copyright (c) 2024 Bryon McCoy (mccoyb00@gmail.com)**

### License Summary:
- ✅ **Personal, non-commercial use** is permitted
- ❌ **Commercial use** is prohibited without explicit written agreement
- 📧 **Contact**: mccoyb00@gmail.com for commercial use permissions
- 📄 **Distribution**: This license must be included with all distributions

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### AgentPM Prototype Development
This repository serves as a testbed for the AgentPM prototype system. If you're interested in contributing to AgentPM development:
- Check [AGENTPM_DEVELOPMENT.md](AGENTPM_DEVELOPMENT.md) for current status
- Review [cursor_handoff_build_run_v_1.md](cursor_handoff_build_run_v_1.md) for development guidelines
- Run `make verify-all` to test the AgentPM system

## 🌟 Features

### StoryMaker
- **AI-Powered Writing**: Generate stories, characters, and dialogue
- **World Building**: Create rich, consistent fictional universes
- **Screenplay Formatting**: Industry-standard script formatting
- **Character Development**: Deep character creation and management
- **Plot Generation**: Intelligent story structure and pacing

### AgentPM Prototype
- **Local-First AI**: No cloud dependencies, full privacy
- **Quality Gates**: Multi-step verification and validation
- **Envelope System**: Consistent JSON response format
- **Proof Capture**: Automatic audit trail for all operations
- **LM Studio Integration**: Local AI models for all operations

---

**Need help?** Run `make help` or check the [Quick Start Guide](QUICK_START.md).