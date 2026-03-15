import json
import logging
import subprocess
from pathlib import Path

from dailylens.config import CLAUDE_MODEL

logger = logging.getLogger("dailylens")

ANALYZE_PROMPT = """아래 경로의 스크린샷 파일을 읽고, 사용자가 현재 무엇을 하고 있는지 분석해주세요.

스크린샷 경로: {screenshot_path}
{app_info}

반드시 아래 JSON 형식으로만 응답해주세요. 다른 텍스트는 포함하지 마세요:
{{"description": "사용자가 하고 있는 활동을 1-2문장으로 설명", "category": "코딩/문서작성/이메일/웹브라우징/미팅/디자인/커뮤니케이션/기타 중 하나"}}"""


def analyze_screenshot(screenshot_path: Path, app_name: str = "") -> dict:
    """Analyze a screenshot using claude CLI."""
    app_info = f"현재 활성 앱: {app_name}" if app_name else ""
    prompt = ANALYZE_PROMPT.format(screenshot_path=screenshot_path, app_info=app_info)

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
            return {"description": "분석 실패", "category": "기타"}

        output = result.stdout.strip()
        return _parse_response(output)

    except subprocess.TimeoutExpired:
        logger.error("claude CLI timed out")
        return {"description": "분석 시간 초과", "category": "기타"}
    except FileNotFoundError:
        logger.error("claude CLI not found. Is Claude Code installed?")
        return {"description": "claude CLI를 찾을 수 없습니다", "category": "기타"}


def _parse_response(output: str) -> dict:
    """Parse JSON response from claude CLI output."""
    # Try to extract JSON from the output
    try:
        # Look for JSON object in the output
        start = output.find("{")
        end = output.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(output[start:end])
            return {
                "description": data.get("description", output),
                "category": data.get("category", "기타"),
            }
    except json.JSONDecodeError:
        pass

    # Fallback: use raw output as description
    return {"description": output, "category": "기타"}
