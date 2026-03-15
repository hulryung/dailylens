import logging
import subprocess
from datetime import date

from dailylens.config import CLAUDE_MODEL, LANGUAGE
from dailylens.prompts import get_summary_prompt
from dailylens.storage import get_captures_for_date, save_daily_summary

logger = logging.getLogger("dailylens")


def generate_daily_summary(target_date: date) -> str:
    """Generate a daily summary from all captures of the given date."""
    t = get_summary_prompt(LANGUAGE)
    captures = get_captures_for_date(target_date)

    if not captures:
        return t["no_captures"].format(date=target_date.isoformat())

    records = []
    for c in captures:
        time_str = c["timestamp"].split("T")[-1][:5] if "T" in c["timestamp"] else c["timestamp"][11:16]
        ocr_text = c.get("ocr_text", "")
        # Truncate OCR for summary to keep prompt manageable
        if len(ocr_text) > 500:
            ocr_text = ocr_text[:500] + "..."
        records.append(t["record_format"].format(
            time=time_str,
            app=c.get("app_name", ""),
            category=c.get("category", ""),
            description=c.get("description", ""),
            ocr_text=ocr_text if ocr_text else "(없음)",
        ))

    captures_text = "\n---\n".join(records)
    prompt = t["prompt"].format(captures_text=captures_text)

    try:
        result = subprocess.run(
            [
                "claude", "-p", prompt,
                "--model", CLAUDE_MODEL,
                "--output-format", "text",
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )

        if result.returncode != 0:
            logger.error(f"claude CLI failed: {result.stderr}")
            return t["error_failed"]

        summary = result.stdout.strip()

    except subprocess.TimeoutExpired:
        summary = t["error_timeout"]
    except FileNotFoundError:
        summary = t["error_not_found"]

    save_daily_summary(target_date, summary)
    return summary
