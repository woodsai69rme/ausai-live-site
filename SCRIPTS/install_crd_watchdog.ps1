# ===============================================================
#  install_crd_watchdog.ps1
#  Register a SYSTEM-level scheduled task that re-asserts
#  chromoting StartType=Auto every 5 minutes. Re-runnable.
# ===============================================================
$ErrorActionPreference = 'Stop'

$TaskName = 'CRD AutoStart Watchdog'
$BodyPath = Join-Path $PSScriptRoot 'crd_watchdog_action.ps1'

if (-not (Test-Path $BodyPath)) {
    Write-Error "Required script not found next to this installer: $BodyPath"
    exit 1
}

# Register-ScheduledTask fails when the principal is SYSTEM and we are
# running un-elevated. Detect and abort with a clean message.
$prin = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $prin.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error 'This installer requires an elevated (Run-as-administrator) PowerShell window.'
    Write-Error 'Re-launch powershell.exe as Administrator and re-run.'
    exit 2
}

$action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$BodyPath`""

# First run ~1 minute from now; then every 5 minutes for ~10 years.
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

# SYSTEM with Highest; ServiceAccount logon means the task fires
# even if no user profile is loaded -- matching how chromoting runs.
$principal = New-ScheduledTaskPrincipal `
    -UserId 'SYSTEM' `
    -LogonType ServiceAccount `
    -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

# Idempotent: nuke any prior copy so re-installs cleanly reset schedule.
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false | Out-Null
}

Register-ScheduledTask -TaskName $TaskName `
    -Action    $action `
    -Trigger   $trigger `
    -Principal $principal `
    -Settings  $settings `
    -Description 'Re-asserts Chrome Remote Desktop service (chromoting) StartType=Auto every 5 minutes so the auto-start value cannot silently regress.' |
    Out-Null

Write-Host ""
Write-Host ("Registered task '{0}'." -f $TaskName)
Write-Host ("  Run-as    : SYSTEM (highest, ServiceAccount)" )
Write-Host ("  Body      : {0}" -f $BodyPath)
Write-Host "  Schedule  : every 5 minutes, starting ~1 minute from now"
Write-Host "  Log file  : C:\ProgramData\CRD-Watchdog\log.txt  (only on regression)"
