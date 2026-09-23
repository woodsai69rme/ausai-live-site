"""
archon_orchestrator.py - Launch the Archon stack on bare Windows.

This script is invoked by START_ARCHON_STACK.bat. It does NOT kill any
running processes (that would self-terminate the interpreter); the caller
MUST free ports 8051/8052/8181 first via STOP_ARCHON_STACK.bat.

Sequence:
  1. archon-server :8181   (FastAPI on socket_app wrapper)
  2. MCP          :8051   (FastMCP SSE)
  3. agents       :8052   (PydanticAI agents; needs archon-server for
                            credentials, so launched last)

Each service is spawned with `python -u` (unbuffered) via the venv's
python.exe. stdout/stderr are routed to dedicated log files using
low-level os.open()/os.close() so file handles don't leak across
restarts (Windows file handle budget is real). Env vars fall back to
known-good bare-Windows defaults (fake Supabase credentials suffice
for /health; the credential handshake to /internal/credentials/agents
will 500 without real Supabase but the catch-all 500 handler preserves
process stability).

Popen flags:
  creationflags=CREATE_NO_WINDOW (same as start_offline_services.py)
  stdin=subprocess.DEVNULL  (avoid interactive prompts on Windows)

Verification:
  - socket.connect_ex() polling per port (listener up = ready)
  - urllib.request smoke test on /health, /internal/health, /
  - poll agents err log for "Successfully fetched N credentials" up to 30s
"""

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

# --- Configuration --------------------------------------------------------

VENV_PYTHON = r"C:\Users\karma\python\.venv\Scripts\python.exe"
VENV_PYTHONW = r"C:\Users\karma\python\.venv\Scripts\pythonw.exe"
PROJECT_ROOT = r"C:\Users\karma\python"
LOG_DIR = r"C:\Users\karma"

# Bare-Windows fallback defaults. Applied to the child env with setdefault()
# semantics (see _build_child_env), so any value already in the caller's
# process env wins. Production callers can export SUPABASE_URL/SERVICE_KEY
# in their shell and the fake defaults below will NOT overwrite them.
BASE_ENV_DEFAULTS = {
    "ARCHON_SERVER_PORT": "8181",
    "ARCHON_MCP_PORT": "8051",
    "ARCHON_AGENTS_PORT": "8052",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_SERVICE_KEY": "test-key-fake-for-bare-windows",
    "LOG_LEVEL": "INFO",
    "PROJECTS_ENABLED": "true",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
    "PYTHONUNBUFFERED": "1",
    # Disable bytecode cache writes. Stale __pycache__ causes Python to
    # execute pre-edit bytecode even after source files change (we hit
    # this exact symptom: server.py was updated but server.cpython-313.pyc
    # was still the dict-based deps version). Source-only execution on
    # launches trades a slightly slower startup (re-parse from .py) for
    # correctness during dev. Override by unsetting if you need cached
    # launch speed in CI.
    "PYTHONDONTWRITEBYTECODE": "1",
    "VIRTUAL_ENV": r"C:\Users\karma\python\.venv",
    # System HTTP proxy breaks loopback + Supabase/OpenRouter on Windows.
    "NO_PROXY": "localhost,127.0.0.1,.supabase.co,supabase.co,openrouter.ai,.openrouter.ai",
    "no_proxy": "localhost,127.0.0.1,.supabase.co,supabase.co,openrouter.ai,.openrouter.ai",
}

# (tag, module, log_name, port, env_extra)
SERVICES = [
    ("SRV",  "src.server.main",    "archon_server", 8181, {}),
    ("MCP",  "src.mcp.mcp_server", "mcp_server",    8051, {}),
    ("AGNT", "src.agents.server",  "agents_server", 8052, {"ARCHON_SERVER_HOST": "127.0.0.1"}),
]

CREATE_NO_WINDOW = 0x08000000

# --- Helpers --------------------------------------------------------------

def port_bound(port: int, timeout_s: int = 45) -> bool:
    """Poll a TCP port. Returns True once something is listening, or False on timeout."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    return True
        except OSError:
            pass
        time.sleep(0.5)
    return False


def _load_project_dotenv() -> dict[str, str]:
    """Parse python/.env into a dict (no dependency on dotenv in orchestrator)."""
    dotenv_path = os.path.join(PROJECT_ROOT, ".env")
    values: dict[str, str] = {}
    try:
        with open(dotenv_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                values[key.strip()] = val.strip().strip("\"'")
    except FileNotFoundError:
        pass
    return values


def _build_child_env(env_extra: dict) -> dict[str, str]:
    """Compose child env from process env + python/.env + fallback defaults + overrides.

    Order of precedence (highest wins):
      1. env_extra (e.g. ARCHON_SERVER_HOST=127.0.0.1 for agents)
      2. process env (caller shell exports)
      3. python/.env (project credentials)
      4. BASE_ENV_DEFAULTS (bare-Windows safe fallback)

    `setdefault` for step 4 preserves real credentials from steps 2–3.
    """
    env = os.environ.copy()
    for key, val in _load_project_dotenv().items():
        env.setdefault(key, val)
    for key, fallback in BASE_ENV_DEFAULTS.items():
        env.setdefault(key, fallback)
    env.update(env_extra)
    return env


def spawn_service(tag: str, module: str, log_name: str, env_extra: dict) -> int:
    """Spawn one Archon service — same bare Popen pattern as start_offline_services.

    Do not redirect stdout/stderr to parent-owned file handles; that was
    correlated with children dying shortly after orchestrator exit on Windows.
    Service logs still land in archon_server.err etc. via uvicorn/logging when
    the process cwd is PROJECT_ROOT (relative log targets in app config).
    """
    env = _build_child_env(env_extra)
    launcher = VENV_PYTHONW if os.path.isfile(VENV_PYTHONW) else VENV_PYTHON
    proc = subprocess.Popen(
        [launcher, "-u", "-m", module],
        cwd=PROJECT_ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
        creationflags=CREATE_NO_WINDOW,
    )
    print(f"  SPAWN {tag:4}  PID {proc.pid:6}  module={module}")
    return proc.pid


def wait_for_log(log_name: str, needle: str, timeout_s: int = 60) -> bool:
    """Poll the .err log of a service until a substring appears (or timeout)."""
    err_path = os.path.join(LOG_DIR, f"{log_name}.err")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with open(err_path, "r", encoding="utf-8", errors="replace") as f:
                txt = f.read()
            if needle in txt:
                return True
        except FileNotFoundError:
            pass
        time.sleep(0.5)
    return False


def smoke(url: str, label: str, timeout_s: int = 10) -> None:
    """One-shot HTTP smoke probe. Prints OK/HE/ER and a body excerpt."""
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as r:
            body = r.read().decode("utf-8", errors="replace")[:200]
            print(f"  OK  {label:30} HTTP {r.status}  {body}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        # 4xx/5xx are still useful signal — not an exception.
        print(f"  HE  {label:30} HTTP {e.code}  {body}")
    except Exception as e:
        print(f"  ER  {label:30} {type(e).__name__}: {str(e)[:120]}")


# --- Main -----------------------------------------------------------------

def _supabase_host_resolves() -> tuple[bool, str]:
    """Return (ok, host) for the SUPABASE_URL loaded from python/.env."""
    from urllib.parse import urlparse

    url = _load_project_dotenv().get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
    host = urlparse(url).hostname or ""
    if not host or host == "test.supabase.co":
        return False, host or "(unset)"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            socket.getaddrinfo(host, 443)
        return True, host
    except OSError:
        return False, host


def main() -> int:
    print("=" * 70)
    print("  Archon Stack Orchestrator (bare Windows)")
    print(f"  venv: {VENV_PYTHON}")
    print(f"  cwd:  {PROJECT_ROOT}")
    print("=" * 70)

    supa_ok, supa_host = _supabase_host_resolves()
    if supa_ok:
        print(f"  Supabase DNS: OK ({supa_host})")
    else:
        print(f"  Supabase DNS: FAIL ({supa_host})")
        print("  Knowledge uploads and RAG will not persist until python/.env has a live project.")

    pids: dict[str, int] = {}
    for tag, module, log_name, port, env_extra in SERVICES:
        print(f"\n=== Spawn {tag} -> port {port} ===")
        pids[tag] = spawn_service(tag, module, log_name, env_extra)
        # SRV imports heavy search/supabase deps; cold start can exceed 90s under load.
        bind_timeout = 240 if tag == "SRV" else 60
        if not port_bound(port, timeout_s=bind_timeout):
            print(f"  FAIL: port {port} not bound within {bind_timeout}s for {tag}")
            print(f"  Last 30 lines of {log_name}.err:")
            err_path = os.path.join(LOG_DIR, f"{log_name}.err")
            try:
                with open(err_path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                    for line in lines[-30:]:
                        print(f"    {line.rstrip()}")
            except FileNotFoundError:
                print(f"    (log not found: {err_path})")
            return 1
        print(f"  OK: port {port} bound.")

    # Agents-specific: poll for credential fetch success against archon-server.
    print("\n=== Polling agents for credential handshake (up to 30s) ===")
    if wait_for_log("agents_server", "Successfully fetched", timeout_s=30):
        print("  OK: agents fetched credentials from archon-server.")
    else:
        # 500 from /internal/credentials/agents is expected when Supabase
        # credentials are fake; agents falls back to defaults from
        # credential_service.get_credential(..., default=...).
        print("  WARN: 'Successfully fetched' line not seen; agents may be")
        print("        in degraded mode using defaults. Check stderr log.")

    print("\n=== Smoke ===")
    smoke("http://127.0.0.1:8181/health", "archon-server /health")
    smoke("http://127.0.0.1:8181/internal/health", "archon-server /internal/health")
    smoke("http://127.0.0.1:8181/", "archon-server /")
    smoke("http://127.0.0.1:8052/health", "agents /health")
    smoke("http://127.0.0.1:8052/agents/list", "agents /agents/list")

    print("\n=== Summary ===")
    for tag, pid in pids.items():
        print(f"  {tag}: PID {pid}")
    print("\nArchon stack started. Logs: C:\\Users\\karma\\*.err / *.out")
    print("Stop with: STOP_ARCHON_STACK.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
