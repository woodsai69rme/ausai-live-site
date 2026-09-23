@echo off
echo ============================================
echo   PUSH 3 NEW GITHUB REPOS
echo   comfyui-workflow-recipes
echo   n8n-templates
echo   ai-security-checklist
echo ============================================
echo.

echo Step 1: Fix GitHub authentication...
echo If this fails, run: gh auth login
echo.
gh auth status 2>nul
if %errorlevel% neq 0 (
    echo.
    echo AUTH FAILED - Run this first: gh auth login
    echo Then re-run this script.
    pause
    exit /b 1
)

echo.
echo Step 2: Creating repo: comfyui-workflow-recipes
echo -----------------------------------------------
cd /d C:\Users\karma\comfyui-workflow-recipes
gh repo create comfyui-workflow-recipes --public --source=. --remote=origin --push
if %errorlevel% neq 0 (
    echo FAILED: comfyui-workflow-recipes
) else (
    echo SUCCESS: https://github.com/woodsai69rme/comfyui-workflow-recipes
)

echo.
echo Step 3: Creating repo: n8n-templates
echo -----------------------------------------------
cd /d C:\Users\karma\n8n-templates
gh repo create n8n-templates --public --source=. --remote=origin --push
if %errorlevel% neq 0 (
    echo FAILED: n8n-templates
) else (
    echo SUCCESS: https://github.com/woodsai69rme/n8n-templates
)

echo.
echo Step 4: Creating repo: ai-security-checklist
echo -----------------------------------------------
cd /d C:\Users\karma\ai-security-checklist
gh repo create ai-security-checklist --public --source=. --remote=origin --push
if %errorlevel% neq 0 (
    echo FAILED: ai-security-checklist
) else (
    echo SUCCESS: https://github.com/woodsai69rme/ai-security-checklist
)

echo.
echo ============================================
echo   DONE. Check the URLs above.
echo ============================================
pause
