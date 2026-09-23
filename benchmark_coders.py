#!/usr/bin/env python3
"""
Lightweight benchmark for local coding models.

Subcommands:
  --sweep                       Benchmark every model in MODEL_ALIASES + --extra-tag entries.
  --model TAG --prompt "..."    Single-model run.
  --prompt "..."                Default coding challenge.
  --extra-tag TAG               Repeatable: add a tag to the sweep.

Each run appends one JSON line to benchmark_coders_results.jsonl.
Use --sweep to print a Markdown summary table at the end.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PROMPT = (
    "Write a Python function called fibonacci(n) that returns the first n"
    " Fibonacci numbers as a list. Include type hints, a single-line docstring,"
    " and a one-line example call. Return only Python code - no markdown fences."
)


def _load_aliases() -> dict[str, str]:
    """Sibling import of MODEL_ALIASES from local_ai_assistant.py."""
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here / "ComfyUI" / "tools"))
    import local_ai_assistant  # type: ignore
    return dict(local_ai_assistant.MODEL_ALIASES)


def run_one(tag: str, prompt: str, *, timeout: int = 600, max_capture: int = 8192) -> dict:
    """Call ``ollama run TAG PROMPT`` (one-shot mode), measure wall-clock, capture stdout."""
    if shutil.which("ollama") is None:
        raise RuntimeError("ollama binary not on PATH")
    start = time.perf_counter()
    try:
        result = subprocess.run(
            ["ollama", "run", tag, prompt],
            capture_output=True,
            timeout=timeout,
            text=True,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start
        return {
            "tag": tag, "secs": round(elapsed, 2), "words": 0, "chars": 0,
            "chars_per_sec": 0.0, "exit_code": -1, "stderr_tail": ["TIMEOUT"],
            "error": "timeout",
        }
    elapsed = time.perf_counter() - start
    out = (result.stdout or "")[:max_capture]
    err = (result.stderr or "")[:512]
    words = len(out.split())
    chars = len(out)
    chars_per_sec = round(chars / elapsed, 2) if elapsed > 0 else 0.0
    return {
        "tag": tag,
        "secs": round(elapsed, 2),
        "words": words,
        "chars": chars,
        "chars_per_sec": chars_per_sec,
        "exit_code": result.returncode,
        "stderr_tail": err.strip().splitlines()[-3:] if err.strip() else [],
    }


def _print_row(label: str, secs: float, words: int, chars: int, chars_per_sec: float) -> None:
    print(f"{label:<32}  secs={secs:>6.2f}  words={words:>4}  chars={chars:>5}  c/s={chars_per_sec:>6.2f}")


def _append_log(path: Path, entry: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark local coding models")
    parser.add_argument("--model", help="Single model tag to run")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Coding prompt (default: fibonacci challenge)")
    parser.add_argument("--extra-tag", action="append", default=[], help="Additional tag for sweep (repeatable)")
    parser.add_argument("--sweep", action="store_true", help="Benchmark MODEL_ALIASES + --extra-tag entries")
    parser.add_argument("--log", type=Path, default=Path(__file__).resolve().parent / "benchmark_coders_results.jsonl")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    if shutil.which("ollama") is None:
        print("ERROR: ollama binary not on PATH. Install from https://ollama.com/download", file=sys.stderr)
        return 2

    entries: list[dict] = []
    timestamp = datetime.now(timezone.utc).isoformat()

    if args.sweep:
        try:
            aliases = _load_aliases()
        except Exception as exc:
            print(f"ERROR loading MODEL_ALIASES: {exc}", file=sys.stderr)
            return 1
        targets: list[tuple[str, str]] = [(alias, tag) for alias, tag in aliases.items()]
        for tag in args.extra_tag:
            targets.append((tag, tag))

        print(f"Sweeping {len(targets)} models with: {args.prompt[:80]!r}...")
        print()
        for label, tag in targets:
            print(f"\n>>> Tag: {label} -> {tag}")
            try:
                res = run_one(tag, args.prompt, timeout=args.timeout)
                res["alias"] = label
                res["timestamp"] = timestamp
                entries.append(res)
                _print_row(label, res["secs"], res["words"], res["chars"], res["chars_per_sec"])
                _append_log(args.log, res)
            except subprocess.TimeoutExpired:
                print(f"  TIMEOUT after {args.timeout}s; skipping")
                entries.append({"alias": label, "tag": tag, "error": "timeout"})
            except Exception as exc:
                print(f"  ERROR: {exc}")
                entries.append({"alias": label, "tag": tag, "error": str(exc)})

        # Summary table
        print()
        print("| Model | Secs | Words | Chars | Chars/sec |")
        print("|-------|------|-------|-------|-----------|")
        for e in entries:
            if "error" in e:
                print(f"| {e['alias']} | ERR | ERR | ERR | ERR |")
            else:
                print(f"| {e['alias']} | {e['secs']} | {e['words']} | {e['chars']} | {e['chars_per_sec']} |")
        return 0

    # Single mode
    if not args.model:
        parser.error("Provide --model OR --sweep")
    res = run_one(args.model, args.prompt, timeout=args.timeout)
    res["timestamp"] = timestamp
    _append_log(args.log, res)
    _print_row(args.model, res["secs"], res["words"], res["chars"], res["chars_per_sec"])
    return res["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
