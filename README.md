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
- **Context-aware continuity** — remembers recent activity to understand work flow (e.g., "continuing code review" vs "switched from email to coding")
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
| `CONTEXT_SIZE` | `5` | Number of recent captures for context (0 to disable) |
| `DUPLICATE_THRESHOLD` | `95` | Skip if similarity >= this % (0-100) |
| `SKIP_APPS` | `1Password,Keychain Access,...` | Comma-separated apps to skip |
| `SKIP_TITLE_KEYWORDS` | `password,secret,...` | Window title keywords to skip |
| `SCREENSHOT_DIR` | `screenshots` | Screenshot storage directory |
| `DB_PATH` | `dailylens.db` | SQLite database path |

## Multi-language support

DailyLens supports multiple languages for screenshot analysis and daily summaries. Set the `LANGUAGE` variable in your `.env` file:

```bash
# .env
LANGUAGE=en
```

| Code | Language | Analysis example | Categories |
|------|----------|-----------------|------------|
| `ko` | Korean (default) | "터미널에서 코드를 편집하고 있다" | 코딩, 문서작성, 이메일, 웹브라우징, 미팅, 디자인, 커뮤니케이션, 기타 |
| `en` | English | "Editing code in the terminal" | coding, writing, email, browsing, meeting, design, communication, other |
| `ja` | Japanese | "ターミナルでコードを編集中" | コーディング, 文書作成, メール, ウェブ閲覧, ミーティング, デザイン, コミュニケーション, その他 |
| `zh` | Chinese | "在终端编辑代码" | 编程, 文档, 邮件, 浏览网页, 会议, 设计, 沟通, 其他 |

To add a new language, add entries to the `ANALYZE_PROMPTS` and `SUMMARY_PROMPTS` dictionaries in `src/dailylens/prompts.py`.

## Privacy & Data Security

**DailyLens never sends your data to any external server.** All screenshots and analysis results are stored exclusively on your local machine.

### Where your data lives

| Data | Location | Leaves your machine? |
|------|----------|---------------------|
| Screenshots | `screenshots/` directory | No |
| Analysis results | `dailylens.db` (SQLite) | No |
| Daily summaries | `dailylens.db` (SQLite) | No |
| Configuration | `.env` file | No |

### How AI analysis works

DailyLens uses the locally installed `claude` CLI (Claude Code) to analyze screenshots. The `claude` CLI runs on your machine as part of your existing Claude Code subscription — there are no API keys, no third-party services, and no external endpoints involved. The analysis prompt and screenshot are processed through the Claude Code CLI pipe mode (`claude -p`), which operates within your authenticated session.

### No network calls from DailyLens

- DailyLens itself makes **zero network requests**. It does not contain any HTTP client code, upload endpoints, or telemetry.
- The only process that communicates externally is the `claude` CLI, which is managed by Anthropic's Claude Code and subject to its own [privacy policy](https://www.anthropic.com/privacy).
- The web dashboard runs on `localhost` only and is not exposed to the internet.

### Built-in protections

- **Sensitive screen filtering** — automatically skips password managers (1Password, Keychain Access), lock screens, and windows with configurable keywords (password, secret, credential, etc.)
- **Duplicate detection** — skips unchanged screens to minimize unnecessary data storage
- **Local-only web UI** — dashboard binds to `localhost`, inaccessible from other machines
- **`.gitignore` configured** — screenshots, database, and `.env` files are excluded from version control by default

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
