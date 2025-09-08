# StoryMaker Quick Start Guide

## For New Users (Zero Manual Intervention)

### **One-Command Setup**
```bash
git clone https://github.com/iog-creator/storymaker-bundle-v1.6.git
cd storymaker-bundle-v1.6-unified-full
make bootstrap
```

**That's it!** The system automatically:
- ✅ Sets up environment and configuration
- ✅ Starts all infrastructure (Docker services)
- ✅ Detects and integrates with LM Studio
- ✅ Initializes AgentPM workspace
- ✅ Syncs rules and enforces guardrails
- ✅ Verifies everything is working

### **Start Using StoryMaker**
```bash
# Start all services
make start

# Check status
make status
```

### **Access StoryMaker**
- **Web UI**: http://localhost:3000
- **API**: http://localhost:8000-8004
- **Verification**: `make verify-all`

## Troubleshooting

### "Bootstrap failed"
- Check Docker is running: `docker ps`
- Verify internet connection for model downloads
- Run `make bootstrap` again (idempotent)

### "LM Studio not found"
- Download from [lmstudio.ai](https://lmstudio.ai)
- Load Qwen chat + embedding models
- Start server on port 1234
- System works without LM Studio but with limited AI features

### "Database connection failed"
- Run: `docker compose up -d db redis minio`
- Check services: `docker compose ps`

### "Services won't start"
- Run: `make restart`
- Check logs: `docker compose logs`

## What Each Service Does

- **worldcore** (port 8000): World building and lore
- **narrative** (port 8001): Story generation and plot
- **screenplay** (port 8002): Script formatting and dialogue
- **media** (port 8003): Images and multimedia
- **interact** (port 8004): User interactions and chat

## Need Help?

Run `make help` to see all available commands.

## Advanced Users

If you want to customize models or settings, see `ADVANCED_SETUP.md`.
