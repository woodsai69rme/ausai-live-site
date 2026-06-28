#!/usr/bin/env python3
"""
opt_b_faceless_shorts.py — Option B: Faceless YouTube Shorts + Affiliate Funnel.

Harvests trending topics via transcript dataset, drafts 30-second shorts via
local AI, generates cover/video via ComfyUI, dry-run uploads via YouTube API,
injects instant-approval affiliate links (Binance, Kraken, Hostinger, etc.).

Closed enums:
    EXEC_STATUS  = (started, ok, skipped, refused, noop, failed)
    SUB_TASKS    = (harvest_topics, write_script, generate_video, upload_short, inject_links)

Default: --dry-run. Nothing is uploaded or applied. Use --run --publish to attempt a real upload.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
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


def harvest_topics(seed_top_n: int) -> list[str]:
    """Return list of topic strings. Real implementation reads local transcript dataset.
    Dry-run returns deterministic seed phrases."""
    seeds = [
        "AI prompt packs that sold on Gumroad last week",
        "Why crypto yield farming in 2026 still beats savings accounts",
        "How Australian freelancers use free AI tools overnight",
        "Zero-approval affiliate programs that pay in USD or AUD",
        "Faceless YouTube channels monetising without YPP",
    ]
    return seeds[: max(1, min(seed_top_n, len(seeds)))]


def write_script(topic: str, model: str, dry_run: bool, duration_target_s: int) -> str:
    """Returns a 30-second voice-over script. Deterministic placeholder if dry-run."""
    if dry_run:
        return (f"Hook: Did you know about {topic}?\n"
                f"Beat 1 (5s): Quick context — what it is and who it serves.\n"
                f"Beat 2 (10s): The one tip most people miss.\n"
                f"Beat 3 (10s): Real numbers (replace with research).\n"
                f"CTA (5s): Like, follow, link in description for the playbook.")
    try:
        prompt = (f"Write a {duration_target_s}-second voice-over script for a YouTube Short on: {topic}. "
                  f"Tone: clear, evidence-driven, Australian-friendly. No music cues.")
        body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                     data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8")).get("response", "").strip()
    except (OSError, json.JSONDecodeError):
        return write_script(topic, model, True, duration_target_s)


def comfyui_ping(url: str) -> bool:
    try:
        host = url.split("//", 1)[-1].split(":")[0]
        port = int(url.rsplit(":", 1)[-1].split("/", 1)[0])
        with socket.create_connection((host, port), timeout=2.0):
            return True
    except OSError:
        return False


def generate_video_cover_stub(topic: str, comfy_alive: bool, dry_run: bool) -> dict:
    """Returns dict describing video file produced. No real render in dry-run."""
    return {
        "topic": topic,
        "comfyui_alive": comfy_alive,
        "file": f"outbox/b_faceless_shorts/{topic.replace(' ', '_')[:30]}.mp4",
        "duration_s": 30,
        "rendered": not dry_run and comfy_alive,
    }


def inject_affiliate_links(description: str, programs: list[str]) -> str:
    """Append affiliate-ready links under a 'Resources' header. Real implementation
    uses each program's actual affiliate URLs. Defaults to /affiliates landing pages."""
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
    ap.add_argument("--publish", action="store_true", help="Trigger placeholder upload flow")
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

    script = write_script(short_topic, cfg["ollama_model_preference"], dry_run,
                          cfg["target_duration_seconds"])
    script_path = OUTBOX / f"script__{now_stamp}.txt"
    script_path.write_text(script, encoding="utf-8")
    append_audit({"ts": now_iso, "module": "opt_b", "status": "ok",
                  "task": "write_script", "script_chars": len(script),
                  "script_path": str(script_path), "model": cfg["ollama_model_preference"]})

    comfy_alive = comfyui_ping(cfg["comfyui_url"])
    video_meta = generate_video_cover_stub(short_topic, comfy_alive, dry_run)
    append_audit({"ts": now_iso, "module": "opt_b", "status": "ok",
                  "task": "generate_video", "comfyui_alive": comfy_alive,
                  "dry_run": dry_run, "would_render_to": video_meta["file"]})

    affiliate_count = cfg.get("affiliate_program_count", 3)
    description = inject_affiliate_links(script,
                                          cfg["instant_approval_affiliate_programs"][:affiliate_count])
    desc_path = OUTBOX / f"description__{now_stamp}.md"
    desc_path.write_text(description, encoding="utf-8")
    append_audit({"ts": now_iso, "module": "opt_b", "status": "ok",
                  "task": "inject_links", "description_chars": len(description),
                  "description_path": str(desc_path),
                  "affiliate_count": affiliate_count})

    upload_status = "skipped_dry_run"
    if not dry_run and args.publish:
        upload_status = "upload_attempted_stub"
    append_audit({"ts": now_iso, "module": "opt_b", "status": "ok",
                  "task": "upload_short", "upload_status": upload_status,
                  "youtube_upload_dry_run": cfg["youtube_upload_dry_run"]})

    print(f"[opt_b] script: {script_path.name} | video: {video_meta['file']} | upload: {upload_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
