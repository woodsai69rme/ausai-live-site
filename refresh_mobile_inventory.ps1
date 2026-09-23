# refresh_mobile_inventory.ps1 -- filter companion to refresh_mobile_inventory.bat
#
# Reads a raw CSV (default: most recent RAW_PC_APPS_INVENTORY__*.csv from user
# profile; fallback to RAW_PC_APPS_INVENTORY.csv) and emits MOBILE_FILTERED.csv
# with rows matching mobile keywords (adb / apktool / jadx / frida / etc).
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File refresh_mobile_inventory.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File refresh_mobile_inventory.ps1 -RawCsv C:\foo\bar.csv -OutCsv C:\foo\out.csv
#
# Designed under Karma's Golden Rules:
#   - read-only (does NOT install/uninstall anything)
#   - append-friendly: raw CSV written by scan_pc_apps.ps1 stays; MOBILE_FILTERED.csv is rewritten atomically
#   - never touches Documents / Downloads / Desktop / OneDrive / Pictures / Videos / Music

[CmdletBinding()]
param(
    [string]$RawCsv,
    [string]$OutCsv = "$PSScriptRoot\MOBILE_FILTERED.csv"
)

$ErrorActionPreference = "SilentlyContinue"

# Decide which RAW CSV to read
if (-not $RawCsv) {
    $candidates = Get-ChildItem -Path $PSScriptRoot -Filter "RAW_PC_APPS_INVENTORY*.csv" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending
    if ($candidates -and $candidates.Count -gt 0) {
        $RawCsv = $candidates[0].FullName
    } else {
        Write-Host "[FAIL] no RAW_PC_APPS_INVENTORY*.csv in $PSScriptRoot -- run scan_pc_apps.ps1 first." -ForegroundColor Red
        exit 3
    }
}
if (-not (Test-Path $RawCsv)) {
    Write-Host "[FAIL] raw CSV missing: $RawCsv" -ForegroundColor Red
    exit 4
}
Write-Host "scanning: $RawCsv"

# Load + filter
$rows = Import-Csv -Path $RawCsv
Write-Host ("  total rows in source: {0}" -f $rows.Count)

$terms = @('adb','fastboot','apktool','jadx','frida','magisk','libimobile',
           'ibimobiledevice','idevice','android studio','platform tools','mtkclient',
           'mtk client','wsa','subsystem for android','scrcpy','imazing','mediatek',
           'samsung','oppo','xiaomi','huawei','pixel','snapdragon','qualcomm','iphone','ipad')

$hits = foreach ($r in $rows) {
    $blob = (($r.DisplayName) + ' ' + ($r.Publisher))
    $matched = @()
    foreach ($t in $terms) {
        if ($blob -match [regex]::Escape($t)) { $matched += $t }
    }
    if ($matched.Count -gt 0) {
        $obj = [ordered]@{}
        foreach ($k in $r.Keys) { $obj[$k] = $r[$k] }
        $obj['matched_terms'] = ($matched -join ',')
        [pscustomobject]$obj
    }
}

Write-Host ("  mobile-related hits: {0}" -f ($hits | Measure-Object).Count)
foreach ($h in ($hits | Select-Object -First 50)) {
    $name = if ([string]::IsNullOrEmpty($h.DisplayName)) { '<NULL>' } else { $h.DisplayName }
    Write-Host ("    {0,-55} | {1,-30} | {2}" -f $name.Substring(0, [Math]::Min($name.Length, 55)), `
                                       ($h.matched_terms.Substring(0, [Math]::Min($h.matched_terms.Length, 30))), `
                                       $h.Source)
}

# Atomic write: tmp + move (no half-written file)
$tmpPath = "$OutCsv.tmp"
$hits | Export-Csv -Path $tmpPath -NoTypeInformation -Encoding UTF8
Move-Item -Path $tmpPath -Destination $OutCsv -Force
Write-Host ("PASS -- wrote {0} mobile-related rows to: {1}" -f ($hits | Measure-Object).Count, $OutCsv) -ForegroundColor Green
exit 0
