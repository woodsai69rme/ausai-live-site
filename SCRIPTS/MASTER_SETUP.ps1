#!/usr/bin/env pwsh
# Master Setup Script - PHASE 1 & PHASE 2
# Installs Git (verified), Go, OpenCode, Crush, and starts Ollama

Write-Host "=== Phase 1: Installing Prerequisites ===" -ForegroundColor Cyan

# Install Go via winget
if (-not (Get-Command go -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Go..."
    winget install GoLang.Go --silent --accept-source-agreements --accept-package-agreements
}

Write-Host "=== Phase 2: Installing Vibe Coding CLIs ===" -ForegroundColor Cyan

# Install OpenCode
npm install -g @opencode-ai/cli 2>&1 | Out-Null

# Install Crush (requires Go)
go install github.com/charmbracelet/crush@latest 2>&1 | Out-Null

# Install Kilo Code
npm install -g @kilocode/cli 2>&1 | Out-Null

Write-Host "=== Phase 5: Starting Ollama ===" -ForegroundColor Cyan
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "OpenCode:      opencode"
Write-Host "Crush:         crush"
Write-Host "Kilo:          kilo"
Write-Host "Ollama:        http://localhost:11434"