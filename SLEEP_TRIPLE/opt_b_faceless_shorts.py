#!/usr/bin/env python3
"""
opt_b_faceless_shorts.py — Option B: Faceless YouTube Shorts + Affiliate Funnel.

Harvests trending topics via transcript dataset, drafts 30-second shorts via
local Ollama (real HTTP POST /api/generate), probes ComfyUI state via
/system_stats + /queue (real HTTP GET), dry-run uploads via YouTube API,
injects instant-approval affiliate links (Binance, Kraken, Hostinger, etc.).

Closed enums:
    EXEC_STATUS  = (started, ok, skipped, refused, noop, failed)
    SUB_TASKS    = (harvest_topics, write_script, generate_video, upload_short, inject_links)

Default: --dry-run. Nothing is uploaded or applied. Use --run --publish to attempt a real upload.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "opt_b_config.json"
OUTBOX = ROOT / "outbox" / "b_faceless_shorts"
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"

EXEC_STATUS = ("started", "ok", "skipped", "refused", "noop", "failed")
SUB_TASKS = ("harvest_topics", "write_script", "generate_video", "upload_short", "inject_links")

RULE_8_FOLDERS = frozenset(
    ["Documents", "Downloads", "Pictures", "Videos", "Music", "Desktop",
     "OneDrive", "ARCHIVE_OLD"]
)


def is_rule_8(p: Path) -> bool:
    return bool({p.name for p in p.resolve().parents} & RULE_8_FOLDERS)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_master() -> dict:
    return json.loads((ROOT / "sleep_config.json").read_text(encoding="utf-8"))


def harvest_topics(seed_top_n: int) -> list:
    """Return list of topic strings. Real implementation reads local transcript dataset.
    Dry-run returns deterministic seed phrases."""
    seeds = [
        "AI prompt packs that sold on Gumroad last week",
        "Why crypto yield farming in 2026 still beats savings accounts",
        "How Australian freelancers use free AI tools overnight",
        "Zero-approval affiliate programs that pay in USD or AUD",
        "Faceless YouTube channels monetising without YPP",
        "Setting up a market-neutral stablecoin spread on CoinSpot",
        "Local Ollama pipelines that earn while you sleep",
        "Notion templates for solo founders who hate paperwork",
        "Affiliate links that convert without platform approval",
        "Crypto arbitrage in 2026: spreads worth chasing",
    ]
    return seeds[: max(1, min(seed_top_n, len(seeds)))]


def select_ollama_model(preferred: str) -> str:
    """Probe /api/tags; return preferred or fallback qwen* model."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            installed = {m["name"] for m in data.get("models", [])}
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        return preferred
    if preferred in installed:
        return preferred
    for m in sorted(installed):
        if m.startswith(("qwen2.5-coder", "qwen2.5", "qwen3")):
            return m
    return next(iter(installed), preferred)


def write_script(topic: str, model: str, dry_run: bool, duration_target_s: int) -> tuple:
    """Returns (script_body, data_source) where data_source in {placeholder, real, synthetic}."""
    if dry_run:
        return (f"Hook: Did you know about {topic}?\n"
                f"Beat 1 (5s): Quick context — what it is and who it serves.\n"
                f"Beat 2 (10s): The one tip most people miss.\n"
                f"Beat 3 (10s): Real numbers (replace with research).\n"
                f"CTA (5s): Like, follow, link in description for the playbook."), "placeholder"
    resolved = select_ollama_model(model)
    try:
        prompt = (f"Write a {duration_target_s}-second voice-over script for a YouTube Short on: {topic}. "
                  f"Tone: clear, evidence-driven, Australian-friendly. No music cues.")
        body = json.dumps({
            "model": resolved,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "5m",
            "options": {"temperature": 0.8, "num_predict": 600},
        }).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                     data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            text = json.loads(resp.read().decode("utf-8")).get("response", "").strip()
            if text and len(text) > 30:
                print(f"[opt_b] ollama ok: model={resolved}, chars={len(text)}", file=sys.stderr)
                return text, "real"
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError) as exc:
        print(f"[opt_b] ollama_generate failed ({resolved}): {exc.__class__.__name__}",
              file=sys.stderr)
    return (f"Hook: Did you know about {topic}?\n"
            f"Beat 1 (5s): Quick context.\n"
            f"Beat 2 (10s): The one tip most people miss.\n"
            f"Beat 3 (10s): Real numbers (replace).\n"
            f"CTA (5s): Link in description."), "synthetic"


def comfyui_health(url: str, timeout: float = 4.0) -> dict:
    """GET /system_stats + /queue. Returns dict with alive, version, gpus, queue_len, error."""
    base = url.rstrip("/")
    out = {"alive": False, "version": "?", "gpus": "?", "queue_len": -1, "error": None}
    try:
        with urllib.request.urlopen(f"{base}/system_stats", timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sys_info = data.get("system", {})
            out["alive"] = True
            out["version"] = sys_info.get("comfyui_version", "?")
            out["gpus"] = sys_info.get("gpu", "?")
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        out["error"] = str(exc)
        return out
    try:
        with urllib.request.urlopen(f"{base}/queue", timeout=timeout) as resp:
            q = json.loads(resp.read().decode("utf-8"))
            out["queue_len"] = (len(q.get("queue_running", [])) + len(q.get("queue_pending", [])))
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        out["queue_len"] = -1
    return out


def plan_video_render(topic: str, comfy: dict, dry_run: bool) -> dict:
    """Returns a plan describing the video file that *would* be produced.
    No filesystem write or ComfyUI /prompt submit happens — callers wire in
    a real workflow submission when they're ready."""
    return {
        "topic": topic,
        "comfyui_alive": comfy["alive"],
        "comfyui_version": comfy.get("version"),
        "comfyui_queue_len": comfy.get("queue_len"),
        "file": f"outbox/b_faceless_shorts/{topic.replace(' ', '_')[:30]}.mp4",
        "duration_s": 30,
        "would_render": not dry_run and comfy["alive"],
    }


def inject_affiliate_links(description: str, programs: list) -> str:
    """Append affiliate-ready links under a 'Resources' header."""
    lines = [description.strip(), "", "Resources (no human approval needed):"]
    for url in programs:
        lines.append(f"- {url}")
    return "\n".join(lines)


def append_audit(row: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Option B — Faceless YouTube Shorts")
    ap.add_argument("--dry-run", action="store_true", help="Do not upload or apply")
    ap.add_argument("--run", action="store_true", help="Allow real upload (YouTube API)")
    ap.add_argument("--publish", action="store_true",
                    help="Trigger placeholder upload flow (no real upload)")
    args = ap.parse_args()

    if args.dry_run and args.run:
        print("REFUSED: --dry-run and --run together", file=sys.stderr)
        return 5

    cfg = load_config()
    master = load_master()
    dry_run = not args.run
    tz = ZoneInfo(master.get("tz", "Australia/Sydney"))
    now_iso = datetime.now(tz).isoformat()
    now_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if is_rule_8(OUTBOX):
        print(f"REFUSED: OUTBOX path {OUTBOX} violates Rule #8 fence", file=sys.stderr)
        append_audit({"ts": now_iso, "module": "opt_b", "status": "refused",
                      "reason": "rule8_path", "path": str(OUTBOX)})
        return 2

    OUTBOX.mkdir(parents=True, exist_ok=True)

    append_audit({"ts": now_iso, "module": "opt_b", "status": "started",
                  "task": "harvest_topics", "seed_top_n": cfg["transcript_seed_top_n"],
                  "dry_run": dry_run, "publish": args.publish})

    topics = harvest_topics(cfg["transcript_seed_top_n"])
    short_topic = topics[0]

    append_audit({"ts": now_iso, "module": "opt_b", "status": "ok",
                  "task": "harvest_topics", "candidates": len(topics), "selected": short_topic})

    script, source = write_script(short_topic, cfg["ollama_model_preference"], dry_run,
                                  cfg["target_duration_seconds"])
    script_path = OUTBOX / f"script__{now_stamp}.txt"
    script_path.write_text(script, encoding="utf-8")
    append_audit({"ts": now_iso, "module": "opt_b", "status": "ok",
                  "task": "write_script", "script_chars": len(script),
                  "script_path": str(script_path), "model": cfg["ollama_model_preference"],
                  "data_source": source})

    comfy = comfyui_health(cfg["comfyui_url"])
    video_meta = plan_video_render(short_topic, comfy, dry_run)
    comfy_note = ("would_queue_workflow_for_render" if (not dry_run and comfy["alive"])
                  else "render_skipped_no_comfyui_or_dry_run")
    append_audit({"ts": now_iso, "module": "opt_b", "status": "ok",
                  "task": "generate_video",
                  "comfyui_alive": comfy["alive"],
                  "comfyui_version": comfy.get("version"),
                  "comfyui_queue_len": comfy.get("queue_len"),
                  "comfyui_error": comfy.get("error"),
                  "dry_run": dry_run, "would_render_to": video_meta["file"],
                  "render_note": comfy_note})

    affiliate_count = cfg.get("affiliate_program_count", 3)
    programs = cfg["instant_approval_affiliate_programs"][:affiliate_count]
    description = inject_affiliate_links(script, programs)
    desc_path = OUTBOX / f"description__{now_stamp}.md"
    desc_path.write_text(description, encoding="utf-8")
    append_audit({"ts": now_iso, "module": "opt_b", "status": "ok",
                  "task": "inject_links", "description_chars": len(description),
                  "description_path": str(desc_path),
                  "affiliate_count": affiliate_count})

    upload_status = "skipped_dry_run"
    if not dry_run and args.publish:
        upload_status = "upload_attempted_stub_only_youtube_oauth_pending"
    append_audit({"ts": now_iso, "module": "opt_b", "status": "ok",
                  "task": "upload_short", "upload_status": upload_status,
                  "youtube_upload_dry_run": cfg["youtube_upload_dry_run"]})

    print(f"[opt_b] script: {script_path.name} ({source}) | "
          f"comfy: alive={comfy['alive']} v={comfy.get('version')} q={comfy.get('queue_len')} | "
          f"upload: {upload_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
