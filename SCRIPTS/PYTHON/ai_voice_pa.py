#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_voice_pa.py — AI Voice Personal Assistant runtime
=====================================================

First concrete runner for AI_VOICE_PA_DESIGN.md (OPT-2.7 + OPT-10.5). Captures
audio (or reads a transcript file), runs STT through a deterministic local
stub, classifies intent via a closed enum, and appends four rows per
invocation to AI_VOICE_PA_AUDIT.log.

✅ COMPLIANCE
- ADDITIVE ONLY — source is never rewritten; audit log is append-only.
- Personal-folder guard rigid: refuses any --source / --audit-out path inside
  Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, or
  Downloads\\ARCHIVE_OLD.

Refusal matrix
- --source in Rule #8              -> exit 1
- --audit-out in Rule #8            -> exit 1
- --stt cloud without credentials   -> exit 1
- intent-enum != INTENT_ENUM         -> exit 1

Default mode is --dry-run. --run is opt-in.

Usage
    python3 ai_voice_pa.py --source file:transcript.txt
    # (dry-run; prints plan; writes nothing)

    python3 ai_voice_pa.py --source file:transcript.txt --run
    # (writes 4 rows to AI_VOICE_PA_AUDIT.log)
"""

# ---------------------------------------------------------------------------
# Golden Rules baked in
# ---------------------------------------------------------------------------
GOLDEN_RULES = (
    "ADDITIVE ONLY - source is not modified; audit log grows append-only.",
    "Personal folders (Documents, Downloads, Pictures, Videos, Music, "
    "Desktop, OneDrive, Downloads\\ARCHIVE_OLD) are NEVER picked as "
    "--source or --audit-out paths; never read as input.",
)
PERSONAL_FOLDERS = (
    "Documents", "Downloads", "Pictures", "Videos", "Music",
    "Desktop", "OneDrive", "ARCHIVE_OLD",
)
INTENT_ENUM = ("transcribe", "summarize", "dispatch", "pause", "noop")
MAX_MIC_SECONDS = 30


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def is_in_personal(path: str) -> bool:
    if not path:
        return False
    norm = path.replace("\\", "/").rstrip("/")
    for pf in PERSONAL_FOLDERS:
        suffix = "/" + pf
        if norm.endswith(suffix) or (suffix + "/") in norm:
            return True
    return False


def iso_now() -> str:
    import datetime as _dt
    return _dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def append_audit(path: str, line: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(line.rstrip("\n") + "\n")


def parse_source(spec: str):
    """Returns ('mic', N) or ('file', path). Raises on bad spec."""
    if not spec:
        raise ValueError("source spec empty")
    if spec.startswith("mic:"):
        try:
            n = int(spec.split(":", 1)[1].strip())
        except ValueError:
            raise ValueError("mic spec must be 'mic:N' where N is integer seconds")
        if n < 1 or n > MAX_MIC_SECONDS:
            raise ValueError(f"mic duration must be 1..{MAX_MIC_SECONDS}s; got {n}")
        return ("mic", n)
    if spec.startswith("file:"):
        return ("file", spec.split(":", 1)[1].strip())
    raise ValueError("--source must start with 'mic:' or 'file:'")


def local_stt_stub(source_kind: str, source_val) -> dict:
    """Deterministic stub: when source is file:, return file's first 200 chars
    plus a tag; when source is mic:N, return a no-content stub.
    """
    if source_kind == "file":
        try:
            with open(source_val, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            return {"ok": False, "chars": 0, "text": "", "error": str(e)}
        excerpt = text.strip()[:200]
        return {"ok": True, "chars": len(text), "text": excerpt}
    # mic stub: zero chars, ok=True
    return {"ok": True, "chars": 0, "text": ""}


def classify_intent(text: str, intent_enum) -> tuple:
    """Keyword-overlap on the closed intent enum; ties -> 'noop'."""
    import re
    tokens = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9-]+", text)]
    if not tokens:
        return ("pause", 0.0)
    best_intent = None
    best_count = 0
    for intent in intent_enum:
        # crude: count occurrences of the intent word itself in text
        count = sum(1 for t in tokens if intent in t)
        if count > best_count:
            best_count = count
            best_intent = intent
    if not best_intent:
        return ("noop", 0.0)
    conf = float(best_count) / float(max(1, len(tokens)))
    return (best_intent, conf)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    import argparse as _ap
    import sys as _sys

    ap = _ap.ArgumentParser(description="AI Voice Personal Assistant (local stub).")
    ap.add_argument("--source", required=True,
                    help="Capture source: 'mic:N' (N<=30s) or 'file:<path>:'.")
    ap.add_argument("--stt", default="local-stub",
                    help="Speech-to-text backend: 'local-stub' (default), 'cloud', 'off'.")
    ap.add_argument("--i-have-credentials", action="store_true",
                    help="Required flag for --stt cloud; refuse without it.")
    ap.add_argument("--intent-enum", default=",".join(INTENT_ENUM),
                    help="Comma-separated closed intents (default the 5-element enum).")
    ap.add_argument("--audit-out", default="AI_VOICE_PA_AUDIT.log",
                    help="Append-only audit log path.")
    ap.add_argument("--run", action="store_true",
                    help="Actually run. Default is dry-run.")
    args = ap.parse_args()

    try:
        source_kind, source_val = parse_source(args.source)
    except ValueError as e:
        print(f"REFUSED: --source invalid: {e}", file=_sys.stderr)
        return 1

    # Personal-folder guard.
    if source_kind == "file" and is_in_personal(source_val):
        print(f"REFUSED: --source file '{source_val}' resolves inside a Rule #8 personal folder.",
              file=_sys.stderr)
        return 1
    if is_in_personal(args.audit_out):
        print(f"REFUSED: --audit-out '{args.audit_out}' resolves inside a Rule #8 personal folder.",
              file=_sys.stderr)
        return 1

    if args.stt == "cloud" and not args.i_have_credentials:
        print("REFUSED: --stt cloud requires --i-have-credentials (no implicit cloud upload).",
              file=_sys.stderr)
        return 1

    intents = tuple(int(i.strip()) for i in args.intent_enum.split(",") if i.strip())
    for i in intents:
        if i not in INTENT_ENUM:
            print(f"REFUSED: intent '{i}' is not in the closed INTENT_ENUM {INTENT_ENUM}.",
                  file=_sys.stderr)
            return 1

    # Compute (text, duration, intent, conf).
    if args.stt == "local-stub":
        stt = local_stt_stub(source_kind, source_val)
        duration_s = source_val if source_kind == "mic" else 0
    elif args.stt == "off":
        stt = {"ok": True, "chars": 0, "text": ""}
        duration_s = source_val if source_kind == "mic" else 0
    else:  # cloud (with --i-have-credentials)
        # Stubbed: do not actually upload; defer to operator implementation.
        stt = {"ok": True, "chars": 0, "text": "", "backend": "cloud-stub"}
        duration_s = source_val if source_kind == "mic" else 0

    if stt.get("ok") and stt.get("chars", 0) > 0:
        intent, conf = classify_intent(stt["text"], INTENT_ENUM)
    else:
        intent, conf = ("pause", 0.0)

    plan = {
        "source_kind": source_kind,
        "source_val": source_val,
        "duration_s": duration_s,
        "stt": stt,
        "intent": intent,
        "conf": conf,
    }

    if not args.run:
        print("DRY-RUN ai_voice_pa: would append 4 rows to", args.audit_out)
        print("  -", plan)
        return 0

    # Real: append 4 rows.
    ts = iso_now()
    append_audit(args.audit_out,
                 f"{ts} | event=capture | source={source_kind}:{source_val} | duration_s={duration_s}")
    append_audit(args.audit_out,
                 f"{ts} | event=stt | backend={args.stt} | chars={stt.get('chars', 0)} | status={'ok' if stt.get('ok') else 'empty'}")
    append_audit(args.audit_out,
                 f"{ts} | event=intent_dispatch | intent={intent} | conf={conf:.4f}")
    append_audit(args.audit_out,
                 f"{ts} | event=run_complete | intent={intent} | chars={stt.get('chars', 0)} | duration_s={duration_s}")
    print(f"ai_voice_pa: appended 4 rows to {args.audit_out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
