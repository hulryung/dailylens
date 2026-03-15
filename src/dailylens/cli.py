import argparse
import logging
import sys
from datetime import date

import uvicorn

from dailylens.storage import init_db


def main():
    parser = argparse.ArgumentParser(description="DailyLens - AI-powered daily work summarizer")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # start command - run capture scheduler + web server
    start_parser = subparsers.add_parser("start", help="Start capturing and web server")
    start_parser.add_argument("--port", type=int, default=8585, help="Web server port")
    start_parser.add_argument("--no-capture", action="store_true", help="Start web server only, no capture")

    # summary command - generate summary for a date
    summary_parser = subparsers.add_parser("summary", help="Generate daily summary")
    summary_parser.add_argument("--date", type=str, default=None, help="Date (YYYY-MM-DD), defaults to today")

    # capture command - take a single screenshot
    subparsers.add_parser("capture", help="Take a single screenshot and analyze it")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    init_db()

    if args.command == "start":
        _cmd_start(args)
    elif args.command == "summary":
        _cmd_summary(args)
    elif args.command == "capture":
        _cmd_capture()
    else:
        parser.print_help()


def _cmd_start(args):
    if not args.no_capture:
        from dailylens.scheduler import start_scheduler
        scheduler = start_scheduler()

    print(f"🔍 DailyLens running at http://localhost:{args.port}")
    print("   Press Ctrl+C to stop\n")

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


if __name__ == "__main__":
    main()
