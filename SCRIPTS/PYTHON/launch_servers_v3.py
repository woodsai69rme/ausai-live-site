"""launch_servers_v3.py - pure-Python detached Popen attempt.

The v2 path (Windows Task Scheduler) hit an ACL block: schtasks /create
returns Access Denied (rc=5) even via cmd.exe /c from non-elevated
Git Bash. This v3 returns to pure Python: spawn both servers with
DETACHED_PROCESS | CREATE_NO_WINDOW, KEEP THE FILE HANDLES ALIVE past
Popen() (the v1 attempt used `with open(...) as out:` which closed
the parent's handle before the child finished writing -- possibly the
actual root cause of the empty-log bug, not Job-Object teardown), and
explicitly close them only after /run-or-port-poll completes.

If the children survive across separate basher boundaries, this path
is preferable because it needs zero ACL elevation AND zero .bat
shells. If they don't, the wrap-up answer is the manual two-terminal
recipe.
"""
import os
import socket
import subprocess
import sys
import time

DETACHED_PROCESS = 0x00000008
CREATE_NO_WINDOW = 0x08000000

CORS_ORIGINS = (
    "http://localhost:3737,"
    "http://127.0.0.1:3737,"
    "http://localhost:8080,"
    "http://127.0.0.1:8080"
)

PORT_TO_LOG = {
    8181: ("fastapi-out.log", "fastapi-err.log"),
    8080: ("http-out.log",    "http-err.log"),
}

UV_CANDIDATES = (
    r"C:\Users\karma\.local\bin\uv.exe",
    r"C:\Users\karma\AppData\Roaming\uv\uv.exe",
    r"C:\Users\karma\AppData\Local\uv\uv.exe",
    r"C:\Program Files\uv\uv.exe",
    r"C:\ProgramData\chocolatey\bin\uv.exe",
)


def spawn(cmd, cwd, out_path, err_path, env_extra=None):
    """Popen with detached flags. Returns (pid, out_fh, err_fh).

    Critically: parent does NOT use `with open(...)`. The parent's
    file handle is kept in scope while the child runs, so the OS
    handle stays valid until the child exits.
    """
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    out_fh = open(out_path, "wb")
    err_fh = open(err_path, "wb")
    # On Windows, `close_fds=False` is the default and the parameter
    # controls HANDLE_FLAG_INHERIT, which we want here. Inheriting
    # the stdio handles into the child is what lets the child write
    # to the log files; we deliberately do NOT pass close_fds=True.
    p = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=out_fh,
        stderr=err_fh,
        stdin=subprocess.DEVNULL,
        env=env,
        creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
    )
    # When main() returns, Python's GC closes out_fh / err_fh. That
    # only releases the parent's Python-file-handle wrapper; the
    # child inherited its own dup via CreateProcess and keeps writing
    # regardless.
    return p, out_fh, err_fh


def poll(port, timeout=20.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def main():
    # Override sys.executable to the project's existing Python 3.12 venv.
    # The http.server child below resolves 'python' via this value. The
    # system Python 3.13 was reported to fail at the http.server load
    # step on this machine (see ORCHESTRATION_LEARNINGS.md Path D).
    # FastAPI is unaffected: uv run resolves its own python.
    PY312_VENV_PYTHON = r"C:\Users\karma\python\.venv\Scripts\python.exe"
    if os.path.exists(PY312_VENV_PYTHON):
        sys.executable = PY312_VENV_PYTHON
        print(f"override sys.executable -> {PY312_VENV_PYTHON}", file=sys.stderr)
        _venv_probe = subprocess.run(
            [PY312_VENV_PYTHON, "--version"],
            capture_output=True, text=True, timeout=5,
        )
        print(
            f"venv --version: {(_venv_probe.stdout or _venv_probe.stderr).strip()}",
            file=sys.stderr,
        )
    else:
        print(
            f"PY312_VENV_PYTHON missing at {PY312_VENV_PYTHON}; "
            f"falling back to sys.executable={sys.executable}",
            file=sys.stderr,
        )

    # Solve uv
    uv_candidates = [
        r"C:\Users\karma\.local\bin\uv.exe",
        r"C:\Users\karma\AppData\Roaming\uv\uv.exe",
        r"C:\Users\karma\AppData\Local\uv\uv.exe",
        r"C:\Program Files\uv\uv.exe",
        r"C:\ProgramData\chocolatey\bin\uv.exe",
    ]
    uv = next((p for p in uv_candidates if os.path.exists(p)), None)
    print(f"uv = {uv}", file=sys.stderr)

    # Spawn http.server (always)
    http_p, http_out, http_err = spawn(
        [sys.executable, "-m", "http.server", "8080", "--bind", "127.0.0.1"],
        cwd=r"C:\Users\karma",
        out_path=r"C:\Users\karma\http-out.log",
        err_path=r"C:\Users\karma\http-err.log",
    )
    print(f"http_pid = {http_p.pid}", file=sys.stderr)

    # Spawn FastAPI (if uv resolved)
    fastapi_p = None
    fastapi_out = fastapi_err = None
    if uv:
        fastapi_p, fastapi_out, fastapi_err = spawn(
            [uv, "run", "python", "-m", "src.server.main"],
            cwd=r"C:\Users\karma\python",
            out_path=r"C:\Users\karma\fastapi-out.log",
            err_path=r"C:\Users\karma\fastapi-err.log",
            env_extra={"CORS_ORIGINS": CORS_ORIGINS},
        )
        print(f"fastapi_pid = {fastapi_p.pid}", file=sys.stderr)
    else:
        print("uv not found; FastAPI not started", file=sys.stderr)

    # Poll
    for port in (8181, 8080):
        bound = poll(port, timeout=20.0)
        print(f"port {port} = {'BOUND' if bound else 'NOT BOUND'}")
        if not bound:
            out_name, err_name = PORT_TO_LOG[port]
            for label, path in (("out", f"C:\\Users\\karma\\{out_name}"),
                                ("err", f"C:\\Users\\karma\\{err_name}")):
                print(f"--- {err_name} ({label}) ---", file=sys.stderr)
                try:
                    with open(path, "rb") as f:
                        sys.stderr.buffer.write(f.read())
                except OSError as exc:
                    print(f"(could not read {path}: {exc})", file=sys.stderr)

    # Write pids file then EXIT -- close_fds=True on parent exit will NOT
    # close our handles (we never set that on the children). The children
    # retain their own dup'd fds.
    with open(r"C:\Users\karma\.launch_pids.txt", "w") as f:
        f.write(f"fastapi_pid={fastapi_p.pid if fastapi_p else ''}\n"
                f"http_pid={http_p.pid}\n")
    print("launch_servers_v3 returned ok -- children should survive")


if __name__ == "__main__":
    main()
