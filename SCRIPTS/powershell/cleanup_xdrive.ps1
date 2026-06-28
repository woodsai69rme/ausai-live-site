# X: Drive Cleanup Script - Free up space
# X: is 100% full (931.51GB used, 0 free)

Write-Host "=== X: DRIVE CLEANUP ===" -ForegroundColor Red
Write-Host "Current Status: FULL (0 bytes free)" -ForegroundColor Yellow

# 1. Calculate node_modules size (biggest space hog)
Write-Host "`nStep 1: Checking node_modules folders..." -ForegroundColor Cyan
$nodeModulesTotal = 0
$repoCount = 0

Get-ChildItem X:\githubrepo -Directory | ForEach-Object {
    $nmPath = Join-Path $_.FullName "node_modules"
    if (Test-Path $nmPath) {
        $size = (Get-ChildItem $nmPath -File -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $nodeModulesTotal += $size
        $repoCount++
    }
}

Write-Host "Found $repoCount repos with node_modules" -ForegroundColor Yellow
Write-Host "Estimated node_modules size: $([math]::Round($nodeModulesTotal / 1GB, 2)) GB" -ForegroundColor Red

# 2. List large backup folders
Write-Host "`nStep 2: Backup folders over 100MB..." -ForegroundColor Cyan
Get-ChildItem X:\githubrepo -Directory | Where-Object { $_.Name -match "BACKUP|backup" } | ForEach-Object {
    $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($size -gt 100MB) {
        [PSCustomObject]@{
            Folder = $_.Name
            SizeMB = [math]::Round($size / 1MB, 2)
            Path = $_.FullName
        }
    }
} | Sort-Object SizeMB -Descending | Format-Table -AutoSize

# 3. Find duplicate OPENROUTER backups
Write-Host "`nStep 3: Duplicate backups to remove..." -ForegroundColor Cyan
Get-ChildItem X:\githubrepo -Directory | Where-Object { $_.Name -match "OPENROUTER_COMPLETE_BACKUP" } | Select-Object Name, FullName | Format-Table

# 4. Cleanup commands (commented out by default)
Write-Host "`n=== CLEANUP COMMANDS (Review First!) ===" -ForegroundColor Red
Write-Host "`n# Delete ALL node_modules folders (frees ~80-90% space):" -ForegroundColor Yellow
Write-Host "Get-ChildItem X:\githubrepo -Directory | ForEach-Object { " -ForegroundColor Gray
Write-Host "    `$nm = Join-Path `$_.FullName 'node_modules'" -ForegroundColor Gray
Write-Host "    if (Test-Path `$nm) { Remove-Item `$nm -Recurse -Force -ErrorAction SilentlyContinue }" -ForegroundColor Gray
Write-Host "}" -ForegroundColor Gray

Write-Host "`n# Delete duplicate OPENROUTER backups:" -ForegroundColor Yellow
Write-Host "Remove-Item X:\githubrepo\OPENROUTER_COMPLETE_BACKUP_* -Recurse -Force" -ForegroundColor Gray

Write-Host "`n# Delete old backups (keep only latest):" -ForegroundColor Yellow
Write-Host "Remove-Item X:\githubrepo\EMERGENCY_BACKUP, X:\githubrepo\ENHANCED_BACKUPS -Recurse -Force" -ForegroundColor Gray

Write-Host "`n=== Estimated Space After Cleanup ===" -ForegroundColor Green
Write-Host "Removing node_modules: ~$([math]::Round($nodeModulesTotal / 1GB, 2)) GB freed" -ForegroundColor Cyan
Write-Host "Removing duplicates: ~0.01 GB freed" -ForegroundColor Cyan
Write-Host "Total estimated free space: ~$([math]::Round($nodeModulesTotal / 1GB, 2)) GB" -ForegroundColor Green
