# scan_pc_apps.ps1 — discover every installed app on this Windows machine.
#
# Output: RAW_PC_APPS_INVENTORY.csv at workspace root. Columns:
#   DisplayName, DisplayVersion, Publisher, InstallLocation, Source
#
# Source flags:
#   "Registry HKLM 64"     → 64-bit registry uninstall keys
#   "Registry HKLM 32"     → 32-bit-on-64-bit registry uninstall keys
#   "Registry HKCU"        → per-user registry uninstall keys
#   "AppX Store"           → Microsoft Store / AppxManifest
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scan_pc_apps.ps1
#
# Designed under Karma's Golden Rules:
#   - read-only (does NOT install/uninstall anything)
#   - output to one CSV (append/example: rename RAW_PC_APPS_INVENTORY.csv → .prev)
#   - never touches Documents / Downloads / Desktop / OneDrive / Pictures /
#     Videos / Music / ARCHIVE_OLD (Rule #8 personal-folder fence)

[CmdletBinding()]
param(
    [string]$OutputPath = "$PSScriptRoot\RAW_PC_APPS_INVENTORY.csv"
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "Scanning OS applications (Registry HKLM 64-bit + 32-bit + HKCU + AppX Store)..." -ForegroundColor Cyan

# ----------------------------------------------------------------------
# 1) Registry HKLM 64-bit uninstall keys
# ----------------------------------------------------------------------
$reg64 = Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -and $_.DisplayName.Trim().Length -gt 0 } |
    Select-Object `
        @{Name='DisplayName';      Expression={$_.DisplayName}},
        @{Name='DisplayVersion';   Expression={if ($_.DisplayVersion) { $_.DisplayVersion } else { 'n/a' }}},
        @{Name='Publisher';        Expression={if ($_.Publisher) { $_.Publisher } else { 'n/a' }}},
        @{Name='InstallLocation';  Expression={if ($_.InstallLocation) { $_.InstallLocation } else { '(unknown)' }}},
        @{Name='Source';           Expression={ 'Registry HKLM 64' }}

# ----------------------------------------------------------------------
# 2) Registry HKLM 32-bit-on-64-bit uninstall keys (Wow6432Node)
# ----------------------------------------------------------------------
$reg32 = Get-ItemProperty "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -and $_.DisplayName.Trim().Length -gt 0 } |
    Select-Object `
        @{Name='DisplayName';      Expression={$_.DisplayName}},
        @{Name='DisplayVersion';   Expression={if ($_.DisplayVersion) { $_.DisplayVersion } else { 'n/a' }}},
        @{Name='Publisher';        Expression={if ($_.Publisher) { $_.Publisher } else { 'n/a' }}},
        @{Name='InstallLocation';  Expression={if ($_.InstallLocation) { $_.InstallLocation } else { '(unknown)' }}},
        @{Name='Source';           Expression={ 'Registry HKLM 32' }}

# ----------------------------------------------------------------------
# 3) Registry HKCU per-user uninstall keys
# ----------------------------------------------------------------------
$regcu = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -and $_.DisplayName.Trim().Length -gt 0 } |
    Select-Object `
        @{Name='DisplayName';      Expression={$_.DisplayName}},
        @{Name='DisplayVersion';   Expression={if ($_.DisplayVersion) { $_.DisplayVersion } else { 'n/a' }}},
        @{Name='Publisher';        Expression={if ($_.Publisher) { $_.Publisher } else { 'n/a' }}},
        @{Name='InstallLocation';  Expression={if ($_.InstallLocation) { $_.InstallLocation } else { '(unknown)' }}},
        @{Name='Source';           Expression={ 'Registry HKCU' }}

# ----------------------------------------------------------------------
# 4) AppX / Microsoft Store packaged apps
# ----------------------------------------------------------------------
$appx = Get-AppxPackage -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -and $_.Name.Trim().Length -gt 0 } |
    Select-Object `
        @{Name='DisplayName';      Expression={$_.Name}},
        @{Name='DisplayVersion';   Expression={if ($_.Version) { $_.Version.ToString() } else { 'n/a' }}},
        @{Name='Publisher';        Expression={if ($_.Publisher) { $_.Publisher } else { 'n/a' }}},
        @{Name='InstallLocation';  Expression={ 'AppX Store' }},
        @{Name='Source';           Expression={ 'AppX Store' }}

# ----------------------------------------------------------------------
# 5) Concat → unique → sort → emit
# ----------------------------------------------------------------------
$all = @($reg64) + @($reg32) + @($regcu) + @($appx) |
    Sort-Object DisplayName -Unique

Write-Host ""
Write-Host "Scan complete. Counts by source:" -ForegroundColor Green
Write-Host ("  Registry HKLM 64 : {0}" -f $reg64.Count)
Write-Host ("  Registry HKLM 32 : {0}" -f $reg32.Count)
Write-Host ("  Registry HKCU    : {0}" -f $regcu.Count)
Write-Host ("  AppX Store       : {0}" -f $appx.Count)
Write-Host ("  TOTAL            : {0}" -f $all.Count)

# Atomic write: temp then move. Avoid leaving a half-written CSV if the
# disc fills mid-export.
$tempPath = "$OutputPath.tmp"
$all | Export-Csv -Path $tempPath -NoTypeInformation -Encoding UTF8
Move-Item -Path $tempPath -Destination $OutputPath -Force

Write-Host ""
Write-Host ("Exported {0} unique rows to:" -f $all.Count) -ForegroundColor Green
Write-Host ("  $OutputPath") -ForegroundColor Yellow
Write-Host ""
Write-Host "Next step: open the CSV and curate the top ~40 apps into tool_kit.py REGISTRY." -ForegroundColor Cyan
Write-Host "  python tool_kit.py list --category os-apps" -ForegroundColor Cyan
