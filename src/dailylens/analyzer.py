import base64
from pathlib import Path

import anthropic

from dailylens.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

ANALYZE_PROMPT = """이 스크린샷을 보고, 사용자가 현재 무엇을 하고 있는지 간결하게 한국어로 설명해주세요.

다음 형식으로 응답해주세요:
- 활동: (어떤 작업을 하고 있는지 1-2문장)
- 카테고리: (코딩, 문서작성, 이메일, 웹브라우징, 미팅, 디자인, 기타 중 하나)

불필요한 설명 없이 간결하게 답변해주세요."""


def analyze_screenshot(screenshot_path: Path, app_name: str = "") -> dict:
    """Analyze a screenshot using Claude Vision API."""
    image_data = base64.standard_b64encode(screenshot_path.read_bytes()).decode("utf-8")

    media_type = "image/png"
    if screenshot_path.suffix.lower() in (".jpg", ".jpeg"):
        media_type = "image/jpeg"

    user_content = []
    user_content.append({
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": image_data,
        },
    })

    prompt = ANALYZE_PROMPT
    if app_name:
        prompt += f"\n\n현재 활성 앱: {app_name}"

    user_content.append({"type": "text", "text": prompt})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": user_content}],
    )

    text = response.content[0].text
    description = text
    category = ""

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("- 카테고리:"):
            category = line.replace("- 카테고리:", "").strip()

    return {
        "description": description,
        "category": category,
    }
