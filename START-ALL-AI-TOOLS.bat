@echo off
title All AI Tools - Menu Launcher
color 0A
cls
echo ========================================
echo   ALL AI TOOLS QUICK LAUNCHER
echo   Updated: 2026-06-17
echo ========================================
echo.
echo Select an option:
echo.
echo 1. Ollama Chat (qwen2.5-coder - best coding)
echo 2. Ollama Chat (phi3 - fastest)
echo 3. OpenClaw Agent (with /steer)
echo 4. Hermes Agent (self-improving)
echo 5. Tadpole Studio (Music - first run downloads models)
echo 6. ComfyUI (Video generation)
echo 7. Oracle Agent  (RAG/Data   - clone TBD; see ORACLE_JARVIS_PAPERCLIP_SETUP.md)
echo 8. Jarvis Agent  (Coding/Sys - clone TBD; see ORACLE_JARVIS_PAPERCLIP_SETUP.md)
echo 9. Paperclip Agt (Admin/Fops - clone TBD; see ORACLE_JARVIS_PAPERCLIP_SETUP.md)
echo 10. List all models
echo 11. List all skills
echo 12. Open documentation
echo 0. Exit
echo.

set /p choice="Enter choice (0-12): "

if "%choice%"=="1" goto ollama_coder
if "%choice%"=="2" goto ollama_phi3
if "%choice%"=="3" goto openclaw
if "%choice%"=="4" goto hermes
if "%choice%"=="5" goto tadpole
if "%choice%"=="6" goto comfyui
if "%choice%"=="7" goto oracle
if "%choice%"=="8" goto jarvis
if "%choice%"=="9" goto paperclip
if "%choice%"=="10" goto models
if "%choice%"=="11" goto skills
if "%choice%"=="12" goto docs
if "%choice%"=="0" exit
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
  cd C:\Users\karma
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

:menu
cls
echo ========================================
echo   ALL AI TOOLS QUICK LAUNCHER
echo   Updated: 2026-06-17
echo ========================================
echo.
echo Select an option:
echo.
echo 1. Ollama Chat (qwen2.5-coder - best coding)
echo 2. Ollama Chat (phi3 - fastest)
echo 3. OpenClaw Agent (with /steer)
echo 4. Hermes Agent (self-improving)
echo 5. Tadpole Studio (Music)
echo 6. ComfyUI (Video)
echo 7. Oracle Agent  (RAG/Data   - clone TBD; see ORACLE_JARVIS_PAPERCLIP_SETUP.md)
echo 8. Jarvis Agent  (Coding/Sys - clone TBD; see ORACLE_JARVIS_PAPERCLIP_SETUP.md)
echo 9. Paperclip Agt (Admin/Fops - clone TBD; see ORACLE_JARVIS_PAPERCLIP_SETUP.md)
echo 10. List all models
echo 11. List all skills
echo 12. Open documentation
echo 0. Exit
echo.
goto end

:end
set /p choice="Enter choice (0-12): "
if "%choice%"=="1" goto ollama_coder
if "%choice%"=="2" goto ollama_phi3
if "%choice%"=="3" goto openclaw
if "%choice%"=="4" goto hermes
if "%choice%"=="5" goto tadpole
if "%choice%"=="6" goto comfyui
if "%choice%"=="7" goto oracle
if "%choice%"=="8" goto jarvis
if "%choice%"=="9" goto paperclip
if "%choice%"=="10" goto models
if "%choice%"=="11" goto skills
if "%choice%"=="12" goto docs
if "%choice%"=="0" exit
goto end
