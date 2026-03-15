import argparse
import logging
import os
import shutil
import subprocess
from datetime import date
from pathlib import Path
from textwrap import dedent

import uvicorn

from dailylens.storage import init_db
from dailylens.config import BASE_DIR


PLIST_LABEL = "com.dailylens.agent"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{PLIST_LABEL}.plist"


def main():
    parser = argparse.ArgumentParser(description="DailyLens - AI-powered daily work summarizer")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # start command
    start_parser = subparsers.add_parser("start", help="Start capturing and web server")
    start_parser.add_argument("--port", type=int, default=8585, help="Web server port")
    start_parser.add_argument("--no-capture", action="store_true", help="Start web server only")

    # summary command
    summary_parser = subparsers.add_parser("summary", help="Generate daily summary")
    summary_parser.add_argument("--date", type=str, default=None, help="Date (YYYY-MM-DD)")

    # capture command
    subparsers.add_parser("capture", help="Take a single screenshot and analyze it")

    # install command
    install_parser = subparsers.add_parser("install", help="Install as macOS launch agent (auto-start)")
    install_parser.add_argument("--port", type=int, default=8585, help="Web server port")

    # uninstall command
    subparsers.add_parser("uninstall", help="Uninstall macOS launch agent")

    # status command
    subparsers.add_parser("status", help="Show launch agent status")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    init_db()

    commands = {
        "start": _cmd_start,
        "summary": _cmd_summary,
        "capture": lambda a: _cmd_capture(),
        "install": _cmd_install,
        "uninstall": lambda a: _cmd_uninstall(),
        "status": lambda a: _cmd_status(),
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


def _cmd_start(args):
    if not args.no_capture:
        from dailylens.scheduler import start_scheduler
        start_scheduler()

    print(f"DailyLens running at http://localhost:{args.port}")
    print("Press Ctrl+C to stop\n")

    from dailylens.server import app
    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="warning")


def _cmd_summary(args):
    from dailylens.summarizer import generate_daily_summary

    target = date.fromisoformat(args.date) if args.date else date.today()
    print(f"Generating summary for {target}...\n")
    summary = generate_daily_summary(target)
    print(summary)


def _cmd_capture():
    from dailylens.scheduler import capture_and_analyze

    print("Taking screenshot and analyzing...")
    capture_and_analyze()
    print("Done!")


def _cmd_install(args):
    dailylens_bin = shutil.which("dailylens")
    if not dailylens_bin:
        # Fall back to uv run
        uv_bin = shutil.which("uv")
        if not uv_bin:
            print("Error: neither 'dailylens' nor 'uv' found in PATH")
            return
        program_args = f"""
    <string>{uv_bin}</string>
    <string>run</string>
    <string>--project</string>
    <string>{BASE_DIR}</string>
    <string>dailylens</string>
    <string>start</string>
    <string>--port</string>
    <string>{args.port}</string>"""
    else:
        program_args = f"""
    <string>{dailylens_bin}</string>
    <string>start</string>
    <string>--port</string>
    <string>{args.port}</string>"""

    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    plist_content = dedent(f"""\
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
      "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>{PLIST_LABEL}</string>
        <key>ProgramArguments</key>
        <array>{program_args}
        </array>
        <key>WorkingDirectory</key>
        <string>{BASE_DIR}</string>
        <key>RunAtLoad</key>
        <true/>
        <key>KeepAlive</key>
        <true/>
        <key>StandardOutPath</key>
        <string>{log_dir}/dailylens.log</string>
        <key>StandardErrorPath</key>
        <string>{log_dir}/dailylens.err</string>
        <key>EnvironmentVariables</key>
        <dict>
            <key>PATH</key>
            <string>{os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")}</string>
        </dict>
    </dict>
    </plist>
    """)

    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLIST_PATH.write_text(plist_content)

    subprocess.run(["launchctl", "load", str(PLIST_PATH)], check=True)
    print(f"DailyLens installed as launch agent")
    print(f"  Plist: {PLIST_PATH}")
    print(f"  Logs:  {log_dir}/")
    print(f"  Web:   http://localhost:{args.port}")
    print(f"\nDailyLens will auto-start on login.")
    print(f"To uninstall: dailylens uninstall")


def _cmd_uninstall():
    if not PLIST_PATH.exists():
        print("DailyLens launch agent is not installed.")
        return

    subprocess.run(["launchctl", "unload", str(PLIST_PATH)])
    PLIST_PATH.unlink()
    print(f"DailyLens launch agent uninstalled.")
    print(f"Removed: {PLIST_PATH}")


def _cmd_status():
    result = subprocess.run(
        ["launchctl", "list", PLIST_LABEL],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"DailyLens launch agent: RUNNING")
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")
    else:
        print(f"DailyLens launch agent: NOT RUNNING")
        if PLIST_PATH.exists():
            print(f"  Plist exists at {PLIST_PATH} but agent is not loaded")
        else:
            print(f"  Not installed. Run 'dailylens install' to set up.")


if __name__ == "__main__":
    main()
