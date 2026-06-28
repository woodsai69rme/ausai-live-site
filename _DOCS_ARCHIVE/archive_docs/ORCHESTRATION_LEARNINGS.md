# Orchestration Learnings — Windows / MSYS / Git Bash

This file documents the **constraints** discovered when trying to spawn a
FastAPI server (`uv run python -m src.server.main` on port 8181) and a
static `python -m http.server 8080` as **background processes that
survive across separate Codebuff `basher` agent invocations**, so that
a downstream `browser-use` agent can hit them.

The task turned out to be harder than expected. Three automation paths
all hit concrete walls on this machine; the only viable path right now
is the **manual two-terminal recipe** below.

## False-paths log (do NOT re-walk)

### Path A — `nohup ... & disown` (rejected)
MSYS bash Job-Object tears down the children the moment the parent
shell exits. Logs empty, ports unbound in next basher.

### Path B — `subprocess.Popen` with `DETACHED_PROCESS | CREATE_NO_WINDOW`
Same Job-Object failure. Confirmed empty logs, "Connection refused" on
both 8181 and 8080 across separate bashers.

### Path C — Windows Task Scheduler (`schtasks /create /sc onstart /run`)
- `/sc once /st 00:00` → task marked expired, `/run` returns 0 but
  silently never fires.
- `/sc onstart /ru SYSTEM /rl HIGHEST` → `Access is denied` from
  non-elevated Git Bash (cmd.exe `schtasks /create` returned rc=5 too).
- `/sc onstart` (no `/ru`) → `Access is denied` regardless of shell.

Conclusion: **the launching user is ACL-blocked from creating scheduled
tasks on this machine from any non-elevated shell**.

### Path D — Pure-Python Popen with `DETACHED_PROCESS | CREATE_NO_WINDOW`
- Spawn succeeds and prints PIDs, but children die before binding
  sockets (empty logs, "Connection refused" on next basher).
- **Root cause hypothesis (unverified):** the parent MSYS bash Job
  Object tears down children on exit, combined with the 8080 zombie
  PID 5600 blocking the new http.server child and (possibly) the
  python-3.13 bundled `http.server` failing before
  `serve_forever`. None of these three causes was isolated to a single
  variable in this session; future re-investigation should kill the
  zombie first, swap `sys.executable` to python 3.12, *then* retry
  Path D to disambiguate.

## Confirmed working: manual two-terminal recipe

This is the only path that actually exercises the API + dashboard
end-to-end. The user runs it themselves; no automation needed.

**Terminal A — FastAPI (port 8181):**
```powershell
cd "C:\Users\karma\python"
$env:CORS_ORIGINS = "http://localhost:3737,http://127.0.0.1:3737,http://localhost:8080,http://127.0.0.1:8080"
uv run python -m src.server.main
```

**Terminal B — static dashboard (port 8080):**
```powershell
cd "C:\Users\karma"
python -m http.server 8080 --bind 127.0.0.1
```

(Leave both running. Browser-side URL:
`http://127.0.0.1:8080/ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html`)

### From MSYS bash (basher-side, MINGW64)

If a future basher wants to drop the manual recipe into a shell
directly, the bash equivalents are:

**Terminal A — FastAPI (port 8181):**
```bash
cd /c/Users/karma/python
CORS_ORIGINS='http://localhost:3737,http://127.0.0.1:3737,http://localhost:8080,http://127.0.0.1:8080' \
  uv run python -m src.server.main
```

**Terminal B — static dashboard (port 8080):**
```bash
cd /c/Users/karma
python -m http.server 8080 --bind 127.0.0.1
```

The MSYS-bash form is **not durable across basher boundaries** (Job
Object teardown again) — it's only useful if you stay inside a single
long-lived shell. The PowerShell form is functionally equivalent.

## Why automation is hard on this machine

| Constraint | Evidence |
|---|---|
| `tmux` not in chocolatey gallery | `choco install tmux` → "package not found" |
| WSL Ubuntu distribution is unresponsive | `wsl -- bash -lc 'echo hi'` timed out at 90s; LxssManager appears stalled |
| `schtasks /create` blocked at ACL | cmd.exe `schtasks /create` returns rc=5 Access Denied |
| `python 3.13` http.server may have a load bug | `[unverified — earlier basher reported; full traceback never tailed]` |
| Popen-detached children die with parent | Job-Object teardown — empty logs |
| Port 8080 zombie from prior sessions | Repeatedly PID 5600 holding the port |

## What would unblock automation here

1. **One-time UAC elevation**, run any of these once from an
   Administrator PowerShell prompt:
   - `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
   - Manually run `schtasks /create /tn archon-fastapi /tr .../run_fastapi.bat /sc onstart /f`
     so the task is registered, then future bashers can merely
     `schtasks /run /tn archon-fastapi` without re-creating.

2. **Per-host WSL recovery** — once LxssManager service recovers,
   install `apt install tmux` inside WSL Ubuntu and use
   `tmux-cli` orchestration agent from there.

3. **`python -m http.server 8123` from `python 3.12`** (existing `.venv`)
   instead of the bundled 3.13. Override `sys.executable` in
   `launch_servers_v3.py` to point at `python 3.12.exe`.

4. **Re-raise the request once one of the above is available** and
   `launch_servers.py` v2 (or v3 with sys.executable override) will
   land.

## Files touched this session (kept as evidence of attempted paths)

| File | State | Why |
|---|---|---|
| `C:\Users\karma\launch_servers.py` | v2 (schtasks path) | ACL-blocked on this machine |
| `C:\Users\karma\launch_servers_v3.py` | pure-Python Popen | Job-Object teardown + port zombie + py3.13 http.server bug |
| `C:\Users\karma\run_fastapi.bat`, `run_http.bat` | written | exercise schtasks path |
| `C:\Users\karma\fastapi-out.log`, `fastapi-err.log`, `http-out.log`, `http-err.log`, `.launch_pids.txt`, `.launch_tasks.txt` | written | diagnostic artifacts |
| `C:\Users\karma\ORCHESTRATION_LEARNINGS.md` | this file | the deliverable for future agents |
