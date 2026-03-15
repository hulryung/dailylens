from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dailylens.config import BASE_DIR, SCREENSHOT_DIR
from dailylens.storage import (
    get_captures_for_date,
    get_daily_summary,
    get_capture_dates,
    get_all_summary_dates,
)
from dailylens.summarizer import generate_daily_summary

app = FastAPI(title="DailyLens")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    today = date.today()
    dates = get_capture_dates()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "today": today.isoformat(),
        "dates": dates,
    })


@app.get("/api/captures/{target_date}")
async def api_captures(target_date: str):
    d = date.fromisoformat(target_date)
    captures = get_captures_for_date(d)
    for c in captures:
        path = Path(c["screenshot_path"])
        c["screenshot_url"] = f"/screenshots/{path.parent.name}/{path.name}"
    return {"date": target_date, "captures": captures}


@app.get("/api/summary/{target_date}")
async def api_summary(target_date: str, regenerate: bool = False):
    d = date.fromisoformat(target_date)
    summary = get_daily_summary(d)
    if summary is None or regenerate:
        summary = generate_daily_summary(d)
    return {"date": target_date, "summary": summary}


@app.get("/screenshots/{date_dir}/{filename}")
async def serve_screenshot(date_dir: str, filename: str):
    filepath = SCREENSHOT_DIR / date_dir / filename
    if not filepath.exists():
        return HTMLResponse("Not found", status_code=404)
    return FileResponse(filepath)
