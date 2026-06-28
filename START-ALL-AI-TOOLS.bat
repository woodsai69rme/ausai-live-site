@echo off
title All AI Tools - Menu Launcher v2
color 0A
:menu
cls
echo ================================================================
echo     ALL AI TOOLS QUICK LAUNCHER - ZERO-HUMAN COMMAND CENTER
echo     Updated: 2026-06-26 | Dashboard: http://localhost:3142
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
echo === DASHBOARD ===
echo 13. Launch God-Mode Dashboard (Port 3142)
echo 14. List all models
echo 15. List all skills
echo 16. Open documentation
echo  h. Help / tips
echo  0. Exit
echo.

set /p choice="Enter choice (0-16, h): "
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
echo h     : Show this help
echo 0     : Exit
echo.
echo Press Enter to return to menu...
pause >nul
goto menu

