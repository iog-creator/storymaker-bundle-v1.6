# StoryMaker User Guide

## For Non-Technical Users

This guide is for writers, authors, and content creators who want to use StoryMaker without getting into technical details.

## What is StoryMaker?

StoryMaker is an AI-powered writing assistant that helps you:
- Create rich fictional worlds
- Develop compelling characters
- Generate story plots and dialogue
- Format screenplays professionally
- Overcome writer's block

## Getting Started

### Step 1: Install LM Studio
1. Go to [lmstudio.ai](https://lmstudio.ai)
2. Download and install LM Studio
3. Open LM Studio
4. Download a model (we recommend `qwen/qwen3-4b-2507`)
5. Click "Start Server" (it should show "Server running on http://127.0.0.1:1234")

### Step 2: Start StoryMaker
1. Open a terminal/command prompt
2. Navigate to the StoryMaker folder
3. Type: `make start`
4. Wait for "StoryMaker is ready!" message

### Step 3: Start Writing
1. Open your web browser
2. Go to: http://localhost:3000
3. Start creating!

## Using StoryMaker

### World Building
- Create fictional universes with consistent rules
- Define locations, cultures, and histories
- Build rich backstories for your settings

### Character Development
- Create detailed character profiles
- Generate character dialogue and interactions
- Develop character arcs and motivations

### Story Generation
- Generate plot ideas and story structures
- Create dialogue and scenes
- Overcome writer's block with AI suggestions

### Screenplay Formatting
- Format scripts to industry standards
- Generate proper scene headings and dialogue
- Create professional-looking screenplays

## Common Issues

### "LM Studio not found"
**What it means**: StoryMaker can't connect to LM Studio
**How to fix**: 
1. Make sure LM Studio is open
2. Make sure the server is running (should show port 1234)
3. Try restarting LM Studio

### "Database connection failed"
**What it means**: The database isn't running
**How to fix**: 
1. Make sure Docker is installed and running
2. Run: `make restart`
3. Wait a few minutes for everything to start

### "Services won't start"
**What it means**: Something is blocking the services
**How to fix**: 
1. Run: `make stop` (wait 10 seconds)
2. Run: `make start`
3. If still not working, restart your computer

## Tips for Writers

### Getting the Best Results
- Be specific in your prompts
- Provide context about your story world
- Use the character profiles you've created
- Experiment with different AI models

### Organizing Your Work
- Use the world-building tools to create consistent settings
- Keep character profiles updated
- Save your best generated content
- Use the project management features

### Overcoming Writer's Block
- Use the plot generation tools
- Try different character perspectives
- Generate dialogue for difficult scenes
- Use the world-building tools to explore new ideas

## Getting Help

### If Something Goes Wrong
1. Run: `make status` to check what's running
2. Run: `make restart` to restart everything
3. Check the troubleshooting section above

### For Technical Issues
- Check the [Quick Start Guide](QUICK_START.md)
- Look at the [README](README.md) for technical details
- Ask for help in the project's support channels

## What's Next?

Once you're comfortable with the basics:
- Explore the advanced features
- Try different AI models
- Customize the settings for your writing style
- Share your creations with the community

Remember: StoryMaker is a tool to enhance your creativity, not replace it. Use it to explore ideas, overcome blocks, and bring your stories to life!
