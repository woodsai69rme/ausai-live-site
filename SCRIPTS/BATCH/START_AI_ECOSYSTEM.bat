@echo off
echo Starting Complete AI Ecosystem...
echo.

echo Launching Master Organization System...
start /min python "%USERPROFILE%\master_organization_system.py"
timeout /t 2 /nobreak >nul

echo.
echo Launching AI Army...
start /min python "%USERPROFILE%\AI_ARMY_MANAGER.py"
timeout /t 2 /nobreak >nul

echo.
echo Launching AI Voice Assistant...
start /min python "%USERPROFILE%\AI_VOICE_ASSISTANT.py"
timeout /t 2 /nobreak >nul

echo.
echo Launching Ecosystem Integrator...
start /min python "%USERPROFILE%\AI_ECOSYSTEM_INTEGRATOR.py"
timeout /t 2 /nobreak >nul

echo.
echo Opening Ecosystem Dashboard...
start "" "%USERPROFILE%\AI_ECOSYSTEM\dashboard.html"
timeout /t 3 /nobreak >nul

echo.
echo All systems launched successfully!
echo.
echo Your complete AI ecosystem is now running:
echo.  - AI Army managing tasks
echo.  - Voice Assistant listening for commands  
echo.  - Browser extension capturing chat history
echo.  - Organization system sorting all content
echo.  - Dashboard monitoring all systems
echo.
echo Press any key to exit.
pause >nul