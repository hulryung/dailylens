import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image

from dailylens.config import (
    SCREENSHOT_DIR, MAX_SCREENSHOT_WIDTH,
    SKIP_APPS, SKIP_TITLE_KEYWORDS,
    DUPLICATE_THRESHOLD,
)

# Store previous screenshot hash for duplicate detection
_previous_hash: int | None = None


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


def get_active_window_title() -> str:
    """Get the title of the currently active window on macOS."""
    script = '''
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        try
            set winTitle to name of front window of frontApp
        on error
            set winTitle to ""
        end try
    end tell
    return winTitle
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


def is_screen_locked() -> bool:
    """Check if the macOS screen is locked."""
    try:
        result = subprocess.run(
            ["python3", "-c",
             "import Quartz; d=Quartz.CGSessionCopyCurrentDictionary(); "
             "print(d.get('CGSSessionScreenIsLocked', 0))"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() == "1"
    except Exception:
        return False


def should_skip_capture() -> tuple[bool, str]:
    """Check if capture should be skipped due to sensitive content.

    Returns (should_skip, reason).
    """
    # Screen locked
    if is_screen_locked():
        return True, "화면 잠금 상태"

    # Sensitive app check
    app_name = get_active_app_name()
    for skip_app in SKIP_APPS:
        if skip_app and skip_app.lower() in app_name.lower():
            return True, f"민감 앱 감지: {app_name}"

    # Window title keyword check
    window_title = get_active_window_title()
    title_lower = window_title.lower()
    for keyword in SKIP_TITLE_KEYWORDS:
        if keyword and keyword.lower() in title_lower:
            return True, f"민감 키워드 감지: '{keyword}' in '{window_title}'"

    return False, ""


def compute_dhash(image_path: Path, hash_size: int = 16) -> int:
    """Compute difference hash (dhash) of an image.

    Resizes to (hash_size+1, hash_size) grayscale, then compares adjacent
    pixels to produce a hash_size*hash_size bit hash.
    """
    with Image.open(image_path) as img:
        img = img.convert("L").resize((hash_size + 1, hash_size), Image.LANCZOS)
        pixels = list(img.getdata())

    hash_val = 0
    for row in range(hash_size):
        for col in range(hash_size):
            offset = row * (hash_size + 1) + col
            if pixels[offset] < pixels[offset + 1]:
                hash_val |= 1 << (row * hash_size + col)
    return hash_val


def _hamming_distance(h1: int, h2: int) -> int:
    """Count differing bits between two hashes."""
    return bin(h1 ^ h2).count("1")


def is_duplicate_screenshot(image_path: Path) -> bool:
    """Check if screenshot is a duplicate of the previous one.

    Returns True if similarity >= DUPLICATE_THRESHOLD%.
    """
    global _previous_hash

    current_hash = compute_dhash(image_path)
    if _previous_hash is None:
        _previous_hash = current_hash
        return False

    total_bits = 16 * 16  # hash_size=16
    distance = _hamming_distance(_previous_hash, current_hash)
    similarity = ((total_bits - distance) / total_bits) * 100

    _previous_hash = current_hash
    return similarity >= DUPLICATE_THRESHOLD
