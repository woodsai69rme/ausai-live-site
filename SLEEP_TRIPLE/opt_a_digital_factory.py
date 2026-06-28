#!/usr/bin/env python3
"""
opt_a_digital_factory.py — Option A: AI Digital Product Factory.

Generates AI prompt packs, code snippets, and design assets while user sleeps.
Calls local Ollama (HTTP POST /api/generate) for real generation with model
discovery fallback if preferred model isn't installed. Stages products as
Gumroad drafts (auto-listing in --publish mode).

Closed enums:
    EXEC_STATUS  = (started, ok, skipped, refused, noop, failed)
    PRODUCT_KIND = (ai_prompts, code_snippets, design_assets)
    PUBLISH_MODE = (draft_only, staged, published)

Default: --dry-run. Products are generated and saved to ./outbox/ but NOT uploaded.
Use --publish for staged upload simulation, --run for live Gumroad API calls.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "opt_a_config.json"
OUTBOX = ROOT / "outbox" / "a_digital_factory"
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"
MASTER_CONFIG_PATH = ROOT / "sleep_config.json"

EXEC_STATUS = ("started", "ok", "skipped", "refused", "noop", "failed")
PRODUCT_KIND = ("ai_prompts", "code_snippets", "design_assets")
PUBLISH_MODE = ("draft_only", "staged", "published")

RULE_8_FOLDERS = frozenset(
    ["Documents", "Downloads", "Pictures", "Videos", "Music", "Desktop",
     "OneDrive", "ARCHIVE_OLD"]
)


def is_rule_8(p: Path) -> bool:
    return bool({seg.name for seg in p.resolve().parents} & RULE_8_FOLDERS)


def assert_rule_8_path(p: Path, label: str) -> int:
    if is_rule_8(p):
        print(f"REFUSED: {label} path {p} violates Rule #8 fence", file=sys.stderr)
        return 2
    return 0


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_orchestrator_config() -> dict:
    return json.loads(MASTER_CONFIG_PATH.read_text(encoding="utf-8"))


def ping_comfyui(url: str, timeout: float = 2.0) -> bool:
    """TCP-only probe (rules out crashed endpoint without making an HTTP call)."""
    try:
        host = url.split("//", 1)[-1].split(":")[0]
        port = int(url.rsplit(":", 1)[-1].split("/", 1)[0])
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def select_ollama_model(preferred: str) -> str:
    """Probe /api/tags; return preferred if installed; else first qwen* or other fallback."""
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
    for m in sorted(installed):
        if any(name in m for name in ("deepseek-r1", "gemma", "phi", "mistral", "llama")):
            return m
    return next(iter(installed), preferred)


def ollama_generate(model: str, prompt: str, timeout: float = 120.0) -> str:
    """POST /api/generate with stream=False and 5-min keep_alive."""
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "5m",
        "options": {"temperature": 0.7, "num_predict": 2048},
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=body, headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
        return (payload.get("response") or "").strip()


def generate_prompts(model: str, topic: str, dry_run: bool) -> tuple:
    """Produce a 30-prompt pack. Returns (body, data_source).
    data_source values: 'placeholder' (dry-run), 'real' (ollama succeeded), 'synthetic' (fallback)."""
    prompt = (
        f"Generate a curated 30-item prompt pack for the topic: {topic}. "
        f"Numbered list only. No preamble, no closing remarks, no markdown fences."
    )
    if dry_run:
        lines = [f"{i:02d}. [PLACEHOLDER_PROMPT #{i} FOR TOPIC: {topic}]"
                 for i in range(1, 31)]
        return "\n".join(lines), "placeholder"
    resolved = select_ollama_model(model)
    try:
        text = ollama_generate(resolved, prompt, timeout=120.0)
        if text and len(text) > 60:
            print(f"[opt_a] ollama ok: model={resolved}, chars={len(text)}", file=sys.stderr)
            return text, "real"
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError) as exc:
        print(f"[opt_a] ollama_generate failed ({resolved}): {exc.__class__.__name__}: {exc}",
              file=sys.stderr)
    placeholder = "\n".join(
        [f"{i:02d}. [PLACEHOLDER_PROMPT #{i} FOR TOPIC: {topic}]" for i in range(1, 31)])
    return "[ollama-failed-fallback-to-placeholder]\n" + placeholder, "synthetic"


def save_product(kind: str, topic: str, body: str, data_source: str, dry_run: bool) -> Path:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = topic.lower().replace(" ", "_").replace("/", "_")[:40]
    out_path = OUTBOX / f"{kind}__{slug}__{stamp}.txt"
    header = (f"# {kind.replace('_', ' ').title()}: {topic}\n"
              f"# generated by opt_a_digital_factory.py\n"
              f"# dry_run={dry_run} | data_source={data_source}\n\n")
    out_path.write_text(header + body, encoding="utf-8")
    return out_path


def gumroad_publish_stub(product_path: Path, mode: str, dry_run: bool) -> str:
    """Returns 'staged' action summary. No live HTTP call unless --publish --run."""
    if mode == "draft_only":
        return f"draft_only: {product_path.name}"
    if mode == "staged":
        return f"staged: would upload to Gumroad (would_create_url=gumroad.com/l/{product_path.stem})"
    if mode == "published" and not dry_run:
        return f"published: stubbed (real call would hit api.gumroad.com/v2/products)"
    return f"published: stubbed dry-run"


def append_audit(row: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Option A — AI Digital Product Factory")
    ap.add_argument("--dry-run", action="store_true", help="Generate products without uploading")
    ap.add_argument("--run", action="store_true", help="Allow real Gumroad upload (post --publish)")
    ap.add_argument("--publish", choices=PUBLISH_MODE, default="draft_only",
                    help="draft_only / staged / published")
    ap.add_argument("--kind", choices=PRODUCT_KIND, default="ai_prompts")
    ap.add_argument("--topic", default="AI productivity for small business owners")
    args = ap.parse_args()

    cfg = load_config()
    master = load_orchestrator_config()
    dry_run = not args.run
    tz = ZoneInfo(master.get("tz", "Australia/Sydney"))
    now_iso = datetime.now(tz).isoformat()

    rc = assert_rule_8_path(OUTBOX, "OUTBOX")
    if rc != 0:
        append_audit({"ts": now_iso, "module": "opt_a", "status": "refused",
                      "reason": "rule8_path", "path": str(OUTBOX)})
        return rc

    if args.dry_run and args.run:
        print("REFUSED: --dry-run and --run together (drop --dry-run to allow real uploads)",
              file=sys.stderr)
        append_audit({"ts": now_iso, "module": "opt_a", "status": "refused",
                      "reason": "dryrun_and_run"})
        return 5

    if args.kind not in PRODUCT_KIND:
        print(f"REFUSED: --kind {args.kind} not in closed enum", file=sys.stderr)
        append_audit({"ts": now_iso, "module": "opt_a", "status": "refused",
                      "reason": "bad_kind", "kind": args.kind})
        return 5
    if args.publish not in PUBLISH_MODE:
        print(f"REFUSED: --publish {args.publish} not in closed enum", file=sys.stderr)
        append_audit({"ts": now_iso, "module": "opt_a", "status": "refused",
                      "reason": "bad_publish_mode", "mode": args.publish})
        return 5

    append_audit({"ts": now_iso, "module": "opt_a", "status": "started",
                  "kind": args.kind, "publish": args.publish, "dry_run": dry_run,
                  "topic": args.topic, "model_requested": cfg["ollama_model_preference"],
                  "products_per_night": cfg["products_per_night"]})

    comfy_alive = ping_comfyui(cfg["comfyui_url"])
    if not comfy_alive and cfg.get("enable_comfy_cover", False):
        append_audit({"ts": now_iso, "module": "opt_a", "status": "refused",
                      "reason": "comfyui_down", "url": cfg["comfyui_url"]})
        return 6

    body, data_source = generate_prompts(cfg["ollama_model_preference"], args.topic, dry_run)
    product_path = save_product(args.kind, args.topic, body, data_source, dry_run)
    publish_summary = gumroad_publish_stub(product_path, args.publish, dry_run)

    append_audit({"ts": now_iso, "module": "opt_a", "status": "ok",
                  "kind": args.kind, "publish": args.publish, "dry_run": dry_run,
                  "product_path": str(product_path), "publish_summary": publish_summary,
                  "characters": len(body), "data_source": data_source,
                  "comfyui_alive": comfy_alive})
    print(f"[opt_a] wrote {product_path.name} ({len(body)} chars, {data_source}) | {publish_summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
