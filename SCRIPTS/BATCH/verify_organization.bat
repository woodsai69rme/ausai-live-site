@echo off
REM Verification script for the new organization structure
REM This script checks if the organization was successful

echo Verifying organization of C:\Users\karma directory...

REM Check if main directories exist in C:\Users\karma
if exist "CONFIG" (
    echo ✓ CONFIG directory exists
) else (
    echo ✗ CONFIG directory missing
)

if exist "PROJECTS" (
    echo ✓ PROJECTS directory exists
) else (
    echo ✗ PROJECTS directory missing
)

if exist "TOOLS" (
    echo ✓ TOOLS directory exists
) else (
    echo ✗ TOOLS directory missing
)

if exist "DOCUMENTATION" (
    echo ✓ DOCUMENTATION directory exists
) else (
    echo ✗ DOCUMENTATION directory missing
)

if exist "AI_TOOLS" (
    echo ✓ AI_TOOLS directory exists
) else (
    echo ✗ AI_TOOLS directory missing
)

if exist "SCRIPTS" (
    echo ✓ SCRIPTS directory exists
) else (
    echo ✗ SCRIPTS directory missing
)

if exist "MEDIA" (
    echo ✓ MEDIA directory exists
) else (
    echo ✗ MEDIA directory missing
)

if exist "TEMP" (
    echo ✓ TEMP directory exists
) else (
    echo ✗ TEMP directory missing
)

if exist "PERSONAL" (
    echo ✓ PERSONAL directory exists
) else (
    echo ✗ PERSONAL directory missing
)

echo.
echo Verifying organization of X: drive...

REM Change to X: drive and check directories
X: 2>nul
if errorlevel 1 (
    echo Unable to access X: drive for verification
) else (
    if exist "AI_MODELS\LMSTUDIO_MODELS" (
        echo ✓ AI_MODELS\LMSTUDIO_MODELS directory exists
    ) else (
        echo ✗ AI_MODELS\LMSTUDIO_MODELS directory missing
    )

    if exist "AI_MODELS\OLLAMA_MODELS" (
        echo ✓ AI_MODELS\OLLAMA_MODELS directory exists
    ) else (
        echo ✗ AI_MODELS\OLLAMA_MODELS directory missing
    )

    if exist "DEVELOPMENT\ACTIVE_PROJECTS" (
        echo ✓ DEVELOPMENT\ACTIVE_PROJECTS directory exists
    ) else (
        echo ✗ DEVELOPMENT\ACTIVE_PROJECTS directory missing
    )

    if exist "CONTENT_CREATION\DOCUMENTS" (
        echo ✓ CONTENT_CREATION\DOCUMENTS directory exists
    ) else (
        echo ✗ CONTENT_CREATION\DOCUMENTS directory missing
    )

    if exist "TOOLS\AUTOMATION" (
        echo ✓ TOOLS\AUTOMATION directory exists
    ) else (
        echo ✗ TOOLS\AUTOMATION directory missing
    )

    if exist "VIRTUAL_MACHINES" (
        echo ✓ VIRTUAL_MACHINES directory exists
    ) else (
        echo ✗ VIRTUAL_MACHINES directory missing
    )

    if exist "ARCHIVES" (
        echo ✓ ARCHIVES directory exists
    ) else (
        echo ✗ ARCHIVES directory missing
    )
    
    echo.
    echo X: drive verification complete.
)

echo.
echo Verification complete. Please review the results above.
echo Check for any directories marked with ✗ and address them as needed.
echo Also manually verify that important files were moved correctly.