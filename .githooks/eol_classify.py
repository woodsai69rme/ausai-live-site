#!/usr/bin/env python
# .githooks/eol_classify.py -- byte-exact EOL classifier for the Golden Rules
# Stage 0 guard, section 3 (added 2026-09-29).
#
# Why python: MSYS text-mode redirection can strip \r bytes when the sh guard
# writes blob contents to scratch files, making pure-sh CR counting unreliable.
# A native python subprocess captures `git cat-file blob` output as exact
# bytes -- no text-mode translation anywhere in the pipeline.
#
# Usage: python eol_classify.py <tree-ish>
#   The classifier enumerates staged A/C/M/R/T changes itself via
#   `git diff-index --cached --name-status --diff-filter=ACMRT <tree-ish>`.
# Output: zero or more verdict lines:
#   __MIXED__ <path>            uniform in HEAD -> mixed staged blob (BLOCK)
#   __FLIP__ <path> (a -> b)    pure whole-file LF<->CRLF conversion (NOTE)
#   __EOLERR__ <path>           classification failure (fail closed)
# Already-mixed files, new files, and binary files produce no verdict line.
# Exit codes: 0 = classified (even if verdicts exist), 1 = usage error.

import subprocess
import sys

UNIFORM = ("lf", "crlf", "none")
FLIPS = {("lf", "crlf"), ("crlf", "lf"), ("none", "lf"), ("none", "crlf")}


def classify(data: bytes) -> str:
    if b"\x00" in data[:8192]:
        return "binary"
    crlf = data.count(b"\r\n")
    lf_total = data.count(b"\n")
    lf_only = lf_total - crlf
    if crlf and lf_only:
        return "mixed"
    if crlf:
        return "crlf"
    if lf_total:
        return "lf"
    return "none"


def git_bytes(*args):
    return subprocess.run(["git", *args], capture_output=True).stdout


def blob_class(rev: str) -> str:
    sha = subprocess.run(["git", "rev-parse", "--quiet", "--verify", rev],
                         capture_output=True, text=True)
    if sha.returncode != 0 or not sha.stdout.strip():
        return "absent"
    blob = subprocess.run(["git", "cat-file", "blob", sha.stdout.strip()],
                          capture_output=True)
    if blob.returncode != 0:
        return "error"
    return classify(blob.stdout)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: eol_classify.py <tree-ish>", file=sys.stderr)
        return 1
    treeish = sys.argv[1]
    manifest = git_bytes("diff-index", "--cached", "--name-status",
                         "--diff-filter=ACMRT", treeish)
    for line in manifest.decode("utf-8", errors="replace").splitlines():
        line = line.rstrip("\r")
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0][:1]
        if status in ("R", "C") and len(parts) >= 3:
            path = parts[2]
        elif len(parts) >= 2:
            path = parts[1]
        else:
            continue
        if not path:
            continue
        new_cls = blob_class(":" + path)
        if new_cls == "absent":
            continue  # not resolvable in index; nothing to check
        old_cls = blob_class(treeish + ":" + path)
        if new_cls == "error" or old_cls == "error":
            print(f"__EOLERR__ {path}")
        elif old_cls in UNIFORM and new_cls == "mixed":
            print(f"__MIXED__ {path}")
        elif (old_cls, new_cls) in FLIPS:
            print(f"__FLIP__ {path} ({old_cls} -> {new_cls})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
