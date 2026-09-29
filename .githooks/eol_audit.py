#!/usr/bin/env python
# .githooks/eol_audit.py -- READ-ONLY repo-wide line-ending census (added 2026-09-30).
#
# Complements eol_classify.py, which is the commit-time enforcer and only ever
# looks at STAGED changes. This tool is the periodic auditor: it reports the EOL
# state of every tracked file so drift that accumulates in the worktree between
# commits is visible before anyone stages it.
#
# It never writes, never stages, never touches the index or the working tree.
# Safe to run at any time, including mid-edit.
#
# Why python: same MSYS trap as eol_classify.py -- text-mode redirection strips
# \r, so pure-sh CR counting is unreliable. Blob bytes are captured natively.
#
# Usage:
#   python eol_audit.py                 # census of the INDEX  (default)
#   python eol_audit.py --worktree      # census of the WORKING TREE bytes
#   python eol_audit.py --mixed         # only files that are mixed, with detail
#   python eol_audit.py --check         # non-zero exit if any file is mixed
#   python eol_audit.py --unpinned      # mixed files that carry NO .gitattributes pin
#   python eol_audit.py --md            # restrict to *.md
#   python eol_audit.py --json          # machine-readable output
#
# Exit codes: 0 = census produced (even if mixed files exist, unless --check),
#             1 = usage error, 2 = git/python failure (fail closed).

import argparse
import json
import os
import subprocess
import sys
import threading

# Shared with eol_classify.py -- identical byte rules, deliberately duplicated
# rather than imported so this tool has no import-path dependency inside a hook.
UNIFORM = ("lf", "crlf", "none")


def classify(data: bytes) -> str:
    if b"\x00" in data[:8192]:
        return "binary"
    crlf = data.count(b"\r\n")
    lf_only = data.count(b"\n") - crlf
    if crlf and lf_only:
        return "mixed"
    if crlf:
        return "crlf"
    if data.count(b"\n"):
        return "lf"
    return "none"


def git_out(*args: str) -> bytes:
    """Run git and capture raw bytes -- never text mode (the \\r-stripping trap)."""
    p = subprocess.run(["git", *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git %s failed: %s"
                           % (" ".join(args), p.stderr.decode("utf-8", "replace").strip()))
    return p.stdout


def tracked_paths() -> list:
    raw = git_out("ls-files", "-z")
    return [p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p]


def gitattributes_pins() -> dict:
    """Map of exact-path pin -> attribute, from .gitattributes in the worktree."""
    pins = {}
    try:
        with open(".gitattributes", "rb") as f:
            data = f.read()
    except OSError:
        return pins
    for line in data.decode("utf-8", "replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split(None, 1)
        if len(parts) == 2:
            pins[parts[0]] = parts[1]
    return pins


def worktree_kind(path: str) -> str:
    if os.path.islink(path) or os.path.isdir(path):
        return "gitlink"
    try:
        with open(path, "rb") as f:
            return classify(f.read())
    except (OSError, ValueError):
        return "unreadable"


def index_kinds(paths: list) -> dict:
    """Classify every index blob in ONE batched `git cat-file --batch` process.

    A per-file `git cat-file` costs ~3000 process spawns and takes minutes; the
    batched form reads all blobs through a single pipe.

    The revs MUST be written concurrently with reading: this repo holds blobs of
    hundreds of KB, so writing every rev before reading any exceeds the 64 KB pipe
    buffer and deadlocks both processes. A writer thread keeps the pipe drained.
    The stream is parsed by length prefix, never as text (the \\r trap).
    """
    if not paths:
        return {}
    proc = subprocess.Popen(["git", "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    out = {}
    write_error = []

    def feed():
        try:
            for p in paths:
                proc.stdin.write((":" + p).encode("utf-8", "surrogateescape") + b"\n")
            proc.stdin.flush()
        except (OSError, ValueError) as e:
            write_error.append(e)
        finally:
            try:
                proc.stdin.close()
            except OSError:
                pass

    writer = threading.Thread(target=feed, daemon=True)
    writer.start()

    def read_exact(n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = proc.stdout.read(n - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    try:
        for p in paths:
            header = proc.stdout.readline()
            if not header:
                break
            parts = header.split()
            # "<rev> missing" or a non-blob type => gitlink (mode 160000) or a
            # path that vanished mid-scan. Not a defect; not a line-ending state.
            if len(parts) < 3 or parts[1] != b"blob":
                out[p] = "gitlink"
                continue
            try:
                size = int(parts[2])
            except ValueError:
                out[p] = "gitlink"
                continue
            data = read_exact(size)
            read_exact(1)  # trailing newline after the payload
            out[p] = classify(data)
    finally:
        writer.join(timeout=30)
        try:
            proc.stdout.close()
        except OSError:
            pass
        proc.kill()
        proc.wait()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--worktree", action="store_true",
                    help="census working-tree bytes instead of the index")
    ap.add_argument("--mixed", action="store_true", help="only show mixed files")
    ap.add_argument("--unpinned", action="store_true",
                    help="only mixed files that have no .gitattributes pin")
    ap.add_argument("--check", action="store_true",
                    help="exit 2 if any mixed file is found")
    ap.add_argument("--md", action="store_true", help="restrict to *.md")
    ap.add_argument("--json", action="store_true", dest="as_json")
    try:
        args = ap.parse_args()
    except SystemExit:
        print("usage: eol_audit.py [--worktree] [--mixed] [--unpinned] [--check] [--md] [--json]",
              file=sys.stderr)
        return 1

    try:
        paths = tracked_paths()
    except RuntimeError as e:
        print("FATAL: %s" % e, file=sys.stderr)
        return 2

    if args.md:
        paths = [p for p in paths if p.lower().endswith(".md")]

    pins = gitattributes_pins()
    source = "worktree" if args.worktree else "index"
    counts = {}
    mixed = []

    if args.worktree:
        kinds = {p: worktree_kind(p) for p in paths}
    else:
        kinds = index_kinds(paths)

    for p in paths:
        kind = kinds.get(p, "unreadable")
        counts[kind] = counts.get(kind, 0) + 1
        if kind == "mixed":
            entry = {"path": p, "source": source, "pin": pins.get(p)}
            if args.unpinned and entry["pin"]:
                continue
            mixed.append(entry)

    if args.as_json:
        print(json.dumps({
            "source": source,
            "scanned": len(paths),
            "counts": counts,
            "mixed_count": len(mixed),
            "mixed": mixed,
        }, indent=2, sort_keys=True))
    else:
        print("EOL census (%s) -- %d tracked files%s"
              % (source, len(paths), ", *.md only" if args.md else ""))
        print("-" * 68)
        for kind in sorted(counts, key=lambda k: -counts[k]):
            print("  %-10s %6d" % (kind, counts[kind]))
        print("-" * 68)
        print("  mixed: %d" % len(mixed))
        if mixed:
            label = "MIXED FILES (source: %s)" % source
            print("\n%s" % label)
            for e in mixed:
                pin = e["pin"] or "-- NO PIN --"
                print("  %-58s %s" % (e["path"][:58], pin))
            if not args.unpinned:
                unpinned = [e for e in mixed if not e["pin"]]
                if unpinned:
                    print("\n  %d mixed file(s) carry no .gitattributes pin -- these are"
                          " the ones to decide on." % len(unpinned))
                    for e in unpinned:
                        print("    %s" % e["path"])
                else:
                    print("\n  every mixed file is accounted for by an explicit pin"
                          " (frozen by decision).")

    if args.check and mixed:
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        print("FATAL: %s" % e, file=sys.stderr)
        sys.exit(2)
