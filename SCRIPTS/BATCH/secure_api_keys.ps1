# Security Remediation Script
# Migrates API keys from plain text configs to environment variables
# Run: powershell -ExecutionPolicy Bypass -File secure_api_keys.ps1

$ErrorActionPreference = "Stop"
$envFile = "$env:USERPROFILE\.ai_env"
$backupDir = "$env:USERPROFILE\SCRIPTS\BACKUPS\$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  API KEY SECURITY REMEDIATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Create backup directory
New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
Write-Host "[1/6] Created backup directory: $backupDir" -ForegroundColor Green

# Backup existing config files
$configFiles = @(
    "$env:USERPROFILE\.claude\claude.json",
    "$env:USERPROFILE\.continue\config.yaml",
    "$env:USERPROFILE\.qwen\settings.json"
)

foreach ($configFile in $configFiles) {
    if (Test-Path $configFile) {
        $fileName = Split-Path $configFile -Leaf
        Copy-Item -Path $configFile -Destination "$backupDir\$fileName" -Force
        Write-Host "  - Backed up: $fileName" -ForegroundColor Yellow
    }
}

# Extract API keys from Claude config
Write-Host "`n[2/6] Extracting API keys from Claude config..." -ForegroundColor Cyan
$claudeConfigPath = "$env:USERPROFILE\.claude\claude.json"

if (Test-Path $claudeConfigPath) {
    $claudeConfig = Get-Content $claudeConfigPath -Raw | ConvertFrom-Json
    
    $apiKeys = @{}
    
    if ($claudeConfig.mcpServers.openrouter.env.OPENROUTER_API_KEY) {
        $apiKeys["OPENROUTER_API_KEY"] = $claudeConfig.mcpServers.openrouter.env.OPENROUTER_API_KEY
        Write-Host "  - Found OpenRouter primary key" -ForegroundColor Green
    }
    
    if ($claudeConfig.mcpServers.'openrouter-backup1'.env.OPENROUTER_API_KEY) {
        $apiKeys["OPENROUTER_API_KEY_BACKUP1"] = $claudeConfig.mcpServers.'openrouter-backup1'.env.OPENROUTER_API_KEY
        Write-Host "  - Found OpenRouter backup1 key" -ForegroundColor Green
    }
    
    if ($claudeConfig.mcpServers.'openrouter-backup2'.env.OPENROUTER_API_KEY) {
        $apiKeys["OPENROUTER_API_KEY_BACKUP2"] = $claudeConfig.mcpServers.'openrouter-backup2'.env.OPENROUTER_API_KEY
        Write-Host "  - Found OpenRouter backup2 key" -ForegroundColor Green
    }
}

# Extract API keys from Continue config
Write-Host "`n[3/6] Extracting API keys from Continue config..." -ForegroundColor Cyan
$continueConfigPath = "$env:USERPROFILE\.continue\config.yaml"

if (Test-Path $continueConfigPath) {
    $continueContent = Get-Content $continueConfigPath -Raw
    
    # Simple regex to find OpenAI key
    if ($continueContent -match 'apiKey:\s*(sk-[a-zA-Z0-9]+)') {
        $apiKeys["OPENAI_API_KEY"] = $matches[1]
        Write-Host "  - Found OpenAI API key" -ForegroundColor Green
    }
}

# Create or update .ai_env file
Write-Host "`n[4/6] Creating/Updating .ai_env file..." -ForegroundColor Cyan

$envContent = @"
# AI Tools Environment Variables
# Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# IMPORTANT: Keep this file secure! Do not commit to version control.

"@

foreach ($key in $apiKeys.Keys) {
    $envContent += "$key=$($apiKeys[$key])`n"
    Write-Host "  - Added: $key" -ForegroundColor Green
}

# Add placeholder for other keys
$envContent += @"

# DashScope (Qwen) API Key
DASHSCOPE_API_KEY=YOUR_DASHSCOPE_KEY_HERE

# GitHub Token
GITHUB_TOKEN=ghp_YOUR_GITHUB_TOKEN_HERE

# Tavily Search API
TAVILY_API_KEY=YOUR_TAVILY_KEY_HERE

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_KEY_HERE
"@

$envContent | Out-File -FilePath $envFile -Encoding UTF8
Write-Host "  - Created: $envFile" -ForegroundColor Green

# Set environment variables for current session
Write-Host "`n[5/6] Setting environment variables for current session..." -ForegroundColor Cyan

foreach ($key in $apiKeys.Keys) {
    [Environment]::SetEnvironmentVariable($key, $apiKeys[$key], "User")
    Set-Item -Path "Env:$key" -Value $apiKeys[$key]
    Write-Host "  - Set: $key" -ForegroundColor Green
}

# Create sanitized config files
Write-Host "`n[6/6] Creating sanitized config files..." -ForegroundColor Cyan

# Sanitize Claude config
if (Test-Path $claudeConfigPath) {
    $claudeConfig = Get-Content $claudeConfigPath -Raw | ConvertFrom-Json

    # Replace API keys with environment variable references
    $claudeConfig.mcpServers.openrouter.env.OPENROUTER_API_KEY = '${OPENROUTER_API_KEY}'
    $claudeConfig.mcpServers.'openrouter-backup1'.env.OPENROUTER_API_KEY = '${OPENROUTER_API_KEY_BACKUP1}'
    $claudeConfig.mcpServers.'openrouter-backup2'.env.OPENROUTER_API_KEY = '${OPENROUTER_API_KEY_BACKUP2}'

    $claudeConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath "$backupDir\claude.json.sanitized" -Encoding UTF8
    Write-Host "  - Created sanitized claude.json" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SECURITY REMEDIATION COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "SUMMARY:" -ForegroundColor Yellow
Write-Host "  - API Keys Extracted: $($apiKeys.Count)" -ForegroundColor White
Write-Host "  - Backup Location: $backupDir" -ForegroundColor White
Write-Host "  - Environment File: $envFile" -ForegroundColor White

Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Review and manually update configs to use environment variables" -ForegroundColor White
Write-Host "  2. Delete backup files after verification (contains plain text keys)" -ForegroundColor White
Write-Host "  3. Add .ai_env to .gitignore" -ForegroundColor White
Write-Host "  4. Restart terminal for changes to take effect" -ForegroundColor White

Write-Host "`nSECURITY WARNING:" -ForegroundColor Red
Write-Host "  The backup folder contains plain text API keys!" -ForegroundColor Red
Write-Host "  Delete it after verifying the new setup works." -ForegroundColor Red

Write-Host "`n========================================`n" -ForegroundColor Cyan
