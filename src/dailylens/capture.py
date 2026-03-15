import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image

from dailylens.config import SCREENSHOT_DIR, MAX_SCREENSHOT_WIDTH


def take_screenshot() -> Path | None:
    """Take a screenshot using macOS screencapture and return the file path."""
    timestamp = datetime.now()
    date_dir = SCREENSHOT_DIR / timestamp.strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)

    filename = timestamp.strftime("%H-%M-%S") + ".png"
    filepath = date_dir / filename

    result = subprocess.run(
        ["screencapture", "-x", "-C", str(filepath)],
        capture_output=True,
        timeout=10,
    )

    if result.returncode != 0 or not filepath.exists():
        return None

    _resize_screenshot(filepath)
    return filepath


def _resize_screenshot(filepath: Path) -> None:
    """Resize screenshot to reduce file size and API costs."""
    with Image.open(filepath) as img:
        if img.width > MAX_SCREENSHOT_WIDTH:
            ratio = MAX_SCREENSHOT_WIDTH / img.width
            new_size = (MAX_SCREENSHOT_WIDTH, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            img.save(filepath, optimize=True)


def get_active_app_name() -> str:
    """Get the name of the currently active application on macOS."""
    script = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell
    return frontApp
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""
