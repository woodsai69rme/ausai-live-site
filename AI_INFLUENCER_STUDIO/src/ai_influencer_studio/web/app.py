"""FastAPI web dashboard for AI Influencer Studio."""

from __future__ import annotations

import json
import logging
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Form, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai_influencer_studio.adapters.automation import AutomationAdapter
from ai_influencer_studio.adapters.content import ContentAdapter
from ai_influencer_studio.adapters.video import VideoAdapter
from ai_influencer_studio.audio_analysis import analyze_audio
from ai_influencer_studio.config import StudioConfig
from ai_influencer_studio.music_video_researcher import MusicVideoResearchEngine
from ai_influencer_studio.repurposer import VideoRepurposer
from ai_influencer_studio.web.auth import verify_api_key

logger = logging.getLogger(__name__)

# Optional auth dependency. If no API key is configured, requests pass through.
AuthDep = Depends(verify_api_key)


def _verify_ws_api_key(websocket: WebSocket) -> None:
    """Verify API key passed as a WebSocket query parameter, if one is configured."""
    from ai_influencer_studio.web.auth import _get_configured_key

    configured = _get_configured_key()
    if configured:
        provided = websocket.query_params.get("api_key", "")
        if provided != configured:
            raise HTTPException(status_code=403, detail="Invalid or missing API key")

app = FastAPI(title="AI Influencer Studio")

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _config() -> StudioConfig:
    return StudioConfig.from_file()


# --------------------------------------------------------------------------
# Google Drive upload runtime (background thread so the dashboard can poll)
# --------------------------------------------------------------------------
_GDRIVE_RUN: dict[str, Any] = {
    "thread": None,
    "stop_event": None,
    "running": False,
    "started_at": None,
    "last_error": None,
    "progress": None,
}


def _gdrive_uploader() -> Any:
    """Build a GDriveUploader from the current config (lazy import)."""
    from ai_influencer_studio.gdrive_uploader import GDriveUploader

    config = _config()
    return GDriveUploader(
        config.gdrive_state_path,
        folder_url=config.gdrive_folder_url,
        user_data_dir=config.gdrive_chrome_user_data_dir or None,
        cdp_url=config.gdrive_cdp_url or None,
        token_path=config.gdrive_token_path,
        client_secrets_path=config.gdrive_client_secrets_path,
        rclone_remote=config.gdrive_rclone_remote or None,
        rclone_path=config.gdrive_rclone_path,
    )


@app.get("/gdrive", response_class=HTMLResponse)
def gdrive_dashboard(request: Request, _api_key: str = AuthDep) -> HTMLResponse:
    """Watch Google Drive upload progress without the terminal."""
    return templates.TemplateResponse(request, "gdrive.html", {})


@app.get("/api/gdrive/status")
def gdrive_status(_api_key: str = AuthDep) -> JSONResponse:
    """Pending/done counts plus live progress of any background upload run."""
    uploader = _gdrive_uploader()
    status = uploader.status()
    status["running"] = bool(_GDRIVE_RUN["running"] and _GDRIVE_RUN["thread"] and _GDRIVE_RUN["thread"].is_alive())
    status["started_at"] = _GDRIVE_RUN["started_at"]
    status["last_error"] = _GDRIVE_RUN["last_error"]
    status["progress"] = _GDRIVE_RUN["progress"]
    return JSONResponse(content=status)


@app.post("/api/gdrive/collect")
def gdrive_collect(
    sources: str = Form(...),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Scan comma/newline-separated source dirs, filter, dedupe into pending."""
    uploader = _gdrive_uploader()
    source_list = [s.strip() for s in sources.replace("\n", ",").split(",") if s.strip()]
    if not source_list:
        return JSONResponse(status_code=400, content={"error": "No source directories provided"})
    try:
        result = uploader.collect(source_list)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    return JSONResponse(content=result)


@app.post("/api/gdrive/upload/start")
def gdrive_upload_start(
    batch_size: int = Form(20),
    delay: float = Form(45.0),
    headed: bool = Form(False),
    max_batches: int | None = Form(None),
    backend: str = Form(""),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Start uploading the pending list in a background thread.

    ``backend`` selects the transport: empty or ``browser`` (Playwright web UI)
    or ``drive_api`` (OAuth2, no browser). Defaults to the configured backend.
    """
    if _GDRIVE_RUN["running"] and _GDRIVE_RUN["thread"] and _GDRIVE_RUN["thread"].is_alive():
        return JSONResponse(status_code=409, content={"error": "An upload is already running"})

    config = _config()
    backend = backend or config.gdrive_backend
    if backend not in ("browser", "drive_api", "rclone"):
        return JSONResponse(status_code=400, content={"error": "backend must be 'browser', 'drive_api', or 'rclone'"})

    uploader = _gdrive_uploader()
    stop_event = threading.Event()
    _GDRIVE_RUN.update(
        stop_event=stop_event,
        running=True,
        started_at=datetime.now(UTC).isoformat(),
        last_error=None,
        progress=None,
    )

    def _worker() -> None:
        try:
            result = uploader.upload_pending(
                batch_size=batch_size,
                delay_seconds=delay,
                headless=not headed,
                max_batches=max_batches,
                stop_event=stop_event,
                on_progress=lambda snap: _GDRIVE_RUN.update(progress=snap),
                backend=backend,
            )
            _GDRIVE_RUN.update(progress=result)
        except Exception as exc:
            _GDRIVE_RUN["last_error"] = str(exc)
        finally:
            _GDRIVE_RUN["running"] = False

    thread = threading.Thread(target=_worker, name="gdrive-upload", daemon=True)
    _GDRIVE_RUN["thread"] = thread
    thread.start()
    return JSONResponse(
        status_code=202,
        content={
            "started": True,
            "message": "Upload started in background; poll /api/gdrive/status",
        },
    )


@app.post("/api/gdrive/upload/stop")
def gdrive_upload_stop(_api_key: str = AuthDep) -> JSONResponse:
    """Request a graceful stop at the next batch boundary."""
    stop_event = _GDRIVE_RUN.get("stop_event")
    if not _GDRIVE_RUN["running"] or stop_event is None:
        return JSONResponse(content={"stopped": False, "message": "No upload running"})
    stop_event.set()
    return JSONResponse(content={"stopped": True, "message": "Stop requested; will stop after the current batch"})


# --------------------------------------------------------------------------
# YouTube publishing runtime (background thread so the dashboard can poll)
# --------------------------------------------------------------------------
_YOUTUBE_RUN: dict[str, Any] = {
    "thread": None,
    "running": False,
    "started_at": None,
    "last_error": None,
    "result": None,
}


@app.get("/youtube", response_class=HTMLResponse)
def youtube_dashboard(request: Request, _api_key: str = AuthDep) -> HTMLResponse:
    """Publish finished music videos to YouTube from the browser."""
    return templates.TemplateResponse(request, "youtube.html", {})


@app.get("/api/youtube/status")
def youtube_status(_api_key: str = AuthDep) -> JSONResponse:
    """Background publish state: running, last error, and the upload result."""
    return JSONResponse(
        content={
            "running": bool(_YOUTUBE_RUN["running"] and _YOUTUBE_RUN["thread"] and _YOUTUBE_RUN["thread"].is_alive()),
            "started_at": _YOUTUBE_RUN["started_at"],
            "last_error": _YOUTUBE_RUN["last_error"],
            "result": _YOUTUBE_RUN["result"],
        }
    )


@app.post("/api/youtube/metadata")
def youtube_metadata(
    plan: str = Form(...),
    song_index: int = Form(0),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Preview YouTube metadata generated from a song plan (no network)."""
    from ai_influencer_studio.youtube_publish import build_metadata

    plan_path = Path(plan)
    if not plan_path.exists():
        return JSONResponse(status_code=400, content={"error": f"Plan file not found: {plan_path}"})
    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
        songs = data.get("songs", [])
        if song_index < 0 or song_index >= len(songs):
            return JSONResponse(status_code=400, content={"error": f"Invalid song index: {song_index}"})
        return JSONResponse(content=build_metadata(songs[song_index]))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})


@app.post("/api/youtube/upload/start")
def youtube_upload_start(
    plan: str = Form(...),
    song_index: int = Form(0),
    video: str = Form(""),
    thumbnail: str = Form(""),
    privacy: str = Form(""),
    create_playlist: str = Form(""),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Start publishing one song plan in a background thread."""
    from ai_influencer_studio.youtube_publish import YouTubePublisher, save_publish_record

    if _YOUTUBE_RUN["running"] and _YOUTUBE_RUN["thread"] and _YOUTUBE_RUN["thread"].is_alive():
        return JSONResponse(status_code=409, content={"error": "A publish is already running"})

    config = _config()
    plan_path = Path(plan)
    if not plan_path.exists():
        return JSONResponse(status_code=400, content={"error": f"Plan file not found: {plan_path}"})
    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
        songs = data.get("songs", [])
        if song_index < 0 or song_index >= len(songs):
            return JSONResponse(status_code=400, content={"error": f"Invalid song index: {song_index}"})
        song = songs[song_index]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    video_path = Path(video) if video else plan_path.with_suffix(".mp4")
    if not video_path.exists():
        return JSONResponse(status_code=400, content={"error": f"Video file not found: {video_path}"})

    publisher = YouTubePublisher(
        token_path=config.youtube_token_path,
        client_secrets_path=config.youtube_client_secrets_path,
    )
    _YOUTUBE_RUN.update(running=True, started_at=datetime.now(UTC).isoformat(), last_error=None, result=None)

    def _worker() -> None:
        try:
            result = publisher.publish_song(
                song,
                video_path,
                thumbnail_path=thumbnail or None,
                privacy=privacy or config.youtube_default_privacy,
                category_id=config.youtube_category_id,
                create_playlist_title=create_playlist or config.youtube_playlist_title or None,
            )
            save_publish_record(result, config.data_dir / "youtube_publish.jsonl")
            _YOUTUBE_RUN["result"] = result
        except Exception as exc:
            _YOUTUBE_RUN["last_error"] = str(exc)
        finally:
            _YOUTUBE_RUN["running"] = False

    thread = threading.Thread(target=_worker, name="youtube-publish", daemon=True)
    _YOUTUBE_RUN["thread"] = thread
    thread.start()
    return JSONResponse(
        status_code=202,
        content={"started": True, "message": "Publish started in background; poll /api/youtube/status"},
    )


@app.get("/pipeline", response_class=HTMLResponse)
def pipeline_dashboard(request: Request, _api_key: str = AuthDep) -> HTMLResponse:
    """One view of the whole production loop: plans -> execute -> upload -> publish."""
    return templates.TemplateResponse(request, "pipeline.html", {})


@app.get("/api/pipeline/status")
def pipeline_status(_api_key: str = AuthDep) -> JSONResponse:
    """Aggregate plan, Drive-upload, and YouTube-publish state for the pipeline page."""
    config = _config()
    plans: list[dict[str, Any]] = []
    plan_paths: set[Path] = set()
    for pattern in ("*_music_video_plan.json", "master_music_video_plan.json"):
        plan_paths.update(config.data_dir.glob(pattern))
    for path in sorted(plan_paths):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        plans.append({
            "name": path.name,
            "path": str(path),
            "songs": len(data.get("songs", [])),
            "continuity_warnings": data.get("continuity_warnings", []),
            "created": data.get("created", ""),
        })

    gdrive: dict[str, Any] = {}
    try:
        uploader = _gdrive_uploader()
        gdrive = uploader.status()
        gdrive["running"] = bool(_GDRIVE_RUN["running"] and _GDRIVE_RUN["thread"] and _GDRIVE_RUN["thread"].is_alive())
        gdrive["progress"] = _GDRIVE_RUN["progress"]
    except Exception as exc:
        gdrive = {"error": str(exc)}

    youtube_records: list[dict[str, Any]] = []
    log_path = config.data_dir / "youtube_publish.jsonl"
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").strip().splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            metadata = record.get("metadata") or {}
            youtube_records.append({
                "title": record.get("title") or metadata.get("title"),
                "video_id": record.get("video_id"),
                "url": record.get("url"),
                "uploaded_at": record.get("uploaded_at"),
            })

    return JSONResponse(
        content={
            "plans": plans,
            "gdrive": gdrive,
            "youtube": {
                "running": bool(_YOUTUBE_RUN["running"] and _YOUTUBE_RUN["thread"] and _YOUTUBE_RUN["thread"].is_alive()),
                "last_error": _YOUTUBE_RUN["last_error"],
                "records": youtube_records[-5:][::-1],
            },
        }
    )


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, _api_key: str = AuthDep) -> HTMLResponse:
    """Main dashboard with metrics and upcoming posts."""
    config = _config()
    adapter = AutomationAdapter(config)
    posts = adapter.list_scheduled_posts()
    pending = [p for p in posts if p.status == "pending"]
    posted = [p for p in posts if p.status == "posted"]

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "pending_count": len(pending),
            "posted_count": len(posted),
            "upcoming": pending[:5],
        },
    )


@app.get("/factory", response_class=HTMLResponse)
def factory(request: Request, _api_key: str = AuthDep) -> HTMLResponse:
    """Content creation lab."""
    return templates.TemplateResponse(request, "factory.html", {})


@app.post("/factory/generate")
def factory_generate(
    content_type: str = Form(...),
    topic: str = Form(...),
    platform: str = Form("instagram"),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Generate content from the factory page."""
    config = _config()
    try:
        if content_type in {"post", "caption", "blog", "video_script"}:
            adapter = ContentAdapter(config)
            if content_type == "post":
                result = adapter.generate_post(topic, platform)
            elif content_type == "caption":
                result = adapter.generate_caption(topic, platform)
            elif content_type == "blog":
                result = adapter.generate_blog(topic)
            else:
                result = adapter.generate_video_script(topic)
            return {"type": content_type, "result": result}

        if content_type == "talking_head":
            adapter = VideoAdapter(config)
            result = adapter.generate_talking_head_short(topic)
            return {"type": content_type, "result": result}

        if content_type == "social_video":
            adapter = VideoAdapter(config)
            result = adapter.generate_social_video(topic, platform)
            return {"type": content_type, "result": result}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})

    raise HTTPException(status_code=400, detail=f"Unknown content type: {content_type}")


@app.get("/calendar", response_class=HTMLResponse)
def calendar_view(request: Request, _api_key: str = AuthDep) -> HTMLResponse:
    """Visual calendar of scheduled posts."""
    config = _config()
    adapter = AutomationAdapter(config)
    posts = adapter.list_scheduled_posts()
    return templates.TemplateResponse(
        request,
        "calendar.html",
        {
            "posts": posts,
        },
    )


@app.post("/calendar/schedule")
def calendar_schedule(
    platform: str = Form(...),
    content: str = Form(...),
    scheduled_at: str = Form(...),
    hashtags: str = Form(""),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Schedule a new post from the calendar page."""
    config = _config()
    adapter = AutomationAdapter(config)
    try:
        scheduled_dt = datetime.fromisoformat(scheduled_at)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": f"Invalid datetime: {exc}"})

    hashtag_list = [h.strip() for h in hashtags.split(",") if h.strip()]
    try:
        post_id = adapter.schedule_post(
            platform=platform,
            content=content,
            scheduled_at=scheduled_dt,
            hashtags=hashtag_list,
        )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})

    return JSONResponse(status_code=200, content={"id": post_id, "scheduled_at": scheduled_dt.isoformat()})


@app.post("/publish/now")
def publish_now(
    platform: str = Form(...),
    content: str = Form(...),
    media_path: str = Form(""),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Publish a post immediately via API."""
    config = _config()
    adapter = AutomationAdapter(config)
    try:
        result = adapter.post_via_api(
            platform=platform,
            content=content,
            media_path=media_path or None,
        )
        return result
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/music-video", response_class=HTMLResponse)
def music_video_lab(request: Request, _api_key: str = AuthDep) -> HTMLResponse:
    """Music video research and planning lab."""
    return templates.TemplateResponse(request, "music_video.html", {})


@app.post("/api/music-video/research")
def music_video_research(
    vram: int = Form(8),
    max_results: int = Form(10),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Research free video generators and YouTube trends."""
    config = _config()
    engine = MusicVideoResearchEngine(
        data_dir=config.data_dir,
        youtube_api_key=config.youtube_api_key or None,
    )
    generators = engine.research_generators(vram_gb=vram)
    trends = engine.fetch_youtube_trends(max_results=max_results)
    return JSONResponse(content={"generators": generators, "trends": trends})


@app.post("/api/music-video/plan")
def music_video_plan(
    song_name: str = Form(...),
    audio_path: str = Form(...),
    genre: str = Form(""),
    mood: str = Form(""),
    duration: float = Form(180.0),
    character_ref: str = Form(""),
    generation_mode: str = Form("full"),
    style_bible_path: str = Form(""),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Create and save a master music video plan for one song."""
    config = _config()
    engine = MusicVideoResearchEngine(data_dir=config.data_dir)
    plan_kwargs: dict[str, Any] = {
        "song_name": song_name,
        "audio_path": audio_path,
        "genre": genre,
        "mood": mood,
        "duration": duration,
        "character_ref": character_ref or None,
        "generation_mode": generation_mode,
    }
    if style_bible_path.strip():
        plan_kwargs["style_bible_path"] = style_bible_path.strip()
    engine.create_song_plan(**plan_kwargs)
    plan = engine.create_master_plan()
    path = engine.save_master_plan_with_name(song_name)
    return JSONResponse(content={"plan": plan, "path": str(path)})


@app.get("/api/music-video/plans")
def music_video_plans(_api_key: str = AuthDep) -> JSONResponse:
    """List saved master plans in the data directory."""
    config = _config()
    plans: list[dict[str, Any]] = []
    for f in sorted(config.data_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if "songs" in data:
                plans.append({
                    "name": f.name,
                    "path": str(f),
                    "songs": len(data.get("songs", [])),
                    "created": data.get("created"),
                })
        except Exception:
            continue
    return JSONResponse(content={"plans": plans})


@app.post("/api/music-video/analyze-audio")
def music_video_analyze_audio(
    audio_path: str = Form(...),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Analyze an audio file and return duration and BPM."""
    try:
        result = analyze_audio(audio_path)
        return JSONResponse(content=result)
    except FileNotFoundError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except (ValueError, RuntimeError) as exc:
        return JSONResponse(status_code=400, content={"error": f"Could not decode audio: {exc}"})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.delete("/api/music-video/plans/{plan_name}")
def music_video_delete_plan(
    plan_name: str,
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Delete a saved master plan from the data directory."""
    config = _config()
    plan_name = Path(plan_name).name
    plan_path = config.data_dir / plan_name
    if not plan_path.exists() or not plan_path.is_file():
        return JSONResponse(status_code=404, content={"error": f"Plan not found: {plan_name}"})
    try:
        plan_path.unlink()
        return JSONResponse(content={"deleted": plan_name})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/api/music-video/plans/{plan_name}/rename")
def music_video_rename_plan(
    plan_name: str,
    new_name: str = Form(...),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Rename a saved master plan."""
    config = _config()
    plan_name = Path(plan_name).name
    plan_path = config.data_dir / plan_name
    new_path = config.data_dir / Path(new_name).name
    if not new_name.strip() or not new_path.name.endswith(".json"):
        return JSONResponse(status_code=400, content={"error": "new_name must be a non-empty .json filename"})
    if not plan_path.exists() or not plan_path.is_file():
        return JSONResponse(status_code=404, content={"error": f"Plan not found: {plan_name}"})
    if new_path.exists():
        return JSONResponse(status_code=409, content={"error": f"Destination already exists: {new_name}"})
    try:
        plan_path.rename(new_path)
        return JSONResponse(content={"renamed": {"from": plan_name, "to": new_path.name}})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/api/music-video/execute")
def music_video_execute(
    plan: str = Form(...),
    song_index: int = Form(0),
    generation_mode: str = Form(""),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Execute a saved song plan through the ComfyUI orchestrator.

    ``plan`` can be either a filename inside the configured data directory
    or a full filesystem path.
    """
    config = _config()
    adapter = VideoAdapter(config)
    try:
        plan_path = config.data_dir / plan
        if not plan_path.exists():
            # Allow full paths for backward compatibility / CLI use.
            plan_path = Path(plan)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        songs = plan.get("songs", [])
        if not isinstance(songs, list) or not songs:
            return JSONResponse(status_code=400, content={"error": "Plan must contain a non-empty 'songs' list"})
        if song_index < 0 or song_index >= len(songs):
            return JSONResponse(status_code=400, content={"error": "Invalid song index"})
        song = songs[song_index]
        if not isinstance(song, dict):
            return JSONResponse(status_code=400, content={"error": "Song plan must be a dictionary"})
        if generation_mode:
            song["generation_mode"] = generation_mode
        audio_path = song.get("audio_path")
        if not isinstance(audio_path, str) or not audio_path.strip():
            return JSONResponse(status_code=400, content={"error": "Song plan must include a non-empty 'audio_path'"})
        if not Path(audio_path).exists():
            return JSONResponse(status_code=404, content={"error": f"Audio file not found: {audio_path}"})
        result = adapter.execute_music_video_plan(song)
        return JSONResponse(content=result)
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"error": f"Plan file not found: {plan}"})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.websocket("/ws/music-video/execute")
async def music_video_execute_ws(websocket: WebSocket) -> None:
    """Execute a saved song plan through the ComfyUI orchestrator with streaming progress."""
    _verify_ws_api_key(websocket)
    await websocket.accept()
    config = _config()
    adapter = VideoAdapter(config)

    try:
        try:
            message = await websocket.receive_json()
        except json.JSONDecodeError as exc:
            await websocket.send_json({"type": "error", "message": f"Invalid JSON: {exc}"})
            return
        plan_name = message.get("plan")
        song_index = int(message.get("song_index", 0))
        generation_mode = message.get("generation_mode", "")
        if generation_mode not in ("", "full", "clip_only", "assembly_only"):
            await websocket.send_json({"type": "error", "message": "Invalid generation_mode"})
            return
        if not isinstance(plan_name, str) or not plan_name.strip():
            await websocket.send_json({"type": "error", "message": "Missing or empty 'plan'"})
            return

        plan_name = Path(plan_name).name
        plan_path = config.data_dir / plan_name
        if not plan_path.exists():
            await websocket.send_json({"type": "error", "message": f"Plan file not found: {plan_name}"})
            return

        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        songs = plan_data.get("songs", [])
        if not isinstance(songs, list) or not songs:
            await websocket.send_json({"type": "error", "message": "Plan must contain a non-empty 'songs' list"})
            return
        if song_index < 0 or song_index >= len(songs):
            await websocket.send_json({"type": "error", "message": "Invalid song index"})
            return

        song = songs[song_index]
        if not isinstance(song, dict):
            await websocket.send_json({"type": "error", "message": "Song plan must be a dictionary"})
            return
        if generation_mode:
            song["generation_mode"] = generation_mode
        audio_path = song.get("audio_path")
        if not isinstance(audio_path, str) or not audio_path.strip():
            await websocket.send_json({"type": "error", "message": "Song plan must include a non-empty 'audio_path'"})
            return
        if not Path(audio_path).exists():
            await websocket.send_json({"type": "error", "message": f"Audio file not found: {audio_path}"})
            return

        await websocket.send_json({"type": "status", "message": "started"})
        async for message in adapter.execute_music_video_plan_streaming(song):
            await websocket.send_json(message)
    except WebSocketDisconnect:
        return
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass


@app.post("/api/video/repurpose")
def video_repurpose(
    input_path: str = Form(...),
    platform: str = Form("tiktok"),
    start: float = Form(0.0),
    duration: float = Form(0.0),
    caption: str = Form(""),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Create a vertical repurposed clip from an existing video."""
    try:
        repurposer = VideoRepurposer()
        output_dir = _config().media_dir / "repurposed"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{Path(input_path).stem}_{platform}.mp4"
        kwargs: dict[str, Any] = {"platform": platform, "start": start, "caption": caption or None}
        if duration > 0:
            kwargs["duration"] = duration
        result = repurposer.create_vertical_cut(input_path, output_path, **kwargs)
        return JSONResponse(content=result)
    except FileNotFoundError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except RuntimeError as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/api/scheduler/{scheduler}/push")
def scheduler_push(
    scheduler: str,
    payload: dict[str, Any] | None = None,
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Push a payload to an external scheduler (n8n, postiz, mixpost)."""
    payload = payload or {}
    try:
        config = _config()
        adapter = AutomationAdapter(config)
        result = adapter.push_to_scheduler(scheduler, payload)
        return JSONResponse(content=result)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        logger.exception("Scheduler push to %s failed", scheduler)
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/api/video/repurpose/multi")
def video_repurpose_multi(
    input_path: str = Form(...),
    platforms: str = Form("tiktok"),
    clip_duration: float = Form(15.0),
    _api_key: str = AuthDep,
) -> JSONResponse:
    """Generate repurposed clips for multiple platforms."""
    try:
        repurposer = VideoRepurposer()
        output_dir = _config().media_dir / "repurposed"
        platform_list = [p.strip() for p in platforms.split(",") if p.strip()]
        result = repurposer.create_multi_clips(
            input_path,
            output_dir,
            platforms=platform_list,
            clip_duration=clip_duration,
        )
        return JSONResponse(content={"clips": result})
    except FileNotFoundError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except RuntimeError as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/api/agent/run")
def agent_run(payload: dict[str, Any] | None = None, _api_key: str = AuthDep) -> JSONResponse:
    """Run an autonomous multi-model browser/computer task.

    Body keys: ``task`` (required), ``target`` (browser|windows), ``url``, ``app``,
    ``models`` (provider::model refs), ``domains``, ``apps``, ``headed``,
    ``allow_sensitive_fields``, ``max_steps``. When ``models`` is omitted, up to
    four free vision models are auto-selected from the registry snapshot.
    """
    from ai_influencer_studio.model_registry import ModelRegistry
    from ai_influencer_studio.safe_use.agent import MultiModelAgent, pick_free_vision_models
    from ai_influencer_studio.safe_use.browser import PlaywrightBrowser
    from ai_influencer_studio.safe_use.engine import SafeUseEngine
    from ai_influencer_studio.safe_use.multi_model import MultiModelClient
    from ai_influencer_studio.safe_use.policy import SafePolicy

    payload = payload or {}
    task = payload.get("task")
    if not isinstance(task, str) or not task.strip():
        return JSONResponse(status_code=400, content={"error": "task is required"})
    target = str(payload.get("target", "browser"))
    if target not in ("browser", "windows"):
        return JSONResponse(status_code=400, content={"error": "target must be 'browser' or 'windows'"})

    config = _config()
    models = [str(item) for item in payload.get("models", []) if isinstance(item, str)]
    if not models:
        try:
            snapshot = ModelRegistry.load_snapshot(config.data_dir / "model_registry.json")
            models = pick_free_vision_models(snapshot, limit=4)
        except Exception:
            models = []
        if not models:
            return JSONResponse(status_code=400, content={"error": "no models supplied and no free vision models in registry"})

    policy = SafePolicy(
        allowed_domains={str(item) for item in payload.get("domains", []) if isinstance(item, str)},
        allowed_apps={str(item) for item in payload.get("apps", []) if isinstance(item, str)},
        allow_sensitive_fields=bool(payload.get("allow_sensitive_fields", False)),
    )
    browser = None
    if target == "browser":
        browser = PlaywrightBrowser(headless=not bool(payload.get("headed", False)), screenshot_dir=config.data_dir / "safe-use-screenshots")
    engine = SafeUseEngine(policy=policy, audit_path=config.data_dir / "safe-use-audit.jsonl", browser=browser)

    client = MultiModelClient(openrouter_api_key=config.openrouter_api_key or None)
    aggregator = payload.get("aggregator")
    agent = MultiModelAgent(
        engine,
        models=models,
        client=client,
        max_steps=int(payload.get("max_steps", 12)),
        aggregator=str(aggregator) if isinstance(aggregator, str) and aggregator.strip() else None,
    )
    try:
        result = agent.run_task(task, target=target, url=payload.get("url"), app=payload.get("app"))
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    finally:
        engine.close()
    return JSONResponse(content=result)
