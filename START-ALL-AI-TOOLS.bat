@echo off
title All AI Tools - Menu Launcher v2
color 0A
:menu
cls
echo ================================================================
echo     ALL AI TOOLS QUICK LAUNCHER - ZERO-HUMAN COMMAND CENTER
echo     Updated: 2026-06-29 | Dashboard: http://localhost:3142
echo ================================================================
echo.
echo === AI CODING TOOLS ===
echo  1. Kilo AI v7.3.54 (Code Generation CLI)
echo  2. OpenClaw Agent (with /steer)
echo  3. OpenCode AI
echo.
echo === LOCAL AI MODELS ===
echo  4. Ollama Chat (qwen2.5-coder - best coding)
echo  5. Ollama Chat (phi3 - fastest)
echo.
echo === AUTONOMOUS AGENTS ===
echo  6. Hermes Agent (self-improving, OpenRouter free tier)
echo  7. Agent Zero (Dynamic AI Framework)
echo  8. Oracle Agent  (RAG/Data)
echo  9. Jarvis Agent  (Coding/Sys)
echo 10. Paperclip Agt (Admin/Fops)
echo.
echo === CREATIVE TOOLS ===
echo 11. Tadpole Studio (Music)
echo 12. ComfyUI (Video/Image)
echo.
echo === UI VISION RPA (added 2026-07-28) ===
echo 22. Install UI Vision daily macro scheduler (Windows Task Scheduler)
echo.
echo === MOBILE RECOVERY (added 2026-07-09) ===
echo 21. Mobile Recovery Suite (iPhone + Android + Oppo)
echo.
echo === DASHBOARD ===
echo 13. Launch God-Mode Dashboard (Port 3142)
echo 14. List all models
echo 15. List all skills
echo 16. Open documentation
echo === ARCHON STACK (bare Windows) ===
echo 17. Start Archon Stack (8181 + 8051 + 8052)
echo 18. Stop Archon Stack
echo === ORNITH CODING MODEL ===
echo 19. Pull & test Ornith-1 9B (Ollama agentic coder)
echo === LOCAL MODEL BENCHMARK ===
echo 20. Benchmark all installed coders (fibonacci challenge)
echo  h. Help / tips
echo  0. Exit
echo.
echo  Tip: Run option 22 once to register the daily UI Vision macro task.
echo.

set /p choice="Enter choice (0-22, h): "
if "%choice%"=="" goto menu
if "%choice%"=="h" goto help
if "%choice%"=="H" goto help

if "%choice%"=="1" goto kilo
if "%choice%"=="2" goto openclaw
if "%choice%"=="3" goto opencode
if "%choice%"=="4" goto ollama_coder
if "%choice%"=="5" goto ollama_phi3
if "%choice%"=="6" goto hermes
if "%choice%"=="7" goto agent_zero
if "%choice%"=="8" goto oracle
if "%choice%"=="9" goto jarvis
if "%choice%"=="10" goto paperclip
if "%choice%"=="11" goto tadpole
if "%choice%"=="12" goto comfyui
if "%choice%"=="13" goto godmode
if "%choice%"=="14" goto models
if "%choice%"=="15" goto skills
if "%choice%"=="16" goto docs
if "%choice%"=="17" goto archon_start
if "%choice%"=="18" goto archon_stop
if "%choice%"=="19" goto ornith_install
if "%choice%"=="20" goto benchmark_codes
if "%choice%"=="21" goto recovery_suite
if "%choice%"=="22" goto uivision_scheduler
if "%choice%"=="0" exit
goto menu

:kilo
echo.
echo Launching Kilo AI v7.3.54...
kilo
goto menu

:opencode
echo.
echo Launching OpenCode AI...
opencode
goto menu

:agent_zero
echo.
echo Launching Agent Zero...
cd /d C:\Users\karma\agent-zero
python run_ui.py
cd /d C:\Users\karma
goto menu

:godmode
echo.
echo Launching God-Mode Dashboard on port 3142...
start http://localhost:3142
cd /d C:\Users\karma\ACTIVE_PROJECTS\ai-tools-suite
start cmd /k npm run dev
cd /d C:\Users\karma
goto menu

:ollama_coder
echo.
echo Starting Ollama with qwen2.5-coder (best coding model)...
echo.
ollama run qwen2.5-coder:latest
goto menu

:ollama_phi3
echo.
echo Starting Ollama with phi3 (fastest model)...
echo.
ollama run phi3:latest
goto menu

:openclaw
echo.
echo Launching OpenClaw Agent...
echo Try: /steer command mid-session
echo.
openclaw agent --agent test
goto menu

:hermes
echo.
echo Launching Hermes Agent (self-improving)...
cd /d C:\Users\karma\hermes-agent
set Path=C:\Users\karma\.local\bin;%Path%
uv run python run_agent.py
cd /d C:\Users\karma
goto menu

:tadpole
echo.
echo Starting Tadpole Studio (Music Generation)...
echo First run will download ~10GB models
echo.
cd /d C:\Users\karma\tadpole-studio
python start.py
cd /d C:\Users\karma
goto menu

:comfyui
echo.
echo Starting ComfyUI (Video/Image Generation)...
cd /d C:\Users\karma\ComfyUI
python main.py
cd /d C:\Users\karma
goto menu

:oracle
echo.
echo Launching Oracle Agent (RAG/Data persona)...
if exist "C:\Users\karma\oracle-agent" (
  echo ==============================================
  echo Oracle clone found - launching via uv run python main.py
  echo ==============================================
  cd /d C:\Users\karma\oracle-agent
  set Path=C:\Users\karma\.local\bin;%Path%
  uv run python main.py
  cd /d C:\Users\karma
) else (
  echo ==============================================
  echo Oracle agent NOT yet cloned.
  echo See: C:\Users\karma\ORACLE_JARVIS_PAPERCLIP_SETUP.md
  echo Then run: git clone ^<repo url^> C:\Users\karma\oracle-agent
  echo          cd C:\Users\karma\oracle-agent ^&^& uv sync
  echo ==============================================
)
pause
goto menu

:jarvis
echo.
echo Launching Jarvis Agent (Coding/System persona)...
if exist "C:\Users\karma\jarvis-agent" (
  echo ==============================================
  echo Jarvis clone found - launching via uv run python main.py
  echo ==============================================
  cd /d C:\Users\karma\jarvis-agent
  set Path=C:\Users\karma\.local\bin;%Path%
  uv run python main.py
  cd /d C:\Users\karma
) else (
  echo ==============================================
  echo Jarvis agent NOT yet cloned.
  echo See: C:\Users\karma\ORACLE_JARVIS_PAPERCLIP_SETUP.md
  echo Then run: git clone ^<repo url^> C:\Users\karma\jarvis-agent
  echo          cd C:\Users\karma\jarvis-agent ^&^& uv sync
  echo ==============================================
)
pause
goto menu

:paperclip
echo.
echo Launching Paperclip Agent (Admin/FileOps persona)...
if exist "C:\Users\karma\paperclip-agent" (
  echo ==============================================
  echo Paperclip clone found - launching via uv run python main.py
  echo ==============================================
  cd /d C:\Users\karma\paperclip-agent
  set Path=C:\Users\karma\.local\bin;%Path%
  uv run python main.py
  cd /d C:\Users\karma
) else (
  echo ==============================================
  echo Paperclip agent NOT yet cloned.
  echo See: C:\Users\karma\ORACLE_JARVIS_PAPERCLIP_SETUP.md
  echo Then run: git clone ^<repo url^> C:\Users\karma\paperclip-agent
  echo          cd C:\Users\karma\paperclip-agent ^&^& uv sync
  echo ==============================================
)
pause
goto menu

:models
echo.
echo Available Models:
ollama list
echo.
pause
goto menu

:skills
echo.
echo Installed Skills:
npx skills list
echo.
pause
goto menu

:docs
echo.
echo Opening documentation...
start notepad C:\Users\karma\ALL-TOOLS-CONFIGURED.md
goto menu

:archon_start
echo.
echo === Starting Archon Stack ===
echo archon-server :8181   (FastAPI + Socket.IO)
echo MCP          :8051   (FastMCP SSE)
echo agents       :8052   (PydanticAI; pulls creds from archon-server)
echo.
echo This usually takes 30-45 seconds as each service imports models and binds its port.
echo.
call "%~dp0START_ARCHON_STACK.bat"
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:archon_stop
echo.
echo === Stopping Archon Stack ===
echo Killing PIDs bound to ports :8181, :8051, :8052 ...
echo.
call "%~dp0STOP_ARCHON_STACK.bat"
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:ornith_install
echo.
echo === Pulling Ornith-1 9B via Ollama (~5.6 GB) ===
echo This is an agentic-coding-focused LLM (256K context, MIT).
echo.
ollama pull ornith:9b
if errorlevel 1 goto :ornith_upgrade_hint
echo.
echo === Smoke test: ornith:9b codegen ===
python "%~dp0ComfyUI\tools\local_ai_assistant.py" chat --model ornith:9b --prompt "Print Hello World in Python (one line)"
goto :ornith_install_done

:ornith_upgrade_hint
echo.
echo ============================================================
echo  PULL FAILED - your Ollama is too old for the Ornith-1 manifest.
echo.
echo  FIX: upgrade Ollama to the latest release:
echo    https://ollama.com/download
echo  Then re-run this menu option (19).
echo.
echo  The wired aliases (qwen, deepseek) work for models you already have:
echo    python "%~dp0ComfyUI\tools\local_ai_assistant.py" check
echo ============================================================

:ornith_install_done
echo.
pause >nul
goto menu

:benchmark_codes
echo.
echo === Benchmarking local coders with the fibonacci challenge ===
echo Each model runs the SAME prompt + is timed (wall-clock + chars/sec).
echo Results append to C:\Users\karma\benchmark_coders_results.jsonl so
echo you can diff before/after an Ollama upgrade.
echo.
python "%~dp0benchmark_coders.py" --sweep --extra-tag qwen2.5:14b --extra-tag qwen2.5:32b
echo.
pause >nul
goto menu

:recovery_suite
echo.

echo === Mobile Recovery Suite (iPhone + Android + Oppo) ===
echo Bundles: REAL pymobiledevice3/libimobiledevice (iPhone), Oppo broken-screen
echo specialist (EDL/MSM/scrcpy/fastboot), the working Android/Oppo GUI,
echo existing Dr.Fone-Alt batch menus, and the four Flask reference UIs.
echo.
echo Headline use case: data recovery / access on a phone with a broken screen.
echo See: COMPLETED_PROJECTS\mobile_backup\MOBILE_TOOLS_INDEX.md
echo.
call "%~dp0COMPLETED_PROJECTS\mobile_backup\RECOVERY_SUITE.bat"
echo.
pause >nul
goto menu

:uivision_scheduler
echo.
echo === UI Vision Daily Macro Scheduler ===
echo Registers a Windows Task Scheduler job that starts the local dashboard
echo server every day so UI Vision can run a chosen macro.
echo.
echo Available starter macros are in RPA\ui-vision\macros\
echo   Example: Read_AI_Tools_Active_Projects
echo.
set /p UIV_MACRO="Macro name [Read_AI_Tools_Active_Projects]: "
if "%UIV_MACRO%"=="" set "UIV_MACRO=Read_AI_Tools_Active_Projects"
if not exist "%~dp0RPA\ui-vision\macros\%UIV_MACRO%.json" (
    echo [ERROR] Macro not found: %~dp0RPA\ui-vision\macros\%UIV_MACRO%.json
    echo Press Enter to return to menu...
    pause >nul
    goto menu
)
echo.
echo Choose trigger time ^(24-hour HH:MM^). Press Enter for default 06:00:
set /p UIV_TIME="Time [06:00]: "
if "%UIV_TIME%"=="" set "UIV_TIME=06:00"
echo.
call "%~dp0RPA\ui-vision\install_ui_vision_scheduler.bat" %UIV_MACRO% --time %UIV_TIME% --interval 60 --timeout 300
echo.
echo Press Enter to return to menu...
pause >nul
goto menu

:help
echo.
echo === QUICK TIPS ===
echo 1-3  : Coding tools (Kilo, OpenClaw, OpenCode)
echo 4-5  : Local chat models (Ollama)
echo 6    : Hermes chat agent (OpenRouter free tier)
echo 7    : Agent Zero dynamic framework
echo 8-10 : Oracle/Jarvis/Paperclip (need clone first)
echo 11-12: Creative tools (Tadpole, ComfyUI)
echo 13   : Web dashboard on port 3142
echo 14-15: List models / skills
echo 16   : Open this documentation
echo 17   : Start Archon Stack (8181 + 8051 + 8052)
echo 18   : Stop Archon Stack
echo 19   : Pull & test Ornith-1 9B (Ollama agentic coder)
echo 20   : Benchmark installed coders (fibonacci challenge)
echo 21   : Mobile Recovery Suite (iPhone + Android + Oppo broken screen)
echo 22   : Install UI Vision daily macro scheduler (Windows Task Scheduler)
echo h     : Show this help
echo 0     : Exit
echo.
echo Press Enter to return to menu...
pause >nul
goto menu

