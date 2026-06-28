# Register-BackupTask.ps1 - ENH-H1 Master Backup Scheduler
#
# ✅ COMPLIANCE: ADDITIVE ONLY.
# - Registers VERIFICATION ONLY (no copies, moves, deletes).
# - Calls `verify_backups.ps1` which already obeys Rule #8.
# - Idempotent: a re-run updates the existing task; no duplicates spawned.
# - Personal folders (Documents, Downloads, Pictures, Videos, Music,
#   Desktop, OneDrive, Downloads\ARCHIVE_OLD) are NEVER touched.
#
# Usage (Administrator required):
#   powershell -ExecutionPolicy Bypass -File .\Register-BackupTask.ps1

[CmdletBinding()]
param(
    [string]$ScriptPath     = "$PSScriptRoot\verify_backups.ps1",
    [string]$TaskName       = "GoldenRules-VerifyBackups",
    [string]$TaskFolder     = "\GoldenRules",
    [string]$Schedule       = "DAILY",   # DAILY | WEEKLY | HOURLY | ONLOGON
    [datetime]$RunAt        = ([datetime]::Today).AddHours(6),  # 06:00 local
    [string[]]$DaysOfWeek    = @("SUN"),  # if WEEKLY
    [switch]$Unregister
)

# ---------------------------------------------------------------------------
# Compliance constants
# ---------------------------------------------------------------------------
$GOLDEN_RULES = @"
$( "=" * 70 )
⭐ Rule #1  Nothing is obsolete (we never delete backups).
⭐ Rule #5  All backups are critical (we never alter backups).
⭐ Rule #7  Enhancement not reduction.
⭐ Rule #8  Personal folders are sacred (NEVER touched). verify_backups.ps1 enforces.
$( "=" * 70 )
"@

$PERSONAL_FOLDERS = @(
    "$HOME\Documents",
    "$HOME\Downloads",
    "$HOME\Pictures",
    "$HOME\Videos",
    "$HOME\Music",
    "$HOME\Desktop",
    "$HOME\OneDrive",
    "$HOME\Downloads\ARCHIVE_OLD"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Test-Admin {
    $id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object System.Security.Principal.WindowsPrincipal($id)
    return $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Confirm-SafeRoot {
    param([string]$Path)
    foreach ($p in $PERSONAL_FOLDERS) {
        if ($Path -like "$p*") {
            throw "REFUSED: path '$Path' is inside Rule #8 personal folder '$p'."
        }
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function Main {
    if ($Unregister) {
        Write-Output $GOLDEN_RULES
        Write-Output "[$TaskName] Unregister requested."
        if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Output "[$TaskName] Unregistered."
        } else {
            Write-Output "[$TaskName] No task to remove."
        }
        "Unregister $(Get-Date -Format 'o')" | Out-File -Append -FilePath "$HOME\08_SCRIPTS\BACKUP_SCHEDULER_AUDIT.log" -Encoding utf8
        return
    }

    if (-not (Test-Admin)) {
        throw "REFUSED: must run as Administrator (right-click → Run as Administrator). Exits without changes."
    }

    if (-not (Test-Path -LiteralPath $ScriptPath)) {
        throw "REFUSED: verify_backups.ps1 missing at '$ScriptPath'. The scheduler would fail on every trigger."
    }

    # Defense-in-depth: even though verify_backups.ps1 enforces Rule #8 internally,
    # refuse to wire this scheduler if any path we operate on would resolve to a
    # personal folder. This protects against future parameter expansion.
    Confirm-SafeRoot -Path $ScriptPath
    foreach ($seg in ($TaskFolder -split '\\')) {
        if ($seg -and $PERSONAL_FOLDERS -contains $seg) {
            throw "REFUSED: TaskFolder '$TaskFolder' contains a Rule #8 component ('$seg')."
        }
    }

    # Sanity: is the script's reported target list Rule-#8-safe?
    # verify_backups.ps1 already enforces; we declare it here as defense-in-depth.
    Write-Output $GOLDEN_RULES

    Write-Output "[$TaskName] Script path: $ScriptPath"
    Write-Output "[$TaskName] Schedule  : $Schedule, run-at-local $($RunAt.ToString('t'))"
    if ($Schedule -eq 'WEEKLY') {
        Write-Output "[$TaskName] Days       : $($DaysOfWeek -join ', ')"
    }

    $action  = New-ScheduledTaskAction -Execute 'powershell.exe' `
                -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`""
    $trigger = switch ($Schedule) {
        'DAILY'   { New-ScheduledTaskTrigger -Daily -At $RunAt }
        'WEEKLY'  { New-ScheduledTaskTrigger -Weekly -DaysOfWeek $DaysOfWeek -At $RunAt }
        'HOURLY'  { New-ScheduledTaskTrigger -Once -At $RunAt -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650) }
        'ONLOGON' { New-ScheduledTaskTrigger -AtLogOn }
        default   { throw "Schedule must be DAILY | WEEKLY | HOURLY | ONLOGON" }
    }
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" `
                -RunLevel Highest
    $settings  = New-ScheduledTaskSettingsSet `
                -StartWhenAvailable `
                -DontStopOnIdleEnd `
                -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
                -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)

    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings
        Write-Output "[$TaskName] Updated existing task in place (no duplicate; idempotent)."
    } else {
        Register-ScheduledTask -TaskName $TaskName `
            -TaskPath $TaskFolder `
            -Action $action `
            -Trigger $trigger `
            -Principal $principal `
            -Settings $settings `
            -Description "ENH-H1: schedules verify_backups.ps1 (additive integrity audit). Personal folders untouched (Rule #8)."
        Write-Output "[$TaskName] Registered under $TaskFolder."
    }

    # Compliance log (append-only)
    $line = "$(Get-Date -Format 'o') [$TaskName] schedule=$Schedule at=$($RunAt.ToString('o')) host=$env:COMPUTERNAME script=$ScriptPath"
    $dir = "$HOME\08_SCRIPTS"
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $line | Out-File -Append -FilePath "$dir\BACKUP_SCHEDULER_AUDIT.log" -Encoding utf8
    Write-Output "[$TaskName] Audit line appended to 08_SCRIPTS\BACKUP_SCHEDULER_AUDIT.log."
}

Main
