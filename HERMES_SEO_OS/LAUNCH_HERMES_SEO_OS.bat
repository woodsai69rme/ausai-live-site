@echo off
setlocal EnableExtensions
title Hermes SEO OS — Julian Goldie style
cd /d C:\Users\karma
set PY=C:\Program Files\Python313\python.exe
if not exist "%PY%" set PY=python

:MENU
cls
echo ==============================================================
echo   HERMES SEO OS  (Julian Goldie–style agent SEO system)
echo   Local-first: Ollama + OpenRouter free + Hermes + OpenClaw
echo ==============================================================
echo.
echo   [1] Run pipeline — type a keyword
echo   [2] Run pipeline — seed from keyword bank (pick index)
echo   [3] List outbox drafts
echo   [4] Dry-run (no LLM)
echo   [5] Open SEO OS portal (HTML)
echo   [6] Open Portal War Room
echo   [7] Open brand memory + swarm docs
echo   [8] Start Hermes CLI (hermes-agent)
echo   [9] Open AusAI live site
echo   [0] Exit
echo.
set /p C="Pick: "

if "%C%"=="0" exit /b 0
if "%C%"=="1" goto KW
if "%C%"=="2" goto BANK
if "%C%"=="3" goto LIST
if "%C%"=="4" goto DRY
if "%C%"=="5" goto PORTAL
if "%C%"=="6" goto WAR
if "%C%"=="7" goto DOCS
if "%C%"=="8" goto HERMES
if "%C%"=="9" goto SITE
goto MENU

:KW
set /p KW="Keyword: "
"%PY%" "HERMES_SEO_OS\pipeline\seo_pipeline.py" --keyword "%KW%"
explorer "HERMES_SEO_OS\outbox"
pause
goto MENU

:BANK
"%PY%" -c "import json; b=json.load(open(r'HERMES_SEO_OS\memory\KEYWORD_BANK.json',encoding='utf-8')); [print(i, x['kw']) for i,x in enumerate(b.get('seed_keywords',[]))]"
set /p IDX="Index: "
"%PY%" "HERMES_SEO_OS\pipeline\seo_pipeline.py" --from-bank %IDX%
explorer "HERMES_SEO_OS\outbox"
pause
goto MENU

:LIST
"%PY%" "HERMES_SEO_OS\pipeline\seo_pipeline.py" --list-outbox
pause
goto MENU

:DRY
"%PY%" "HERMES_SEO_OS\pipeline\seo_pipeline.py" --keyword "test dry run" --dry-run
pause
goto MENU

:PORTAL
start "" "HERMES_SEO_OS\HERMES_SEO_OS.html"
goto MENU

:WAR
if exist "OPEN_PORTAL_WAR_ROOM.bat" call "OPEN_PORTAL_WAR_ROOM.bat"
goto MENU

:DOCS
start "" notepad "HERMES_SEO_OS\agents\SWARM.md"
start "" notepad "HERMES_SEO_OS\memory\BRAND_VOICE.md"
start "" notepad "HERMES_SEO_OS\README.md"
goto MENU

:HERMES
cd /d C:\Users\karma\hermes-agent
"%PY%" hermes
cd /d C:\Users\karma
pause
goto MENU

:SITE
start "" "https://ausailive.vercel.app/"
goto MENU
