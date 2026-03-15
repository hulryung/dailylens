import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCREENSHOT_DIR = BASE_DIR / os.getenv("SCREENSHOT_DIR", "screenshots")
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "dailylens.db")
CAPTURE_INTERVAL_SECONDS = int(os.getenv("CAPTURE_INTERVAL_SECONDS", "60"))
MAX_SCREENSHOT_WIDTH = int(os.getenv("MAX_SCREENSHOT_WIDTH", "1280"))
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "sonnet")
DUPLICATE_THRESHOLD = int(os.getenv("DUPLICATE_THRESHOLD", "95"))
LANGUAGE = os.getenv("LANGUAGE", "ko")

# Apps/windows to skip capturing (sensitive content)
SKIP_APPS = [
    s.strip() for s in
    os.getenv("SKIP_APPS", "1Password,Keychain Access,SecurityAgent,loginwindow").split(",")
]

# Window title keywords that trigger skipping
SKIP_TITLE_KEYWORDS = [
    s.strip() for s in
    os.getenv("SKIP_TITLE_KEYWORDS", "password,비밀번호,암호,private,secret,credential,로그인,signin,sign in").split(",")
]

SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
