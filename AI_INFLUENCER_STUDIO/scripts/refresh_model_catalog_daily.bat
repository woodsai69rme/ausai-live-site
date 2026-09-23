@echo off
setlocal
rem Refresh the verified model catalog once per day; stale data is retained on provider failure.
rem Resolve aisocial via its user-site console script first (the Task Scheduler's
rem minimal environment does not include it on PATH), then fall back to PATH lookup.
set "AISOCIAL=%APPDATA%\Python\Python313\Scripts\aisocial.exe"
if not exist "%AISOCIAL%" set "AISOCIAL=aisocial"

"%AISOCIAL%" model-registry refresh --daily
exit /b %ERRORLEVEL%
