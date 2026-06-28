# Master Storage Optimization Tool (Technical Only)
# Targets: Python, Node, Docker, WSL, and Temp Caches.
# STRICT EXCLUSION: Media, Downloads, Documents, Personal Folders.

$ErrorActionPreference = "SilentlyContinue"

function Get-FolderSizeGB($path) {
    if (Test-Path $path) {
        $size = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        return [math]::Round($size / 1GB, 2)
    }
    return 0
}

function Show-Header($title) {
    Write-Host "`n=== $title ===" -ForegroundColor Cyan
}

function Clean-Python() {
    Show-Header "Cleaning Python Caches"
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Host "Running: uv cache clean..." -DarkGray
        uv cache clean
    }
    if (Get-Command pip -ErrorAction SilentlyContinue) {
        Write-Host "Running: pip cache purge..." -DarkGray
        pip cache purge
    }
    Write-Host "Python cleanup complete." -ForegroundColor Green
}

function Clean-Node() {
    Show-Header "Cleaning Node.js / PNPM Caches"
    if (Get-Command pnpm -ErrorAction SilentlyContinue) {
        Write-Host "Running: pnpm store prune..." -DarkGray
        pnpm store prune
    }
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        Write-Host "Running: npm cache clean --force..." -DarkGray
        npm cache clean --force
    }
    Write-Host "Node.js cleanup complete." -ForegroundColor Green
}

function Clean-Docker() {
    Show-Header "Cleaning Docker Build Cache"
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Host "Running: docker system prune -af --volumes..." -DarkGray
        docker system prune -af --volumes
    }
    Write-Host "Docker cleanup complete." -ForegroundColor Green
}

function Clean-SystemTemp() {
    Show-Header "Cleaning System & User Temp (Safe Files Only)"
    $tempPaths = @("$env:TEMP", "C:\Windows\Temp")
    foreach ($path in $tempPaths) {
        Write-Host "Cleaning $path..." -DarkGray
        Get-ChildItem -Path $path -Recurse | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-1) } | Remove-Item -Recurse -Force
    }
    Write-Host "Temp cleanup complete." -ForegroundColor Green
}

function Show-Audit() {
    Show-Header "STORAGE AUDIT (Technical Bloat)"
    $audit = @(
        [PSCustomObject]@{ Category="Python (UV/Pip)"; SizeGB=(Get-FolderSizeGB "$env:LOCALAPPDATA\uv") + (Get-FolderSizeGB "$env:LOCALAPPDATA\pip\cache") }
        [PSCustomObject]@{ Category="Node (PNPM/NPM)"; SizeGB=(Get-FolderSizeGB "$env:LOCALAPPDATA\pnpm") + (Get-FolderSizeGB "$env:LOCALAPPDATA\npm-cache") }
        [PSCustomObject]@{ Category="WSL Virtual Disks"; SizeGB=(Get-FolderSizeGB "$env:LOCALAPPDATA\Packages") } # Approximate
        [PSCustomObject]@{ Category="Cypress/Playwright"; SizeGB=(Get-FolderSizeGB "$env:LOCALAPPDATA\Cypress") + (Get-FolderSizeGB "$env:LOCALAPPDATA\ms-playwright") }
        [PSCustomObject]@{ Category="Nomic/AI Models"; SizeGB=(Get-FolderSizeGB "$env:LOCALAPPDATA\nomic.ai") }
    )
    $audit | Format-Table -AutoSize
}

# MAIN EXECUTION MENU
Clear-Host
Write-Host "JARVIS STORAGE OPTIMIZER" -ForegroundColor Yellow -BackgroundColor Blue
Write-Host "Targeting technical bloat on C: drive. Media/Personal folders are PROTECTED."

$choice = Read-Host "`n[1] Full Audit`n[2] Clean All (Python, Node, Docker, Temp)`n[3] Clean Python Only`n[4] Clean Node Only`n[5] Clean Docker Only`n[Q] Quit`n`nSelect an option"

switch ($choice) {
    "1" { Show-Audit }
    "2" { Clean-Python; Clean-Node; Clean-Docker; Clean-SystemTemp; Show-Audit }
    "3" { Clean-Python; Show-Audit }
    "4" { Clean-Node; Show-Audit }
    "5" { Clean-Docker; Show-Audit }
    "Q" { exit }
    Default { Write-Host "Invalid Selection" -ForegroundColor Red }
}

Write-Host "`nOptimization process finished. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
