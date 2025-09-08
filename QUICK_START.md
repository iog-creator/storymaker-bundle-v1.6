# StoryMaker Quick Start Guide

## For New Users (5 Minutes to Running)

### Step 1: Start LM Studio
1. Open LM Studio
2. Load any chat model (e.g., `qwen/qwen3-4b-2507`)
3. Start the server (it should show "Server running on http://127.0.0.1:1234")

### Step 2: Run StoryMaker
```bash
# One command to start everything
make start
```

That's it! StoryMaker will:
- ✅ Check if LM Studio is running
- ✅ Start the database
- ✅ Start all services
- ✅ Verify everything is working

### Step 3: Access StoryMaker
- **Web UI**: http://localhost:3000
- **API**: http://localhost:8000-8004

## Troubleshooting

### "LM Studio not found"
- Make sure LM Studio is running
- Check that the server is on port 1234
- Try: `curl http://127.0.0.1:1234/v1/models`

### "Database connection failed"
- Run: `make db.setup`
- This will start the database and run migrations

### "Services won't start"
- Run: `make restart`
- This will stop and restart all services

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
