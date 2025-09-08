# StoryMaker v1.6

**AI-Powered Creative Writing Platform**

StoryMaker helps authors, screenwriters, and content creators build rich narratives with AI assistance. It provides world-building tools, character development, plot generation, and screenplay formatting.

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
git clone <this-repo>
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

- **[Quick Start Guide](QUICK_START.md)** - For new users
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

See [LICENSE](LICENSE) for details.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Need help?** Run `make help` or check the [Quick Start Guide](QUICK_START.md).