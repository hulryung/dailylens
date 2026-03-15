import sqlite3
from datetime import datetime, date

from dailylens.config import DB_PATH


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            screenshot_path TEXT NOT NULL,
            description TEXT,
            app_name TEXT,
            category TEXT,
            ocr_text TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS daily_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            summary TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_captures_timestamp ON captures(timestamp);
        CREATE INDEX IF NOT EXISTS idx_summaries_date ON daily_summaries(date);
    """)
    # Add ocr_text column if missing (migration for existing DBs)
    try:
        conn.execute("ALTER TABLE captures ADD COLUMN ocr_text TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass  # column already exists
    conn.close()


def save_capture(timestamp: str, screenshot_path: str, description: str,
                 app_name: str = "", category: str = "", ocr_text: str = "") -> int:
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO captures (timestamp, screenshot_path, description, app_name, category, ocr_text) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (timestamp, screenshot_path, description, app_name, category, ocr_text),
    )
    conn.commit()
    capture_id = cursor.lastrowid
    conn.close()
    return capture_id


def get_captures_for_date(target_date: date) -> list[dict]:
    conn = get_db()
    date_str = target_date.isoformat()
    rows = conn.execute(
        "SELECT * FROM captures WHERE timestamp LIKE ? ORDER BY timestamp",
        (f"{date_str}%",),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_daily_summary(target_date: date, summary: str) -> None:
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO daily_summaries (date, summary, created_at) VALUES (?, ?, ?)",
        (target_date.isoformat(), summary, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_daily_summary(target_date: date) -> str | None:
    conn = get_db()
    row = conn.execute(
        "SELECT summary FROM daily_summaries WHERE date = ?",
        (target_date.isoformat(),),
    ).fetchone()
    conn.close()
    return row["summary"] if row else None


def get_all_summary_dates() -> list[str]:
    conn = get_db()
    rows = conn.execute(
        "SELECT date FROM daily_summaries ORDER BY date DESC"
    ).fetchall()
    conn.close()
    return [row["date"] for row in rows]


def get_recent_captures(limit: int = 5) -> list[dict]:
    """Get the most recent N captures (excluding skipped ones)."""
    conn = get_db()
    rows = conn.execute(
        "SELECT timestamp, app_name, category, description FROM captures "
        "WHERE category != '스킵됨' AND description != '' "
        "ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in reversed(rows)]


def search_captures(query: str, limit: int = 50) -> list[dict]:
    """Full-text search across OCR text and descriptions."""
    conn = get_db()
    pattern = f"%{query}%"
    rows = conn.execute(
        "SELECT * FROM captures "
        "WHERE (ocr_text LIKE ? OR description LIKE ?) AND category != '스킵됨' "
        "ORDER BY timestamp DESC LIMIT ?",
        (pattern, pattern, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_capture_dates() -> list[str]:
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT substr(timestamp, 1, 10) as date FROM captures ORDER BY date DESC"
    ).fetchall()
    conn.close()
    return [row["date"] for row in rows]
