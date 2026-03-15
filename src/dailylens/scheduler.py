import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from dailylens.capture import take_screenshot, get_active_app_name, should_skip_capture, is_duplicate_screenshot
from dailylens.analyzer import analyze_screenshot
from dailylens.storage import save_capture
from dailylens.config import CAPTURE_INTERVAL_SECONDS

logger = logging.getLogger("dailylens")


def capture_and_analyze() -> None:
    """Take a screenshot, analyze it, and save the result."""
    try:
        # Check if capture should be skipped
        skip, reason = should_skip_capture()
        if skip:
            logger.info(f"Capture skipped: {reason}")
            timestamp = datetime.now().isoformat()
            save_capture(
                timestamp=timestamp,
                screenshot_path="",
                description=reason,
                app_name="",
                category="스킵됨",
            )
            return

        app_name = get_active_app_name()
        screenshot_path = take_screenshot()

        if screenshot_path is None:
            logger.warning("Failed to take screenshot")
            return

        logger.info(f"Screenshot saved: {screenshot_path}")

        # Skip if screenshot is same as previous
        if is_duplicate_screenshot(screenshot_path):
            logger.info("Capture skipped: duplicate screenshot")
            screenshot_path.unlink(missing_ok=True)
            return

        result = analyze_screenshot(screenshot_path, app_name=app_name)

        timestamp = datetime.now().isoformat()
        save_capture(
            timestamp=timestamp,
            screenshot_path=str(screenshot_path),
            description=result["description"],
            app_name=app_name,
            category=result["category"],
        )
        logger.info(f"Capture analyzed: {result['category']} - {app_name}")

    except Exception as e:
        logger.error(f"Capture failed: {e}", exc_info=True)


def start_scheduler() -> BackgroundScheduler:
    """Start the background scheduler for periodic captures."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        capture_and_analyze,
        "interval",
        seconds=CAPTURE_INTERVAL_SECONDS,
        id="capture_job",
        max_instances=1,
    )
    scheduler.start()
    logger.info(f"Scheduler started: capturing every {CAPTURE_INTERVAL_SECONDS}s")
    return scheduler
