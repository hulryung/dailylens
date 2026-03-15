import logging
import subprocess
from datetime import date

from dailylens.config import CLAUDE_MODEL
from dailylens.storage import get_captures_for_date, save_daily_summary

logger = logging.getLogger("dailylens")

SUMMARY_PROMPT = """아래는 사용자의 하루 동안의 화면 캡처 분석 기록입니다. 이를 바탕으로 하루 업무 내용을 정리해주세요.

## 요구사항
1. **타임라인**: 시간대별로 주요 활동을 정리 (예: 09:00-10:30 코드 리뷰)
2. **업무 요약**: 오늘 한 일을 3-5개 항목으로 정리
3. **카테고리별 시간**: 각 카테고리(코딩, 문서작성 등)에 대략 얼마나 시간을 썼는지
4. **특이사항**: 주목할만한 패턴이나 특이사항이 있으면 언급

한국어로 작성해주세요. 마크다운 형식으로 깔끔하게 정리해주세요.

## 캡처 기록
{captures_text}"""


def generate_daily_summary(target_date: date) -> str:
    """Generate a daily summary from all captures of the given date."""
    captures = get_captures_for_date(target_date)

    if not captures:
        return f"{target_date.isoformat()} 에 기록된 캡처가 없습니다."

    records = []
    for c in captures:
        time_str = c["timestamp"].split("T")[-1][:5] if "T" in c["timestamp"] else c["timestamp"][11:16]
        app = c.get("app_name", "")
        desc = c.get("description", "")
        cat = c.get("category", "")
        records.append(f"[{time_str}] 앱: {app} | 카테고리: {cat}\n{desc}")

    captures_text = "\n---\n".join(records)
    prompt = SUMMARY_PROMPT.format(captures_text=captures_text)

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
            return "요약 생성에 실패했습니다."

        summary = result.stdout.strip()

    except subprocess.TimeoutExpired:
        summary = "요약 생성 시간이 초과되었습니다."
    except FileNotFoundError:
        summary = "claude CLI를 찾을 수 없습니다. Claude Code가 설치되어 있는지 확인해주세요."

    save_daily_summary(target_date, summary)
    return summary
