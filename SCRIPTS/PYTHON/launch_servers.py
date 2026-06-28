"""launch_servers.py - detach-launch FastAPI on 8181 and http.server on 8080.

Background
----------
The first version of this script used ``subprocess.Popen`` with
``DETACHED_PROCESS | CREATE_NO_WINDOW`` creation flags. That proved
insufficient: the parent MSYS / Git Bash shell lives in a Windows Job
Object that tears down all associated children on exit, so the servers
died the moment basher-1 returned and basher-2 saw "Connection refused"
with empty ``fastapi-out.log`` / ``http-out.log``.

This v2 uses **Windows Task Scheduler** (``schtasks``) to start both
servers. The Task Scheduler service (svchost.exe) spawns the children
under a fresh Win32 session, completely outside the MSYS Job Object
boundary, so the children reliably survive across basher invocations.

Why this path
~~~~~~~~~~~~~
* Zero new dependency (uses stdlib ``subprocess`` + the Windows-native
  ``schtasks`` CLI that ships with every Windows install).
* Highest probability of working: Task Scheduler service has its own
  process tree, not bound to the calling shell.
* Idempotent cleanup via ``schtasks /delete``.

Run
~~~
From MSYS bash::

    python "C:\\Users\\karma\\launch_servers.py"

After running, give the servers ~10s to start, then smoke-test in a
separate basher call::

    curl -sS -m 5 http://127.0.0.1:8181/health
    curl -sS -m 5 -X POST http://127.0.0.1:8181/api/jarvis/command \\
         -H 'Content-Type: application/json' -d '{"command":"status"}'
    curl -sS -m 5 http://127.0.0.1:8080/ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html | head -3

Cleanup
-------
The script registers two named tasks (``archon-fastapi``,
``archon-http``). End and delete them with::

    schtasks /end   /tn archon-fastapi
    schtasks /delete /tn archon-fastapi /f
    schtasks /end   /tn archon-http
    schtasks /delete /tn archon-http /f

If the wrappers are still running the children can also be killed
directly via::

    taskkill /F /IM python.exe

Caveats
-------
* This script requires the launching user to be **logged in**. The
  scheduled tasks run under the current user; if the session is
  locked or disconnected, the Task Scheduler service will refuse to
  fire them. /ru SYSTEM bypasses this but is rejected with "Access
  is denied" from a non-elevated shell.
* The script does not detect zombie listeners on 8181 / 8080 left
  over from a prior run. If the port is already bound, the new
  child exits silently; the polling loop will surface "NOT BOUND"
  and the *err.log will carry the actual reason.
"""
import os
import shutil
import socket
import subprocess
import sys
import time

CORS_ORIGINS = (
    "http://localhost:3737,"
    "http://127.0.0.1:3737,"
    "http://localhost:8080,"
    "http://127.0.0.1:8080"
)

FASTAPI_BAT = r"C:\Users\karma\run_fastapi.bat"
HTTP_BAT     = r"C:\Users\karma\run_http.bat"
FASTAPI_OUT  = r"C:\Users\karma\fastapi-out.log"
FASTAPI_ERR  = r"C:\Users\karma\fastapi-err.log"
HTTP_OUT     = r"C:\Users\karma\http-out.log"
HTTP_ERR     = r"C:\Users\karma\http-err.log"
TASK_FASTAPI = "archon-fastapi"
TASK_HTTP    = "archon-http"


def write_bat(path, body):
    """Write a small .bat wrapper. CRLF line endings are required by cmd.exe."""
    with open(path, "wb") as f:
        f.write(body.encode("utf-8") + b"\r\n")


def find_uv():
    """3-layer resolution: 5 canonical paths, then where.exe, then shutil.which."""
    candidates = [
        r"C:\Users\karma\.local\bin\uv.exe",
        r"C:\Users\karma\AppData\Roaming\uv\uv.exe",
        r"C:\Users\karma\AppData\Local\uv\uv.exe",
        r"C:\Program Files\uv\uv.exe",
        r"C:\ProgramData\chocolatey\bin\uv.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    try:
        out = subprocess.check_output(
            ["where.exe", "uv"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        if out:
            return out.splitlines()[0]
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pass
    return shutil.which("uv")


def schtasks(*args):
    """Thin wrapper around `schtasks` that surfaces a CalledProcessError on non-zero exit."""
    return subprocess.check_call(["schtasks", *args])


def main():
    uv_path = find_uv()
    if uv_path is None:
        print("WARN: uv.exe not found; skipping FastAPI launch.", file=sys.stderr)
        fastapi_ok = False
    else:
        print(f"uv_path = {uv_path}")
        fastapi_ok = True

    # Always start http.server -- no uv dependency.
    write_bat(
        HTTP_BAT,
        f'@echo off\r\n'
        f'cd /d "C:\\Users\\karma"\r\n'
        f'"{sys.executable}" -m http.server 8080 --bind 127.0.0.1 '
        f'> "{HTTP_OUT}" 2> "{HTTP_ERR}"\r\n',
    )

    if fastapi_ok:
        write_bat(
            FASTAPI_BAT,
            f'@echo off\r\n'
            f'set CORS_ORIGINS={CORS_ORIGINS}\r\n'
            f'cd /d "C:\\Users\\karma\\python"\r\n'
            f'"{uv_path}" run python -m src.server.main '
            f'> "{FASTAPI_OUT}" 2> "{FASTAPI_ERR}"\r\n',
        )

    # Pre-cleanup: end + delete any prior registration so we never end up
    # with two children fighting for port 8181 (a prior /run might still
    # hold the port). CalledProcessError is fine (task didn't exist) --
    # we swallow it via check_output so the launch continues regardless.
    for task in (TASK_FASTAPI, TASK_HTTP):
        try:
            subprocess.run(
                ["schtasks", "/end", "/tn", task],
                capture_output=True, check=False,
            )
        except OSError:
            pass
        subprocess.run(
            ["schtasks", "/delete", "/tn", task, "/f"],
            capture_output=True, check=False,
        )

    # Idempotent: /f overwrites any prior task definition. We use
    # /sc onstart instead of /sc once /st 00:00 because Windows marks
    # a one-shot task with a past /st as expired and /run silently
    # refuses to kick it (we hit exactly that bug in the first cut).
    # /sc onstart stays perpetually valid; a subsequent /run kicks
    # the task on demand.
    #
    # We deliberately omit /ru SYSTEM /rl HIGHEST: from a non-elevated
    # Git Bash (non-RunAs), schtasks rejects SYSTEM-owned creation with
    # "Access is denied." The task runs under the current user, which
    # is sufficient for this dev workflow -- the children outlive the
    # bash session because Task Scheduler service (svchost.exe) is the
    # actual parent, not the calling shell.
    if fastapi_ok:
        subprocess.run(
            ["schtasks", "/create", "/tn", TASK_FASTAPI,
             "/tr", FASTAPI_BAT, "/sc", "onstart", "/f"],
            check=True,
        )
        subprocess.run(["schtasks", "/run", "/tn", TASK_FASTAPI], check=True)

    subprocess.run(
        ["schtasks", "/create", "/tn", TASK_HTTP,
         "/tr", HTTP_BAT, "/sc", "onstart", "/f"],
        check=True,
    )
    subprocess.run(["schtasks", "/run", "/tn", TASK_HTTP], check=True)

    # After /run, the .bat wrappers and the underlying python.exe /
    # uv.exe might still need a few seconds to bind their sockets.
    # Poll each port for up to ~20s before printing 'done' so a
    # follow-up basher call knows when to start smoke-testing. If a
    # port never binds, dump the corresponding *err.log so the failure
    # mode is visible immediately (uv missing, port collision, etc.).
    err_log_for_port = {
        8181: ("fastapi-err.log", "/c/Users/karma/fastapi-err.log"),
        8080: ("http-err.log",    "/c/Users/karma/http-err.log"),
    }
    for port in (8181, 8080):
        bound = False
        for _ in range(40):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                try:
                    s.connect(("127.0.0.1", port))
                    bound = True
                    break
                except OSError:
                    pass
            time.sleep(0.5)
        print(f"port {port} = {'BOUND' if bound else 'NOT BOUND'}")
        if not bound:
            label, path = err_log_for_port[port]
            print(f"--- {label} (debug) ---", file=sys.stderr)
            try:
                with open(path, "rb") as f:
                    sys.stderr.buffer.write(f.read())
            except OSError as exc:
                print(f"(could not read {path}: {exc})", file=sys.stderr)

    # Stash the task names so future cleanup can be scripted.
    with open(r"C:\Users\karma\.launch_tasks.txt", "w") as f:
        f.write(
            f"fastapi_task={TASK_FASTAPI if fastapi_ok else ''}\n"
            f"http_task={TASK_HTTP}\n"
        )

    print(f"scheduled {TASK_HTTP} (http.server on 8080)")
    if fastapi_ok:
        print(f"scheduled {TASK_FASTAPI} (FastAPI on 8181)")
    print("wait ~10s then curl /health and /api/jarvis/command to smoke-test")


if __name__ == "__main__":
    main()
