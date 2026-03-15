"""Language-specific prompt templates for DailyLens."""

ANALYZE_PROMPTS = {
    "ko": {
        "prompt": """아래 경로의 스크린샷 파일을 읽고, 사용자가 현재 무엇을 하고 있는지 분석해주세요.

스크린샷 경로: {screenshot_path}
{app_info}
{context_section}
반드시 아래 JSON 형식으로만 응답해주세요. 다른 텍스트는 포함하지 마세요:
{{"description": "사용자가 하고 있는 활동을 1-2문장으로 설명", "category": "코딩/문서작성/이메일/웹브라우징/미팅/디자인/커뮤니케이션/기타 중 하나"}}""",
        "context_header": """
아래는 이전 캡처 기록입니다. 이 맥락을 참고하여 현재 활동이 이전 작업의 연속인지, 새로운 작업으로 전환했는지 판단해주세요.
이전 작업의 연속이라면 "~를 계속 진행 중" 등으로, 전환했다면 "~에서 ~로 전환" 등으로 표현해주세요.

### 이전 캡처 기록
{context_entries}
""",
        "context_entry": "[{time}] {app} — {description}",
        "app_info": "현재 활성 앱: {app_name}",
        "categories": "코딩/문서작성/이메일/웹브라우징/미팅/디자인/커뮤니케이션/기타",
        "fallback_category": "기타",
        "error_analyze": "분석 실패",
        "error_timeout": "분석 시간 초과",
        "error_not_found": "claude CLI를 찾을 수 없습니다",
    },
    "en": {
        "prompt": """Read the screenshot file at the path below and analyze what the user is currently doing.

Screenshot path: {screenshot_path}
{app_info}
{context_section}
Respond ONLY in the JSON format below. Do not include any other text:
{{"description": "Describe the user's activity in 1-2 sentences", "category": "one of: coding/writing/email/browsing/meeting/design/communication/other"}}""",
        "context_header": """
Below are recent capture records. Use this context to determine whether the current activity is a continuation of previous work or a switch to something new.
If continuing, say "Continuing to..." or similar. If switching, say "Switched from ... to ..." or similar.

### Recent capture history
{context_entries}
""",
        "context_entry": "[{time}] {app} — {description}",
        "app_info": "Currently active app: {app_name}",
        "categories": "coding/writing/email/browsing/meeting/design/communication/other",
        "fallback_category": "other",
        "error_analyze": "Analysis failed",
        "error_timeout": "Analysis timed out",
        "error_not_found": "claude CLI not found",
    },
    "ja": {
        "prompt": """以下のパスのスクリーンショットファイルを読み、ユーザーが現在何をしているか分析してください。

スクリーンショットパス: {screenshot_path}
{app_info}
{context_section}
必ず以下のJSON形式のみで回答してください。他のテキストは含めないでください:
{{"description": "ユーザーの活動を1-2文で説明", "category": "コーディング/文書作成/メール/ウェブ閲覧/ミーティング/デザイン/コミュニケーション/その他 のいずれか"}}""",
        "context_header": """
以下は最近のキャプチャ記録です。このコンテキストを参考に、現在の活動が前の作業の継続か、新しい作業への切り替えかを判断してください。
継続の場合は「～を継続中」、切り替えの場合は「～から～に切り替え」などと表現してください。

### 最近のキャプチャ記録
{context_entries}
""",
        "context_entry": "[{time}] {app} — {description}",
        "app_info": "現在アクティブなアプリ: {app_name}",
        "categories": "コーディング/文書作成/メール/ウェブ閲覧/ミーティング/デザイン/コミュニケーション/その他",
        "fallback_category": "その他",
        "error_analyze": "分析失敗",
        "error_timeout": "分析タイムアウト",
        "error_not_found": "claude CLIが見つかりません",
    },
    "zh": {
        "prompt": """请读取以下路径的截图文件，分析用户当前正在做什么。

截图路径: {screenshot_path}
{app_info}
{context_section}
请仅以下面的JSON格式回答，不要包含其他文字:
{{"description": "用1-2句话描述用户的活动", "category": "编程/文档/邮件/浏览网页/会议/设计/沟通/其他 之一"}}""",
        "context_header": """
以下是最近的截图记录。请参考此上下文，判断当前活动是之前工作的延续还是切换到了新任务。
如果是延续，请说"继续..."；如果是切换，请说"从...切换到..."。

### 最近截图记录
{context_entries}
""",
        "context_entry": "[{time}] {app} — {description}",
        "app_info": "当前活跃应用: {app_name}",
        "categories": "编程/文档/邮件/浏览网页/会议/设计/沟通/其他",
        "fallback_category": "其他",
        "error_analyze": "分析失败",
        "error_timeout": "分析超时",
        "error_not_found": "找不到claude CLI",
    },
}

SUMMARY_PROMPTS = {
    "ko": {
        "prompt": """아래는 사용자의 하루 동안의 화면 캡처 분석 기록입니다. 이를 바탕으로 하루 업무 내용을 정리해주세요.

## 요구사항
1. **타임라인**: 시간대별로 주요 활동을 정리 (예: 09:00-10:30 코드 리뷰)
2. **업무 요약**: 오늘 한 일을 3-5개 항목으로 정리
3. **카테고리별 시간**: 각 카테고리(코딩, 문서작성 등)에 대략 얼마나 시간을 썼는지
4. **특이사항**: 주목할만한 패턴이나 특이사항이 있으면 언급

한국어로 작성해주세요. 마크다운 형식으로 깔끔하게 정리해주세요.

## 캡처 기록
{captures_text}""",
        "record_format": "[{time}] 앱: {app} | 카테고리: {category}\n{description}",
        "no_captures": "{date} 에 기록된 캡처가 없습니다.",
        "error_failed": "요약 생성에 실패했습니다.",
        "error_timeout": "요약 생성 시간이 초과되었습니다.",
        "error_not_found": "claude CLI를 찾을 수 없습니다. Claude Code가 설치되어 있는지 확인해주세요.",
    },
    "en": {
        "prompt": """Below are the screen capture analysis records from the user's day. Please organize a daily work summary based on these records.

## Requirements
1. **Timeline**: Organize major activities by time blocks (e.g., 09:00-10:30 Code review)
2. **Work Summary**: Summarize the day's work in 3-5 items
3. **Time by Category**: Approximate time spent on each category (coding, writing, etc.)
4. **Notable Patterns**: Mention any noteworthy patterns or observations

Write in English. Use clean markdown formatting.

## Capture Records
{captures_text}""",
        "record_format": "[{time}] App: {app} | Category: {category}\n{description}",
        "no_captures": "No captures recorded for {date}.",
        "error_failed": "Failed to generate summary.",
        "error_timeout": "Summary generation timed out.",
        "error_not_found": "claude CLI not found. Please check that Claude Code is installed.",
    },
    "ja": {
        "prompt": """以下はユーザーの一日の画面キャプチャ分析記録です。これを基に一日の業務内容をまとめてください。

## 要件
1. **タイムライン**: 時間帯別に主要な活動を整理（例: 09:00-10:30 コードレビュー）
2. **業務要約**: 今日行ったことを3-5項目でまとめる
3. **カテゴリ別時間**: 各カテゴリ（コーディング、文書作成など）にどのくらい時間を使ったか
4. **特記事項**: 注目すべきパターンや特記事項があれば言及

日本語で作成してください。マークダウン形式できれいにまとめてください。

## キャプチャ記録
{captures_text}""",
        "record_format": "[{time}] アプリ: {app} | カテゴリ: {category}\n{description}",
        "no_captures": "{date} のキャプチャ記録がありません。",
        "error_failed": "要約の生成に失敗しました。",
        "error_timeout": "要約の生成がタイムアウトしました。",
        "error_not_found": "claude CLIが見つかりません。Claude Codeがインストールされているか確認してください。",
    },
    "zh": {
        "prompt": """以下是用户一天的屏幕截图分析记录。请根据这些记录整理每日工作总结。

## 要求
1. **时间线**: 按时间段整理主要活动（例: 09:00-10:30 代码审查）
2. **工作总结**: 将今天的工作整理为3-5个要点
3. **分类用时**: 各类别（编程、文档等）大约花了多少时间
4. **特别说明**: 如有值得注意的模式或特别事项请说明

请用中文撰写，使用整洁的Markdown格式。

## 截图记录
{captures_text}""",
        "record_format": "[{time}] 应用: {app} | 类别: {category}\n{description}",
        "no_captures": "{date} 没有记录的截图。",
        "error_failed": "生成总结失败。",
        "error_timeout": "生成总结超时。",
        "error_not_found": "找不到claude CLI。请确认Claude Code已安装。",
    },
}


def get_analyze_prompt(lang: str) -> dict:
    return ANALYZE_PROMPTS.get(lang, ANALYZE_PROMPTS["en"])


def get_summary_prompt(lang: str) -> dict:
    return SUMMARY_PROMPTS.get(lang, SUMMARY_PROMPTS["en"])
