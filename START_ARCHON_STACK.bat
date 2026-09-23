@echo off
REM ============================================================
REM  START_ARCHON_STACK.bat
REM  Brings up the three Archon services on bare Windows:
REM    - archon-server :8181  (FastAPI + Socket.IO wrapper)
REM    - MCP          :8051  (FastMCP SSE)
REM    - agents       :8052  (PydanticAI; pulls creds from archon-server)
REM
REM  Procedure:
REM    1. Call STOP_ARCHON_STACK.bat (safe even if nothing is running)
REM       so we have a clean slate (no orphan python.exe holding ports).
REM       -- Note: STOP cannot run as a sub-process from inside this .bat
REM          because it taskkills python.exe; if our shell already
REM          echoes through python that would self-terminate. So we
REM          invoke it as a separate cmd invocation.
REM    2. Run archon_orchestrator.py (a clean Python script that does
REM       NOT call taskkill) to spawn each service in order with
REM       port-bind polling for readiness.
REM
REM  Logs land in C:\Users\karma\*.err and C:\Users\karma\*.out:
REM    - archon_server.out / .err
REM    - mcp_server.out    / .err
REM    - agents_server.out / .err
REM
REM  Pre-requisites (the user must have run these once already):
REM    - uv sync (or pip install -e .) inside C:\Users\karma\python\
REM    - .env file OR fall back to fake Supabase credentials (the
REM      orchestrator bakes in SUPABASE_URL/SUPABASE_SERVICE_KEY
REM      defaults good enough for /health and most read endpoints)
REM ============================================================

setlocal

echo === START_ARCHON_STACK: phase 1 (clean slate) ===
call "%~dp0STOP_ARCHON_STACK.bat"
if errorlevel 1 (
    echo WARNING: STOP returned non-zero. Continuing anyway.
)

echo.
echo === START_ARCHON_STACK: phase 2 (spawn orchestrator) ===
echo Using Python from venv at C:\Users\karma\python\.venv\Scripts\python.exe
"C:\Users\karma\python\.venv\Scripts\python.exe" -u "C:\Users\karma\archon_orchestrator.py"
set RC=%ERRORLEVEL%

echo.
if %RC% NEQ 0 (
    echo FAILURE: orchestrator exited with code %RC%. Inspect *.err logs.
) else (
    echo SUCCESS: stack is up.
    echo   - archon-server :8181
    echo   - MCP          :8051
    echo   - agents       :8052
    echo.
    echo Tail logs in another shell with:
    echo   powershell Get-Content C:\Users\karma\archon_server.err -Wait
    echo.
    echo Stop with: STOP_ARCHON_STACK.bat
)

endlocal & exit /b %RC%
