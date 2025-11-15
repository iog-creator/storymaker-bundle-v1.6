# Live Monitoring Dashboard

The StoryMaker Live Dashboard provides real-time visual monitoring of all system components with a terminal-based interface using Node.js + blessed/blessed-contrib.

## Quick Start

```bash
# Launch the live dashboard
make ui.live

# Press 'q' to exit
```

## Features

### Proof-Driven Design
- **Terse success**: One-line confirmation when systems are healthy
- **Detailed errors only**: Full error information only when something fails
- **Concrete proof**: Success states include verifiable artifacts (SHA, counts, timestamps)
- **First-fail focus**: Guard failures show the specific proof file and reason

### Real-Time Monitoring
- **1-second refresh rate** for live updates
- **8 monitoring tiles** in a 3x3 grid layout (3 rows, 3 columns)
- **Events log** in the bottom row spanning all columns
- **Scrollable content** with full information display
- **Color-coded status indicators**:
  - 🟢 Green: Healthy/OK
  - 🟡 Yellow: Warnings
  - 🔴 Red: Errors
  - 🔵 Cyan: Busy/Active

### Live File Watching
- **Blinking indicators** when files change
- **Real-time activity logging** in the events panel
- **Automatic status updates** when documents are modified

### Visual Feedback
- **Border color changes** based on system health
- **Content updates** showing current status
- **Blinking effects** during active operations
- **Event timestamps** for all activities

### Navigation & Scrolling
- **Tile navigation**: Use ← → or h/l to move between tiles
- **Content scrolling**: Use ↑ ↓ or j/k to scroll within the focused tile
- **Quick navigation**: Page Up/Down for 5-line jumps, Home/End for top/bottom
- **Help overlay**: Press ? to see all keyboard shortcuts
- **Focus indicators**: Current tile has cyan border and is scrollable
- **Independent scrolling**: Each tile scrolls independently when focused

## Monitored Systems

### 1. LM Studio
- **Success**: `ping ✔` (terse, no extra info)
- **Failure**: Shows first line of error response
- **Status**: Green when healthy, Red when unreachable

### 2. Groq (Creative)
- **Success**: `ping ✔ env ✓` (terse confirmation)
- **Failure**: Shows missing environment variables or HTTP error
- **Status**: Green when all env vars present, Red when missing

### 3. AgentPM
- **Document monitoring**: Watches SSOT files for changes
- **Last change tracking**: Shows time since last modification
- **Status**: Green when files exist and recent

### 4. StoryMaker
- **Implementation status**: Monitors key documentation
- **Change detection**: Tracks updates to implementation docs
- **Status**: Green when files are current

### 5. SSOT Rules (.mdc)
- **Success**: `rules: N (Δ±K)` with delta since last refresh
- **Failure**: Shows missing directory or suggests `make rules.emit`
- **Status**: Green when rules present, Yellow when empty

### 6. Envelopes & Proofs
- **Success**: `proofs: N • latest:file.json • age:time • latency_ms:X`
- **Failure**: Shows missing directory or no proofs
- **Status**: Green when proofs exist, Yellow when empty

### 7. Docs Autosync
- **Success**: `synced ✔ • SHA:7 • age:time • files:N` (concrete proof)
- **Failure**: Shows first 2 lines of error output
- **Status**: Green when passing, Red when failing

### 8. Rerank & QA Guards
- **Success**: `✔ all guards` (terse confirmation)
- **Failure**: Shows first failing proof filename and reason
- **Status**: Green when all guards pass, Red when any fail

### 9. Events Log
- **Live activity**: Real-time logging of file changes and system events
- **Timestamped entries**: Shows when files are modified, created, or deleted
- **Scrollable history**: Full event history with timestamps
- **Status**: Always visible in bottom row spanning all columns

## Configuration

The dashboard configuration is stored in `tools/dashboard.config.json`:

```json
{
  "poll_ms": 1000,
  "tiles": [
    {
      "id": "lmstudio",
      "title": "LM Studio",
      "type": "service",
      "healthz": "http://127.0.0.1:1234/healthz",
      "info": "http://127.0.0.1:1234/v1/models"
    },
    // ... more tiles
  ]
}
```

### Customization
- **Refresh rate**: Modify `poll_ms` value
- **Add tiles**: Add new tile configurations to the `tiles` array
- **Change endpoints**: Update URLs and commands as needed

## Dependencies

The dashboard requires Node.js and npm:

```bash
# Check if Node.js is installed
node --version
npm --version

# Install dependencies
make ui.install
```

### Required Packages
- `blessed`: Terminal UI framework
- `blessed-contrib`: Grid layout and widgets
- `undici`: HTTP client for service checks
- `chokidar`: File system watching

## Troubleshooting

### Dashboard won't start
```bash
# Install Node.js (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install dependencies
make ui.install

# Check versions
node --version
npm --version
```

### Tiles showing errors
- **LM Studio**: Ensure LM Studio is running on port 1234
- **Groq**: Check that `GROQ_API_KEY` and `GROQ_MODEL` are set
- **Guards**: Verify that Python environment is set up correctly
- **Files**: Ensure the monitored files and directories exist

### Performance issues
- **Slow refresh**: Increase `poll_ms` value in config
- **High CPU**: Reduce the number of monitored files
- **Memory usage**: Restart the dashboard periodically

## Keyboard Shortcuts

- **q**: Quit the dashboard
- **Ctrl+C**: Force exit
- **← → (h/l)**: Move between tiles
- **↑ ↓ (j/k)**: Scroll current tile
- **Page Up/Down**: Scroll 5 lines at a time
- **Home/End**: Jump to top/bottom of current tile
- **?**: Toggle help overlay

## Integration

The dashboard integrates with the existing StoryMaker workflow:

```bash
# Start services
make start

# Launch dashboard in another terminal
make ui.live

# Run verification
make verify-all
```

The dashboard will show real-time status of all these operations and provide immediate feedback on system health and changes.
