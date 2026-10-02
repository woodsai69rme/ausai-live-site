#!/usr/bin/env python3
# .githooks/eol_watchdog.py -- periodic advisory EOL drift check (added 2026-10-01).
#
# Read-only. Never writes any repo file except the append-only drift log and,
# on --init, the baseline JSON. Classification is delegated to eol_audit.py
# (tracked_paths / gitattributes_pins / index_kinds / classify) so there is
# exactly one source of truth for the byte rules.
#
# Modes:
#   --init        snapshot the current index census as the baseline, then exit 0
#   (default)     census, compare with baseline, append one CRLF line to the
#                 drift log; exit 2 only on a REGRESSION vs baseline
#   --quiet       same, but no stdout summary (scheduled-task mode)
#   --log PATH    drift log path      (default: .githooks/eol_watchdog.log)
#   --baseline P  baseline JSON path  (default: .githooks/eol_watchdog_baseline.json)
#
# Exit codes: 0 = clean or improvement, 1 = error (e.g. no baseline),
# 2 = regression (mixed count grew, or a NEW unpinned mixed file appeared).
# Advisory only: never blocks a commit (that is eol_classify.py's job, via the
# pre-commit guard); the watchdog exists so drift between commits gets noticed.
#
# The drift log is append-only per Golden Rules v1.1 and uses CRLF endings so
# MSYS text tools cannot silently mangle it; *.log is .gitignore'd.
# The baseline JSON is committed; when a settlement legitimately lowers the
# mixed count, re-run --init and commit the new baseline in the same commit.

import argparse
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import eol_audit  # noqa: E402  (same directory; read-only census)


def census() -> dict:
    """Index census reusing eol_audit's helpers: {path: {'class','pin'}}."""
    paths = eol_audit.tracked_paths()
    pins = eol_audit.gitattributes_pins()
    kinds = eol_audit.index_kinds(paths)
    return {p: {"class": kinds.get(p, "unreadable"), "pin": pins.get(p)}
            for p in paths}


def summarize(fmap: dict) -> dict:
    unpinned_mixed = sorted(
        p for p, i in fmap.items()
        if i["class"] == "mixed" and not i["pin"])
    return {
        "mixed": sum(1 for i in fmap.values() if i["class"] == "mixed"),
        "mixed_unpinned": len(unpinned_mixed),
        "unpinned_mixed_paths": unpinned_mixed,
    }


def load_baseline(path: str) -> dict:
    with open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


def log_line(log_path: str, text: str) -> None:
    line = text.replace("\r", "").replace("\n", " ") + "\r\n"
    with open(log_path, "ab") as f:
        f.write(line.encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="EOL drift watchdog (read-only)")
    ap.add_argument("--init", action="store_true",
                    help="snapshot the current census as the baseline")
    ap.add_argument("--quiet", action="store_true", help="suppress stdout")
    ap.add_argument("--log", default=os.path.join(HERE, "eol_watchdog.log"))
    ap.add_argument("--baseline",
                    default=os.path.join(HERE, "eol_watchdog_baseline.json"))
    try:
        args = ap.parse_args()
    except SystemExit:
        return 1

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        fmap = census()
    except Exception as exc:
        log_line(args.log, "ERROR {} | census failed: {}".format(now, exc))
        if not args.quiet:
            print("eol_watchdog: census failed: {}".format(exc), file=sys.stderr)
        return 1

    snap = summarize(fmap)

    if args.init:
        payload = {
            "created": now,
            "scanned": len(fmap),
            "mixed": snap["mixed"],
            "mixed_unpinned": snap["mixed_unpinned"],
            "unpinned_mixed_paths": snap["unpinned_mixed_paths"],
        }
        with open(args.baseline, "wb") as f:
            f.write(json.dumps(payload, indent=1, sort_keys=True).encode("utf-8"))
        if not args.quiet:
            print("baseline written: {} (scanned={}, mixed={}, unpinned={})".format(
                args.baseline, payload["scanned"], payload["mixed"],
                payload["mixed_unpinned"]))
        return 0

    try:
        base = load_baseline(args.baseline)
    except Exception as exc:
        log_line(args.log, "ERROR {} | baseline unreadable: {}".format(now, exc))
        if not args.quiet:
            print("eol_watchdog: baseline unreadable (run --init): {}".format(exc),
                  file=sys.stderr)
        return 1

    # ---- regression analysis ----
    verdict, exit_code, details = "OK", 0, []
    if snap["mixed"] > base["mixed"]:
        verdict, exit_code = "REGRESSION", 2
        details.append("mixed {} -> {}".format(base["mixed"], snap["mixed"]))
    new_unpinned = sorted(set(snap["unpinned_mixed_paths"])
                          - set(base["unpinned_mixed_paths"]))
    if new_unpinned:
        verdict, exit_code = "REGRESSION", 2
        details.append("new unpinned mixed: {}".format(", ".join(new_unpinned)))
    if exit_code == 0 and snap["mixed"] < base["mixed"]:
        details.append("improved: mixed {} -> {} (baseline not auto-lowered; "
                       "re-run --init to accept)".format(base["mixed"],
                                                         snap["mixed"]))

    sha = hashlib.sha1(json.dumps(
        sorted((p, i["class"], i["pin"] or "") for p, i in fmap.items())
    ).encode("utf-8")).hexdigest()[:12]

    line = "{} | {} | mixed={} (unpinned={}) | files={} | sha={}{}".format(
        now, verdict, snap["mixed"], snap["mixed_unpinned"], len(fmap), sha,
        (" | " + "; ".join(details)) if details else "")
    log_line(args.log, line)
    if not args.quiet:
        print(line)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
