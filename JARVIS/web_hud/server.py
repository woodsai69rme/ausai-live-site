#!/usr/bin/env python3
"""
JARVIS Web HUD Server — Real-Time Control Center & REST API (v2.2.0 Complete Empire Edition).
Runs on Port 6970 with an Iron-Man Holographic Glass UI.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

from jarvis_arrow import show_ai_arrow_by_query, show_ai_arrow
from jarvis_brain import JarvisBrain
from jarvis_browser import JarvisBrowserBridge
from jarvis_bumblebee import BumblebeeVoiceEngine
from jarvis_employees import SPARKEmployee, TARSEmployee
from jarvis_fast_rag import JarvisFastRAG
from jarvis_gateway import EmpireGateway
from jarvis_invoice import JarvisInvoiceEngine
from jarvis_kokoro import get_neural_voice
from jarvis_memory import get_memory
from jarvis_mission_master import JarvisMasterMissionOrchestrator
from jarvis_phone import JarvisPhoneAssistant
from jarvis_scheduler import JarvisAutonomousScheduler
from jarvis_som import get_som
from jarvis_takeover import JarvisAutonomousTakeover
from jarvis_storyboard_visualizer import render_storyboard_preview
from jarvis_telegram import JarvisTelegramBridge
from jarvis_video_pipeline import JarvisVideoPipeline
from jarvis_vision import get_vision
from jarvis_voice import get_voice

app = FastAPI(title="JARVIS Holographic HUD Server", version="2.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = JARVIS_DIR / "web_hud" / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
INVOICE_DIR = JARVIS_DIR / "invoices"
CONTENT_DIR = JARVIS_DIR / "content_vault"
CONTENT_DIR.mkdir(parents=True, exist_ok=True)
OFFERINGS_DIR = JARVIS_DIR / "agency_offerings"
OFFERINGS_DIR.mkdir(parents=True, exist_ok=True)
NICHE_DIR = OFFERINGS_DIR / "niche_campaigns"
NICHE_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_MANIFEST_DIR = CONTENT_DIR / "video_manifests"
VIDEO_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR = JARVIS_DIR / "screenshots"


class ArrowRequest(BaseModel):
    query: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    label: Optional[str] = "TARGET"
    mode: Optional[str] = "guide"


class TakeoverRequest(BaseModel):
    task: str


class InvoiceRequest(BaseModel):
    prompt: str


class ProposalRequest(BaseModel):
    client_name: str
    service_scope: str


class ContentExplosionRequest(BaseModel):
    topic: str


class MemoryAddRequest(BaseModel):
    content: str
    category: str = "general"


class SpeakRequest(BaseModel):
    text: str


class PhoneSimRequest(BaseModel):
    caller: str = "Bruce Wayne"
    phone: str = "+1 (555) 019-2834"
    inquiry: str = "Requesting autonomous AI copilot consulting"


class SchedulerTriggerRequest(BaseModel):
    loop: str = "morning"  # morning, midday, evening, all


class MasterMissionRequest(BaseModel):
    client: str = "OmniCorp Global"
    scope: str = "Autonomous AI Copilot Deployment"
    invoice: str = "$6,500"
    topic: str = "Autonomous AI Copilots on Windows 11"


class VideoManifestRequest(BaseModel):
    topic: str = "How AI Employees Run Autonomous Workstations in 2026"


class BumblebeeRequest(BaseModel):
    category: str = "greeting"
    topic: Optional[str] = ""
    text: Optional[str] = ""


@app.get("/", response_class=HTMLResponse)
def get_hud_dashboard():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>JARVIS HUD Online</h1>")


@app.get("/warroom", response_class=HTMLResponse)
def get_warroom_dashboard():
    warroom_file = STATIC_DIR / "warroom.html"
    if warroom_file.exists():
        return HTMLResponse(content=warroom_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>JARVIS War Room Online</h1>")


@app.get("/api/status")
def get_system_status():
    vis = get_vision()
    browser = JarvisBrowserBridge()
    mem = get_memory()
    state_file = SCREENSHOT_DIR / "jarvis_takeover_state.json"
    takeover_state = {}
    if state_file.exists():
        try:
            takeover_state = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "status": "ONLINE",
        "system": "JARVIS Autonomous Copilot v2.2.0",
        "screen_resolution": f"{vis.screen_w}x{vis.screen_h}",
        "chrome_cdp_active": browser.is_chrome_cdp_active(),
        "user_profile": mem.get_profile(),
        "takeover_state": takeover_state,
        "timestamp": time.time(),
    }


@app.get("/api/screenshot")
def get_current_screenshot():
    vis = get_vision()
    shot_path, _ = vis.capture_screen("hud_live.png")
    return FileResponse(str(shot_path), media_type="image/png")


@app.get("/api/som")
def get_som_screenshot():
    som = get_som()
    raw_path, _ = som.vision.capture_screen("hud_som_raw.png")
    som_path, _, _ = som.generate_som_overlay(raw_path, SCREENSHOT_DIR / "hud_som_tagged.png")
    return FileResponse(str(som_path), media_type="image/png")


@app.post("/api/arrow")
def trigger_ai_arrow(req: ArrowRequest):
    if req.query:
        threading.Thread(target=show_ai_arrow_by_query, args=(req.query, req.mode), daemon=True).start()
        return {"status": "SUCCESS", "message": f"Locating '{req.query}'"}
    elif req.x is not None and req.y is not None:
        threading.Thread(target=show_ai_arrow, args=(req.x, req.y, req.label, 5.0, req.mode, False), daemon=True).start()
        return {"status": "SUCCESS", "message": f"Targeting ({req.x}, {req.y})"}
    raise HTTPException(status_code=400, detail="Must provide either 'query' or ('x', 'y')")


@app.post("/api/takeover")
def trigger_takeover(req: TakeoverRequest):
    def _run():
        agent = JarvisAutonomousTakeover()
        agent.run_takeover(req.task)

    threading.Thread(target=_run, daemon=True).start()
    return {"status": "SUCCESS", "message": f"Initiated autonomous takeover for: {req.task}"}


@app.post("/api/invoice")
def trigger_invoice(req: InvoiceRequest):
    inv = JarvisInvoiceEngine()
    res = inv.process_voice_note_to_invoice(req.prompt)
    return {"status": "SUCCESS", "data": res}


@app.post("/api/tars/proposal")
def trigger_proposal(req: ProposalRequest):
    tars = TARSEmployee()
    res = tars.generate_proposal(req.client_name, req.service_scope)
    return {"status": "SUCCESS", "data": res}


@app.post("/api/spark/explode")
def trigger_content_explosion(req: ContentExplosionRequest):
    spark = SPARKEmployee()
    out_file = spark.explode_content(req.topic)
    return {"status": "SUCCESS", "file": str(out_file), "content": out_file.read_text(encoding="utf-8")}


@app.post("/api/scheduler/trigger")
def trigger_scheduler(req: SchedulerTriggerRequest):
    sched = JarvisAutonomousScheduler()
    if req.loop == "morning":
        res = sched.run_morning_brief()
    elif req.loop == "midday":
        res = sched.run_midday_content_explosion()
    elif req.loop == "evening":
        res = sched.run_evening_consolidation()
    else:
        sched.run_morning_brief()
        sched.run_midday_content_explosion()
        res = sched.run_evening_consolidation()
    return {"status": "SUCCESS", "loop": req.loop, "result": res}


@app.post("/api/master-mission/run")
def trigger_master_mission(req: MasterMissionRequest):
    orchestrator = JarvisMasterMissionOrchestrator()
    res = orchestrator.run_full_empire_mission(
        client_name=req.client,
        scope=req.scope,
        invoice_amount=req.invoice,
        content_topic=req.topic
    )
    return {"status": "SUCCESS", "mission_result": res}


@app.get("/api/gateway/status")
def get_gateway_status():
    gw = EmpireGateway()
    return {"status": "SUCCESS", "services": gw.audit_all_services()}


@app.get("/api/agency/packages")
def list_agency_packages():
    packages = []
    for p in OFFERINGS_DIR.glob("*.md"):
        packages.append({
            "name": p.name,
            "title": p.stem.replace("_", " "),
            "path": str(p),
            "size": p.stat().st_size,
            "content": p.read_text(encoding="utf-8")
        })
    return {"packages": sorted(packages, key=lambda x: x["name"])}


@app.get("/api/campaigns")
def list_campaigns():
    campaigns = []
    for p in NICHE_DIR.glob("*.md"):
        campaigns.append({
            "filename": p.name,
            "title": p.stem.replace("Campaign_", "").replace("_", " ").title(),
            "path": str(p),
            "size": p.stat().st_size
        })
    return {"campaigns": sorted(campaigns, key=lambda x: x["title"])}


@app.get("/api/campaigns/{filename}")
def get_campaign(filename: str):
    file_path = NICHE_DIR / filename
    if file_path.exists():
        return {"filename": filename, "content": file_path.read_text(encoding="utf-8")}
    raise HTTPException(status_code=404, detail="Campaign not found")


@app.get("/api/rag/search")
def search_fast_rag(q: str = ""):
    rag = JarvisFastRAG()
    hits = rag.search(q, limit=10)
    return {"query": q, "results": hits, "count": len(hits)}


@app.get("/api/video/manifests")
def list_video_manifests():
    manifests = []
    for p in VIDEO_MANIFEST_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            manifests.append({
                "filename": p.name,
                "title": data.get("title", p.stem),
                "total_duration": data.get("total_duration", "60s"),
                "scenes_count": len(data.get("scenes", [])),
                "generated_at": data.get("generated_at", ""),
                "data": data
            })
        except Exception:
            pass
    return {"manifests": sorted(manifests, key=lambda x: x.get("generated_at", ""), reverse=True)}


@app.post("/api/video/manifest")
def generate_video_manifest_endpoint(req: VideoManifestRequest):
    pipeline = JarvisVideoPipeline()
    out_file = pipeline.generate_video_manifest(req.topic)
    manifest_data = json.loads(out_file.read_text(encoding="utf-8"))
    try:
        render_storyboard_preview(out_file)
    except Exception:
        pass
    return {"status": "SUCCESS", "file": str(out_file), "manifest": manifest_data}


@app.get("/api/video/manifests/{filename}/preview")
def get_video_manifest_preview(filename: str):
    preview_file = VIDEO_MANIFEST_DIR / f"Preview_{Path(filename).stem}.png"
    if preview_file.exists():
        return FileResponse(str(preview_file), media_type="image/png")
    json_file = VIDEO_MANIFEST_DIR / filename
    if json_file.exists():
        p = render_storyboard_preview(json_file)
        return FileResponse(str(p), media_type="image/png")
    raise HTTPException(status_code=404, detail="Preview not found")


@app.get("/api/memory")
def get_memories(q: Optional[str] = None):
    mem = get_memory()
    if q:
        return {"memories": mem.search_memories(q)}
    with mem._get_conn() as conn:
        rows = conn.execute("SELECT * FROM memories ORDER BY id DESC LIMIT 20").fetchall()
        return {"memories": [dict(r) for r in rows]}


@app.post("/api/memory/add")
def add_memory_entry(req: MemoryAddRequest):
    mem = get_memory()
    mem.add_memory(req.content, category=req.category)
    return {"status": "SUCCESS", "added": req.content}


@app.post("/api/speak")
def trigger_speak(req: SpeakRequest):
    voice = get_voice()
    voice.speak(req.text)
    return {"status": "SUCCESS", "spoken": req.text}


@app.post("/api/bumblebee/speak")
def bumblebee_speak_endpoint(req: BumblebeeRequest):
    bb = BumblebeeVoiceEngine()
    snippet = bb.speak_as_bumblebee(category=req.category, custom_topic=req.topic or "")
    return {"status": "SUCCESS", "mode": "bumblebee", "snippet": snippet, "commander": "Mr. Wilson"}


@app.post("/api/bumblebee/translate")
def bumblebee_translate_endpoint(req: BumblebeeRequest):
    bb = BumblebeeVoiceEngine()
    out = bb.translate_to_bumblebee(req.text or "Standing by for orders, Mr. Wilson!")
    return {"status": "SUCCESS", "transmission": out}


@app.post("/api/bumblebee/secret")
def bumblebee_secret_phrase_endpoint(req: BumblebeeRequest):
    bb = BumblebeeVoiceEngine()
    res = bb.trigger_secret_phrase(custom_message=req.text or "")
    return {"status": "SUCCESS", "mode": "secret_phrase", "response": res, "commander": "Mr. Wilson"}


@app.get("/api/bumblebee/audio/{filename}")
def bumblebee_audio_stream_endpoint(filename: str):
    audio_path = JARVIS_DIR / "audio_cache" / filename
    if audio_path.exists():
        return FileResponse(str(audio_path), media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio track not found")


@app.post("/api/browser/launch")
def launch_chrome_cdp():
    browser = JarvisBrowserBridge()
    success = browser.launch_chrome_with_cdp()
    return {"status": "SUCCESS" if success else "FAILED", "active": success}


@app.post("/api/phone/simulate")
def simulate_phone_call(req: PhoneSimRequest):
    phone = JarvisPhoneAssistant()
    record = phone.handle_incoming_call_simulation(req.caller, req.phone, req.inquiry)
    return {"status": "SUCCESS", "record": record}


@app.get("/api/content/vault")
def list_content_vault():
    files = []
    for p in CONTENT_DIR.glob("*.md"):
        files.append({
            "name": p.name,
            "path": str(p),
            "size": p.stat().st_size,
            "created": p.stat().st_mtime,
        })
    return {"files": sorted(files, key=lambda x: x["created"], reverse=True)}


@app.get("/api/invoices")
def list_invoices():
    files = []
    for p in INVOICE_DIR.glob("*.pdf"):
        files.append({
            "name": p.name,
            "path": str(p),
            "size": p.stat().st_size,
            "created": p.stat().st_mtime,
        })
    return {"invoices": sorted(files, key=lambda x: x["created"], reverse=True)}


@app.get("/api/download/invoice/{filename}")
def download_invoice(filename: str):
    file_path = INVOICE_DIR / filename
    if file_path.exists():
        return FileResponse(str(file_path), filename=filename)
    raise HTTPException(status_code=404, detail="Invoice not found")


if __name__ == "__main__":
    print("[+] Launching JARVIS Complete Empire HUD Server on http://127.0.0.1:6970 ...")
    uvicorn.run(app, host="127.0.0.1", port=6970, log_level="warning")
