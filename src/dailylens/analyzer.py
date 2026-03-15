import json
import logging
import subprocess
from pathlib import Path

from dailylens.config import CLAUDE_MODEL, LANGUAGE
from dailylens.prompts import get_analyze_prompt

logger = logging.getLogger("dailylens")


def analyze_screenshot(screenshot_path: Path, app_name: str = "") -> dict:
    """Analyze a screenshot using claude CLI."""
    t = get_analyze_prompt(LANGUAGE)

    app_info = t["app_info"].format(app_name=app_name) if app_name else ""
    prompt = t["prompt"].format(screenshot_path=screenshot_path, app_info=app_info)

    try:
        result = subprocess.run(
            [
                "claude", "-p", prompt,
                "--model", CLAUDE_MODEL,
                "--allowedTools", "Read",
                "--output-format", "text",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            logger.error(f"claude CLI failed: {result.stderr}")
            return {"description": t["error_analyze"], "category": t["fallback_category"]}

        output = result.stdout.strip()
        return _parse_response(output, t["fallback_category"])

    except subprocess.TimeoutExpired:
        logger.error("claude CLI timed out")
        return {"description": t["error_timeout"], "category": t["fallback_category"]}
    except FileNotFoundError:
        logger.error("claude CLI not found. Is Claude Code installed?")
        return {"description": t["error_not_found"], "category": t["fallback_category"]}


def _parse_response(output: str, fallback_category: str) -> dict:
    """Parse JSON response from claude CLI output."""
    try:
        start = output.find("{")
        end = output.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(output[start:end])
            return {
                "description": data.get("description", output),
                "category": data.get("category", fallback_category),
            }
    except json.JSONDecodeError:
        pass

    return {"description": output, "category": fallback_category}
