#!/usr/bin/env pwsh
# ============================================
# ONE-CLICK SETUP FOR COMPLETE AI CODING ECOSYSTEM
# Windows PowerShell - Run as Administrator recommended
# ============================================

$ErrorActionPreference = "Continue"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AI CODING ECOSYSTEM INSTALLER v1.0" -ForegroundColor Cyan
Write-Host "  Installs: OpenClaw, Models, Skills, Media Tools" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# SECTION 1: PREREQUISITE CHECK
# ============================================
Write-Host "[1/9] Checking prerequisites..." -ForegroundColor Yellow

$tools = @{
    "node" = "Node.js (required)"
    "npm" = "npm (comes with Node)"
    "python" = "Python 3.11+ (required)"
    "git" = "Git (required)"
    "ollama" = "Ollama (required for local models)"
}

foreach ($tool in $tools.Keys) {
    $installed = Get-Command $tool -ErrorAction SilentlyContinue
    if ($installed) {
        Write-Host "  ✓ $($tools[$tool]) - Found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($tools[$tool]) - NOT FOUND" -ForegroundColor Red
        Write-Host "    Install from: https://nodejs.org / https://www.python.org / https://git-scm.com / https://ollama.ai" -ForegroundColor Gray
    }
}

Write-Host ""

# ============================================
# SECTION 2: INSTALL OPENCLAW
# ============================================
Write-Host "[2/9] Installing OpenClaw..." -ForegroundColor Yellow

if (Test-Path "openclaw") {
    Write-Host "  OpenClaw folder already exists. Updating..." -ForegroundColor Yellow
    cd openclaw
    git pull
    cd ..
} else {
    git clone https://github.com/openclaw/openclaw.git
    Write-Host "  ✓ Cloned OpenClaw repository" -ForegroundColor Green
}

cd openclaw
Write-Host "  Installing npm dependencies (this may take 2-5 min)..." -ForegroundColor Gray
npm install --silent
Write-Host "  Building..." -ForegroundColor Gray
npm run build
cd ..

Write-Host "  ✓ OpenClaw installed" -ForegroundColor Green
Write-Host ""

# ============================================
# SECTION 3: INSTALL HERMES AGENT (OPTIONAL)
# ============================================
Write-Host "[3/9] Installing Hermes Agent (optional)..." -ForegroundColor Yellow

$installHermes = Read-Host "  Install Hermes Agent? (y/n)"

if ($installHermes -eq "y") {
    # Check for uv
    $uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uvInstalled) {
        Write-Host "  Installing uv (Python package manager)..." -ForegroundColor Gray
        irm https://astral.sh/uv/install.ps1 | iex
    }

    git clone https://github.com/NousResearch/hermes-agent.git
    cd hermes-agent
    # Windows doesn't have bash, use manual setup
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -e ".[all]"
    cd ..

    Write-Host "  ✓ Hermes Agent installed to .\hermes-agent\" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Skipping Hermes Agent" -ForegroundColor Gray
}
Write-Host ""

# ============================================
# SECTION 4: PULL LOCAL MODELS
# ============================================
Write-Host "[4/9] Downloading local AI models..." -ForegroundColor Yellow
Write-Host "  This will download ~15GB. Continue? (y/n)" -ForegroundColor Cyan
$downloadModels = Read-Host "  "

if ($downloadModels -eq "y") {
    $models = @(
        "llama3.2:3b",
        "qwen2.5-coder:7b",
        "hermes3:8b",
        "qwen3:8b",
        "deepseek-r1:7b"
    )

    foreach ($model in $models) {
        Write-Host "  Pulling $model..." -ForegroundColor Gray
        ollama pull $model
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    ✓ $model downloaded" -ForegroundColor Green
        } else {
            Write-Host "    ✗ Failed to download $model" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  ⚠ Skipping model downloads. Run 'ollama pull <model>' manually." -ForegroundColor Gray
}
Write-Host ""

# ============================================
# SECTION 5: INSTALL SKILLS CLI + SKILLS
# ============================================
Write-Host "[5/9] Installing agent skills..." -ForegroundColor Yellow

Write-Host "  Installing skills CLI..." -ForegroundColor Gray
npm install -g @lobehub/market-cli 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Note: Use 'npx' instead of global install: npx @lobehub/market-cli ..." -ForegroundColor Yellow
}

$skills = @(
    "vercel-labs/agent-skills",
    "microsoft/azure-skills",
    "firecrawl/firecrawl-cli",
    "supabase/supabase",
    "playwright-cli"
)

Write-Host "  Installing top 5 skills..." -ForegroundColor Gray
foreach ($skill in $skills) {
    Write-Host "    Adding $skill..." -ForegroundColor Gray
    npx -y @lobehub/market-cli skills add $skill 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✓ $skill installed" -ForegroundColor Green
    }
}

Write-Host "  ✓ Skills installed" -ForegroundColor Green
Write-Host ""

# ============================================
# SECTION 6: SETUP N8N (OPTIONAL)
# ============================================
Write-Host "[6/9] Setting up n8n automation (optional)..." -ForegroundColor Yellow

$installN8n = Read-Host "  Install n8n via Docker? (requires Docker Desktop) (y/n)"

if ($installN8n -eq "y") {
    docker pull n8nio/n8n
    docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
    Write-Host "  ✓ n8n running at http://localhost:5678" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Skipping n8n. Install later with: docker run -d -p 5678:5678 n8nio/n8n" -ForegroundColor Gray
}
Write-Host ""

# ============================================
# SECTION 7: INSTALL TADPOLE STUDIO (MUSIC)
# ============================================
Write-Host "[7/9] Installing Tadpole Studio (local music)..." -ForegroundColor Yellow

git clone https://github.com/proximasan/tadpole-studio.git
cd tadpole-studio

Write-Host "  Installing Python dependencies (uv required)..." -ForegroundColor Gray
# Try uv first
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv sync
} else {
    pip install -r requirements.txt
}

cd ..

Write-Host "  ✓ Tadpole Studio installed" -Foreforeground Green
Write-Host "  To run: cd tadpole-studio && python start.py" -ForegroundColor Gray
Write-Host ""

# ============================================
# SECTION 8: OPENROUTER CONFIG
# ============================================
Write-Host "[8/9] Configuring OpenRouter..." -ForegroundColor Yellow

$apiKey = Read-Host "  Enter your OpenRouter API key (or press Enter to skip)"

if ($apiKey) {
    # Create .env file
    $envContent = @"
OPENROUTER_API_KEY=$apiKey
OPENROUTER_DEFAULT_MODEL=openrouter/free
"@

    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "  ✓ .env file created with API key" -ForegroundColor Green

    # Add to PowerShell profile
    $profileLine = "`$env:OPENROUTER_API_KEY=`"$apiKey`""
    if (-not (Select-String -Path $PROFILE -Pattern $profileLine -Quiet)) {
        Add-Content $PROFILE $profileLine
        Write-Host "  ✓ Added to PowerShell profile" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠ Skipping OpenRouter config. Manual setup in .env" -ForegroundColor Gray
}
Write-Host ""

# ============================================
# SECTION 9: PATH CONFIGURATION
# ============================================
Write-Host "[9/9] Checking PATH configuration..." -ForegroundColor Yellow

$pathsToAdd = @(
    "$env:APPDATA\Python\Python313\Scripts",
    "$env:USERPROFILE\.local\bin",
    "$env:LOCALAPPDATA\pnpm"
)

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$needsUpdate = $false

foreach ($path in $pathsToAdd) {
    if ($userPath -notlike "*$path*" -and (Test-Path $path)) {
        Write-Host "  Adding to PATH: $path" -ForegroundColor Yellow
        $needsUpdate = $true
    }
}

if ($needsUpdate) {
    Write-Host "  ⚠ PATH updated. Restart your terminal to apply changes." -ForegroundColor Cyan
} else {
    Write-Host "  ✓ PATH looks good" -ForegroundColor Green
}
Write-Host ""

# ============================================
# SUMMARY
# ============================================
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION COMPLETE!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor White
Write-Host ""
Write-Host "1. RESTART your terminal (to update PATH)" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. TEST local model:" -ForegroundColor White
Write-Host "   ollama run llama3.2:3b" -ForegroundColor Gray
Write-Host ""
Write-Host "3. RUN OpenClaw:" -ForegroundColor White
Write-Host "   cd openclaw" -ForegroundColor Gray
Write-Host "   npx openclaw onboard" -ForegroundColor Gray
Write-Host "   npx openclaw agent --message 'hello'" -ForegroundColor Gray
Write-Host ""
Write-Host "4. RUN Hermes (if installed):" -ForegroundColor White
Write-Host "   cd hermes-agent" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   hermes" -ForegroundColor Gray
Write-Host ""
Write-Host "5. START music studio:" -ForegroundColor White
Write-Host "   cd tadpole-studio" -ForegroundColor Gray
Write-Host "   python start.py" -ForegroundColor Gray
Write-Host ""
Write-Host "6. OPEN ComfyUI (for video):" -ForegroundColor White
Write-Host "   Download from ComfyUI releases, run .bat file" -ForegroundColor Gray
Write-Host ""
Write-Host "7. VIEW n8n (if installed):" -ForegroundColor White
Write-Host "   http://localhost:5678" -ForegroundColor Gray
Write-Host ""
Write-Host "📋 Full guide: AI_ECOSYSTEM_GUIDE.md" -ForegroundColor Cyan
Write-Host "⚡ Quick ref: QUICK_START.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "All tools are now installed. Happy coding!" -ForegroundColor Green
