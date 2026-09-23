#!/usr/bin/env python3
"""bin/run_audit_subprocess.py -- cross-platform Python wrapper for invoking Win32 .bat
installers / CI commands without triggering the MINGW/Git-bash pipe-buffer deadlock.

# Why this exists (cont.16-fup-3)

Documented in `bin/install_ALL_TASKS_AUDIT_LOG.md` (Diagnostic footer, post-Phase-G entry):
when a single bash command line spawns many `cmd.exe` child processes with
`subprocess.run([...], capture_output=True)`, two failure modes are observed on
Git Bash (MINGW):

1. **MINGW pipe-buffer deadlock.** Python's stdout pipe to cmd.exe gets full;
   cmd.exe blocks on the next stdout write; Python then blocks on
   `communicate()`; the whole pipeline hangs until the basher-level 60s timeout
   aborts the call. This is well-known for MINGW + interactive shell layers.

2. **Orphaned-process pipe deadlock on timeout** (cont.16-fup-3 second fix).
   On Windows, `subprocess.run(timeout=...)` calls `TerminateProcess()` which
   kills the IMMEDIATE child (cmd.exe) but ORPHANS grandchildren (e.g.
   `powershell.exe`, child `cmd //c` scripts). Those grandchildren still hold
   the write-end of the pipe handles. Python's `communicate()` blocks
   indefinitely waiting for those pipes to close -- even though the timeout
   already exceeded. This hang CANNOT be detected by Python; only the
   outer basher-level timeout aborts the call.

The winning approach (Phase-G + Phase-H of cont.16-fup-3 derivation) is to
invoke the bat NATIVELY from a SINGLE `cmd.exe` invocation AND bypass `PIPE`
altogether by writing stdout/stderr straight to disk:
  - Stage 1 (fup-3 first cut): `subprocess.run` with `capture_output=True` and
    single native `cmd /c <bat>` invocation -- fixed failure mode 1 but hit
    failure mode 2 when timeout fired.
  - Stage 2 (fup-3 second cut, THIS VERSION): use file handles (`stdout=fout,
    stderr=ferr`) instead of `capture_output=True`. Then Python reads the
    captured files back synchronously after `subprocess.run` returns.
    On Windows timeout, Python can exit cleanly even while grandchildren
    continue writing to the closed-output files (which become broken-pipe
    writes -- harmless). This fixes BOTH failure modes.

This Python wrapper encapsulates that pattern: take the operator's --cmd
string, write stdout/stderr to --out-file / --err-file via a single
cmd /c <cmd> subprocess, then read the files back to print a tail summary
and exit with the child's exit code.

# Usage

    python bin/run_audit_subprocess.py --cmd "bin\\install_ALL_TASKS_AUDIT.bat"
    python bin/run_audit_subprocess.py --cmd "bin\\install_ALL_TASKS_AUDIT.bat" --timeout 120
    python bin/run_audit_subprocess.py --cmd "bin\\install_ALL_TASKS_AUDIT.bat" --tail 30
    python bin/run_audit_subprocess.py --cmd "python script.py --dry-run" --cwd "C:\\some\\path"

# Arguments

    --cmd <string>           REQUIRED. The .bat or command to run. Forwarded VERBATIM
                             to a single cmd /c <cmd> invocation so quoting /
                             percent-variable expansion / pipeline operators all
                             work as in a normal cmd.exe window.
                             NOTE: argparse help texts AVOID the percent character
                             here because Python 3.13 argparse treats the help
                             string as a printf format string (gotcha).
    --timeout <seconds>      Optional. Default 120. Per-process wall-clock timeout.
                             On timeout, partial output is printed and exit 124
                             (mirroring coreutils timeout(1) convention).
    --tail <N>               Optional. Default 20. Number of trailing stdout lines
                             to show on completion.
    --cwd <path>             Optional. Default REPO_ROOT. Working-directory for the
                             child. Useful when invoking a bat elsewhere.
    --log-timestamp          Optional. Append a wall-clock ISO timestamp to the
                             captured stdout file (used by the audit-scheduler's
                             daily pre-flight task in cont.16-fup-5).
    --keep                   Optional. Don't delete tmp/_wrap_out.txt + tmp/_wrap_err.txt
                             after capturing (debug aid).
    --out-file <path>        Optional. Override stdout capture path.
                             Default: REPO_ROOT/tmp/_wrap_out.txt
    --err-file <path>        Optional. Override stderr capture path.
                             Default: REPO_ROOT/tmp/_wrap_err.txt

# Exit codes

    0                        Child reported rc=0 (success).
    124                      Per-process timeout exceeded (partial output printed).
    2                        Pre-flight failure (e.g. --cwd does not exist).
    Any other                Mirror of child's exit code.

# Why single-string cmd + shell-style dispatch (instead of list-form)

We use `subprocess.run(["cmd", "/c", cmd_string], ...)` where `cmd_string` is
the operator's --cmd verbatim (NOT split-on-spaces). cmd.exe handles the parse,
including quoted arguments with spaces, percent-variable expansion, and pipe
pipelines. This matches what the operator would type at a real cmd.exe
prompt. Splitting on spaces would break `C:\\Program Files\\...` paths.

# Why file handles, NOT capture_output=True

On Windows, PIPE handles are inherited by grandchildren. When
TimeoutExpired fires, only the immediate child is killed -- grandchildren
retain the pipe write-end indefinitely, and Python's `communicate()` hangs
forever waiting for those pipes to drain. File handles do not have this
problem: when Python exits or the wrapper closes the file, subsequent writes
from orphaned grandchildren produce a benign broken-pipe write to a file
(Python's stdlib handles that).

# Distribution (PyInstaller --onefile; cont.16-fup-6)
#
# To produce a standalone Windows .exe that does NOT require Python at
# runtime, use `binuild_audit_exe.bat --rebuild` (added in cont.16-fup-6).
# That convenience bat invokes `pyinstaller --onefile` and lands the output
# in `bin\distun_audit_subprocess.exe`. The audit-scheduler XML template
# (`binudit_scheduler.xml`) was migrated to use this .exe as `<Command>`
# instead of `python`, so the scheduled task runs without requiring Python
# on the box. Manual `python binun_audit_subprocess.py` invocations still
# work alongside the .exe -- this is a drop-in addition.
#
# Caveats:
#   - PyInstaller --onefile adds ~0.5-2s cold-start per run (self-extract to
#     the user TEMP dir); vs the 25-30s wrapper measurement it is in the noise.
#   - The .exe is a per-machine release artifact; `bin\dist\`, `binuild\`,
#     and `binun_audit_subprocess.spec` are .gitignored (Pass-15 of the
#     .gitignore hygiene sweep). Only `binuild_audit_exe.bat` is committed.
#   - Antivirus heuristics occasionally flag unsigned PyInstaller --onefile
#     binaries on shared hosts; this dev box is unaffected.
"""
from __future__ import annotations

import argparse
import sys
import subprocess
import time
from datetime import datetime, timezone  # module-level hoist; was lazy import inside main()
from pathlib import Path

# Resolve REPO_ROOT as the parent of bin/ (where this script lives).
# __file__ is `bin/run_audit_subprocess.py` (Windows-friendly: forward OR back
# slashes both work in pathlib).
_THIS = Path(__file__).resolve()
REPO_ROOT = _THIS.parent.parent

DEFAULT_TIMEOUT = 120
DEFAULT_TAIL = 20
DEFAULT_CWD = REPO_ROOT
TIMEOUT_RC = 124
PRE_FLIGHT_RC = 2

DEFAULT_OUT = REPO_ROOT / "tmp" / "_wrap_out.txt"
DEFAULT_ERR = REPO_ROOT / "tmp" / "_wrap_err.txt"


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_audit_subprocess.py",
        description=(
            "Cross-platform wrapper for invoking Win32 .bat installers / CI commands "
            "without triggering the MINGW/Git-bash pipe-buffer deadlock OR the "
            "Windows orphaned-process pipe deadlock."
        ),
    )
    p.add_argument(
        "--cmd",
        required=True,
        help=(
            "REQUIRED. The .bat or command to run. Forwarded VERBATIM to "
            "the cmd /c chain so quoting, percent-variable expansion, and "
            "pipeline operators (|, &&, >) all work as in a normal cmd.exe "
            "window. Do NOT pre-split on spaces."
        ),
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Optional wall-clock timeout (seconds). Default {DEFAULT_TIMEOUT}.",
    )
    p.add_argument(
        "--tail",
        type=int,
        default=DEFAULT_TAIL,
        help=f"Optional number of trailing stdout lines to print. Default {DEFAULT_TAIL}.",
    )
    p.add_argument(
        "--cwd",
        type=str,
        default=str(DEFAULT_CWD),
        help=f"Optional working dir for child. Default REPO_ROOT={REPO_ROOT}.",
    )
    p.add_argument(
        "--log-timestamp",
        action="store_true",
        help=(
            "Optional. Emit ISO timestamp preamble to captured stdout file "
            "(used by the audit-scheduler pre-flight task in cont.16-fup-5)."
        ),
    )
    p.add_argument(
        "--keep",
        action="store_true",
        help="Optional. Don't delete captured stdout/stderr files after capture.",
    )
    p.add_argument(
        "--out-file",
        type=str,
        default=str(DEFAULT_OUT),
        help=f"Optional stdout capture path. Default {DEFAULT_OUT}.",
    )
    p.add_argument(
        "--err-file",
        type=str,
        default=str(DEFAULT_ERR),
        help=f"Optional stderr capture path. Default {DEFAULT_ERR}.",
    )
    return p


def banner(rc_label: str, elapsed_s: float, stdout_n: int, stderr_n: int) -> str:
    return f"[wrap] {rc_label} elapsed={elapsed_s:.2f}s stdout_lines={stdout_n} stderr_lines={stderr_n}"


def tail_lines(text: str, n: int) -> str:
    if n <= 0:
        return ""
    lines = text.splitlines()
    return "\n".join(lines[-n:])


def write_timestamp_preamble(file_path: Path, body: str) -> str:
    """Prepend an ISO timestamp preamble to `body` and overwrite `file_path`."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_body = f"# timestamp={ts}\n" + body
    try:
        file_path.write_text(new_body, encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"[wrap][WARN] cannot re-write {file_path}: {exc}", file=sys.stderr)
    return new_body


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    REPO_ROOT.mkdir(parents=True, exist_ok=True)
    child_dir = Path(args.cwd).resolve()
    if not child_dir.is_dir():
        print(f"[wrap][FAIL] --cwd {child_dir} is not an existing directory", file=sys.stderr)
        return PRE_FLIGHT_RC

    out_path = Path(args.out_file)
    err_path = Path(args.err_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    err_path.parent.mkdir(parents=True, exist_ok=True)
    # NOTE: do NOT pre-`unlink()`. Python's `open(path, "w", ...)` already
    # truncates-and-opens, atomically. Pre-unlink risks PermissionError
    # [WinError 32] when a previous case's orphaned grandchild (e.g.
    # ping.exe after a timeout) still holds the file write-end. With the
    # bare `open(path, "w")` path, the orphan is INDEPENDENT: truncating
    # one view of the file does not affect other open file table entries.
    # CAVEAT for operators: under shared-namespace multi-invocation contexts
    # (e.g. a verifier running 9 cases in sequence), ALWAYS pass unique
    # `--out-file` / `--err-file` per case so the orphan-truncation
    # mid-file garbage is contained. Sequential single-invocation usage
    # (operator runs the wrapper ad-hoc) is unaffected.

    # Single native cmd.exe invocation: this is the key to MINGW pipe-buffer
    # deadlock avoidance. cmd /c forwards our --cmd string through cmd.exe's
    # own argv parser, which honors quoting, percent-variable expansion, and
    # pipeline operators identically to an interactive cmd.exe.
    argv_list = ["cmd", "/c", args.cmd]
    print(f"[wrap] launching: {' '.join(argv_list)!r}", file=sys.stderr)
    print(f"[wrap] cwd:      {child_dir}", file=sys.stderr)
    print(f"[wrap] timeout:  {args.timeout}s", file=sys.stderr)
    print(f"[wrap] out:      {out_path}", file=sys.stderr)
    print(f"[wrap] err:      {err_path}", file=sys.stderr)

    t0 = time.time()
    rc = 0
    timed_out = False
    try:
        # FILE-HANDLE pattern (Phase-H fix): stdout/stderr to disk, NOT pipe.
        # This bypasses the orphaned-process pipe-deadlock on Windows timeouts:
        # subprocess.run(timeout=...) calls TerminateProcess on the immediate
        # child; orphaned grandchildren cannot hold a pipe write-end if there
        # is no pipe (file handles are not pipe handles). Even if grandchildren
        # keep running after Python exits, their writes are benign broken-pipe
        # writes to files. Critical invariant: do NOT use capture_output=True
        # here -- that re-introduces the PIPE path.
        with open(out_path, "w", encoding="utf-8", errors="replace", newline="") as fout, \
             open(err_path, "w", encoding="utf-8", errors="replace", newline="") as ferr:
            completed = subprocess.run(
                argv_list,
                cwd=str(child_dir),
                stdout=fout,
                stderr=ferr,
                timeout=args.timeout,
            )
            rc = completed.returncode
            elapsed = time.time() - t0
            rc_label = f"CHILD_RC={rc}"
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        rc = TIMEOUT_RC
        elapsed = time.time() - t0
        rc_label = f"TIMEOUT_RC={TIMEOUT_RC} (after {elapsed:.2f}s)"
        # File handles above are already closed by the with block exit.
        # Read whatever managed to be flushed before the kill fired.
        print(rc_label, file=sys.stderr)

    # Read both streams as text AFTER the child has exited / been killed.
    # In the timeout case these are PARTIAL outputs (the immediate child was
    # killed, so the file's last bytes are whatever got flushed before kill).
    out_text = ""
    err_text = ""
    try:
        out_text = out_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"[wrap][WARN] cannot read {out_path}: {exc}", file=sys.stderr)
    try:
        err_text = err_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"[wrap][WARN] cannot read {err_path}: {exc}", file=sys.stderr)

    # Optional ISO timestamp preamble for chrono-sorted daily traces
    # (cont.16-fup-5 audit scheduler pre-flight). Apply in BOTH success and
    # timeout branches so the captured file has uniform timestamp ordering.
    if args.log_timestamp and out_text:
        out_text = write_timestamp_preamble(out_path, out_text)

    print(banner(rc_label, elapsed, out_text.count("\n"), err_text.count("\n")), file=sys.stderr)
    if err_text.strip():
        print(f"[wrap][stderr-tail-{args.tail}]", file=sys.stderr)
        print(tail_lines(err_text, args.tail), file=sys.stderr)
    print(f"[wrap][stdout-tail-{args.tail}]", file=sys.stderr)
    print(tail_lines(out_text, args.tail))

    # Verbose: keep tmp files around for inspection. Same rationale as
    # above -- bare unlink() risks PermissionError if an orphan grandchild
    # is still holding the handle. Tolerate the failure silently, since
    # leaving the file on disk is acceptable for the debug aid use-case.
    if not args.keep:
        for p in (out_path, err_path):
            try:
                p.unlink(missing_ok=True)
            except PermissionError:
                pass  # orphan grandchild still holds handle; ignore
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
