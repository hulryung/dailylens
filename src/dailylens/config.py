import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCREENSHOT_DIR = BASE_DIR / os.getenv("SCREENSHOT_DIR", "screenshots")
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "dailylens.db")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CAPTURE_INTERVAL_SECONDS = int(os.getenv("CAPTURE_INTERVAL_SECONDS", "60"))
MAX_SCREENSHOT_WIDTH = int(os.getenv("MAX_SCREENSHOT_WIDTH", "1280"))

SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
