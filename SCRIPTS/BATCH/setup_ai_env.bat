@echo off
REM ==========================================
REM Environment Setup for AI Tools
REM Secures API Keys in Environment Variables
REM ==========================================

echo.
echo ==========================================
echo  AI TOOLS ENVIRONMENT SETUP
echo ==========================================
echo.
echo This script will help you set up environment variables
echo for your API keys to avoid storing them in plain text.
echo.

REM Check if .env file exists
if not exist "%USERPROFILE%\.ai_env" (
    echo Creating new environment file: %USERPROFILE%\.ai_env
    echo.
    echo # AI Tools Environment Variables
    echo # Created: %DATE% %TIME%
    echo # IMPORTANT: Keep this file secure!
    echo.
    echo # OpenRouter API Keys
    echo OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
    echo OPENROUTER_API_KEY_BACKUP1=sk-or-v1-YOUR_BACKUP_KEY_HERE
    echo OPENROUTER_API_KEY_BACKUP2=sk-or-v1-YOUR_BACKUP_KEY_HERE
    echo.
    echo # DashScope (Qwen) API Key
    echo DASHSCOPE_API_KEY=YOUR_DASHSCOPE_KEY_HERE
    echo.
    echo # GitHub Token
    echo GITHUB_TOKEN=ghp_YOUR_GITHUB_TOKEN_HERE
    echo.
    echo # Tavily Search API
    echo TAVILY_API_KEY=YOUR_TAVILY_KEY_HERE
    echo.
    echo # Anthropic API
    echo ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_KEY_HERE
    echo.
    echo # OpenAI API
    echo OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_HERE
    echo.
    ) > "%USERPROFILE%\.ai_env"
    echo Created: %USERPROFILE%\.ai_env
    echo.
    echo NEXT STEPS:
    echo 1. Edit %USERPROFILE%\.ai_env with your actual API keys
    echo 2. Run: setx /M PATH "%%PATH%%;%USERPROFILE%"
    echo 3. Restart your terminal for changes to take effect
    echo.
) else (
    echo Environment file already exists: %USERPROFILE%\.ai_env
    echo.
    echo To update your keys, edit: %USERPROFILE%\.ai_env
    echo.
)

REM Load environment variables for current session
echo Loading environment variables for current session...
for /f "tokens=1,* delims==" %%a in ('findstr /v "^#" "%USERPROFILE%\.ai_env" ^| findstr "="') do (
    setx "%%a" "%%b" >nul
    echo - Set: %%a
)

echo.
echo ==========================================
echo Environment setup complete!
echo ==========================================
echo.
echo IMPORTANT SECURITY NOTES:
echo 1. Never commit .ai_env to version control
echo 2. Add .ai_env to your .gitignore
echo 3. Consider using Windows Credential Manager for production
echo 4. Rotate API keys regularly
echo.
echo To verify keys are set, run: echo %OPENROUTER_API_KEY%
echo.
pause
