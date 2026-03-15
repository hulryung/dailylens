# DailyLens

Take periodic screenshots and summarize your daily work with AI — powered by [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

No API key needed. Uses your existing Claude Code subscription via the `claude` CLI.

## How it works

```
Every 60 seconds:
  screencapture → resize → duplicate check → Claude Vision analysis → SQLite

On demand:
  Aggregate day's captures → Claude generates markdown summary
```

## Features

- **Periodic screenshot capture** — configurable interval (default: 60s)
- **AI-powered analysis** — Claude describes what you're doing in each screenshot
- **Daily summary** — timeline, task breakdown, category stats, notable patterns
- **Web dashboard** — dark-themed UI with timeline view and summary panel
- **Screenshot zoom** — click thumbnails to expand, navigate with arrow keys
- **Duplicate detection** — skips unchanged screens using perceptual hashing (dhash)
- **Sensitive screen filtering** — skips password managers, lock screens, and configurable keywords
- **Auto-start** — install as macOS launch agent to run on login

## Quick start

```bash
# Clone
git clone https://github.com/hulryung/dailylens.git
cd dailylens

# Install dependencies
uv sync

# (Optional) customize settings
cp .env.example .env

# Take a single test capture
uv run dailylens capture

# Start capturing + web dashboard
uv run dailylens start
# Open http://localhost:8585
```

## Commands

| Command | Description |
|---------|-------------|
| `dailylens start` | Start capture scheduler + web server |
| `dailylens start --no-capture` | Web server only (no capture) |
| `dailylens start --port 9090` | Use custom port |
| `dailylens capture` | Take a single screenshot and analyze |
| `dailylens summary` | Generate today's summary (terminal output) |
| `dailylens summary --date 2026-03-15` | Summary for a specific date |
| `dailylens install` | Install as macOS launch agent (auto-start on login) |
| `dailylens uninstall` | Remove launch agent |
| `dailylens status` | Check launch agent status |

## Configuration

All settings are optional. Configure via `.env` file or environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CAPTURE_INTERVAL_SECONDS` | `60` | Seconds between captures |
| `MAX_SCREENSHOT_WIDTH` | `1280` | Resize screenshots to this width |
| `CLAUDE_MODEL` | `sonnet` | Claude model to use |
| `LANGUAGE` | `ko` | Output language: `ko`, `en`, `ja`, `zh` |
| `DUPLICATE_THRESHOLD` | `95` | Skip if similarity >= this % (0-100) |
| `SKIP_APPS` | `1Password,Keychain Access,...` | Comma-separated apps to skip |
| `SKIP_TITLE_KEYWORDS` | `password,secret,...` | Window title keywords to skip |
| `SCREENSHOT_DIR` | `screenshots` | Screenshot storage directory |
| `DB_PATH` | `dailylens.db` | SQLite database path |

## Privacy

- **100% local** — all data stays on your machine
- **No API keys** — uses Claude Code CLI with your existing subscription
- **Sensitive screen filtering** — automatically skips password managers, lock screens, and configurable apps/keywords
- **Duplicate detection** — doesn't waste resources on unchanged screens
- Screenshots stored in local `screenshots/` directory, analysis in local SQLite

## Tech stack

- **Python 3.11+** with [uv](https://docs.astral.sh/uv/)
- **macOS `screencapture`** for screenshots
- **Claude Code CLI** (`claude -p`) for vision analysis and summarization
- **SQLite** for storage
- **FastAPI + Jinja2** for web dashboard
- **APScheduler** for periodic capture
- **Pillow** for image processing

## Requirements

- macOS (uses native `screencapture` command)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## License

MIT
