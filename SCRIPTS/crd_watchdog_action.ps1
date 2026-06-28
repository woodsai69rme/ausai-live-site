# ===============================================================
#  crd_watchdog_action.ps1
#  Body of the scheduled task. Runs every 5 minutes under SYSTEM.
#
#  Two self-healing actions, in order:
#    1. Re-arm StartMode if it has regressed from AUTO_START.
#    2. Restart the service if it is STOPPED (covers runtime crashes,
#       `sc stop`, or someone ending it via Task Manager / Services.msc).
#
#  Both checks run on every tick. The second is independent of the first
#  so a running-but-StartMode=`auto` service that gets stopped still
#  gets recovered.
#
#  Idempotent: silent when the service is healthy on both axes.
# ===============================================================
$ErrorActionPreference = 'Continue'

# Fast path: sc qc is faster than Get-CimInstance for one-shot config read.
$qc = & sc.exe qc chromoting 2>&1
if ($LASTEXITCODE -ne 0) {
    # Service registration missing -- left to the user / installer.
    exit 0
}

# === Step 1: re-arm StartMode if regressed ===
$startModeHealthy = $qc -match '^\s*START_TYPE\s*:\s*2\s+AUTO_START'
$prevMode = ''
if (-not $startModeHealthy) {
    # Capture prior value for the log before flipping.
    $prevLine = ($qc | Select-String -Pattern '^\s*START_TYPE\s*:\s*.*$').ToString()
    $prevMode = ($prevLine -split ':', 2)[1].Trim()

    & sc.exe config chromoting start= auto | Out-Null
}

# === Step 2: re-arm the service if it stopped ===
# STATE values:
#   1 STOPPED       -- act, call sc start
#   2 START_PENDING -- mid-transition; sc start will return 1056
#   3 STOP_PENDING  -- mid-transition; do not interfere
#   4 RUNNING       -- quiet
# Only act on 1; pending-state races are naturally absorbed by the
# 1056 ERROR_SERVICE_ALREADY_RUNNING tolerance on `sc start`.
$state = & sc.exe query chromoting 2>&1
$stateStopped = ($LASTEXITCODE -eq 0) -and ($state -match '^\s*STATE\s*:\s*1\s+STOPPED')
$startCode = 0
if ($stateStopped) {
    & sc.exe start chromoting 2>&1 | Out-Null
    $startCode = $LASTEXITCODE
}

# === Logging: append only when something happened ===
$hadAction = (-not $startModeHealthy) -or $stateStopped
if ($hadAction) {
    $logDir  = 'C:\ProgramData\CRD-Watchdog'
    $logPath = Join-Path $logDir 'log.txt'
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    if (-not $startModeHealthy) {
        $startEntry = '{0}  chromoting.StartMode was "{1}"; reset to "Auto".' -f `
                      (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss'), $prevMode
        Add-Content -Path $logPath -Value $startEntry
    }

    if ($stateStopped) {
        $stopMsg = switch ($startCode) {
            0       { 'restart issued' }
            1056    { 'race: already running' }
            1058    { 'service still disabled -- Step 1 flip did not stick (group policy or SCM caching?)' }
            default { "start returned exit $startCode" }
        }
        $stateEntry = '{0}  chromoting.State was "STOPPED"; {1}.' -f `
                      (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss'), $stopMsg
        Add-Content -Path $logPath -Value $stateEntry
    }
}

# Healthy on both axes (or no service to manage): silent 0.
exit 0
