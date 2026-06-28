<#
.SYNOPSIS
    Verifies the integrity of critical system files against a known baseline.
    Part of Option 1.7: Backup Integrity Verifier.

.DESCRIPTION
    This script calculates SHA256 hashes of files in critical directories and compares them
    against a stored manifest. It alerts on modified, added, or deleted files.

.PARAMETER Generate
    If specified, generates a new baseline manifest instead of verifying.

.EXAMPLE
    .\verify_backups.ps1 -Generate
    Generates a new baseline.

.EXAMPLE
    .\verify_backups.ps1
    Verifies current files against the baseline.
#>

param (
    [Switch]$Generate
)

$CriticalPaths = @(
    "C:\Users\karma\scripts",
    "C:\Users\karma\.gemini",
    "C:\Users\karma\docs"
)

$ManifestFile = "C:\Users\karma\scripts\security\backup_manifest.json"
$LogFile = "C:\Users\karma\scripts\security\integrity_log.txt"

function Log-Message {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Get-FileHashDictionary {
    $Hashes = @{}
    foreach ($Path in $CriticalPaths) {
        if (Test-Path $Path) {
            Log-Message "Scanning $Path..."
            Get-ChildItem -Path $Path -Recurse -File | 
                Where-Object { $_.FullName -notmatch "node_modules|__pycache__|\.git|tmp|temp" } |
                ForEach-Object {
                    $Hash = Get-FileHash -Path $_.FullName -Algorithm SHA256
                    $Hashes[$_.FullName] = $Hash.Hash
                }
        } else {
            Log-Message "[WARN] Path not found: $Path"
        }
    }
    return $Hashes
}

# Ensure log directory exists
$LogDir = Split-Path $LogFile
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

if ($Generate) {
    Log-Message "[INFO] Generating new integrity baseline..."
    $CurrentState = Get-FileHashDictionary
    $CurrentState | ConvertTo-Json -Depth 5 | Set-Content -Path $ManifestFile
    Log-Message "[OK] Baseline generated with $($CurrentState.Count) files."
}
else {
    if (-not (Test-Path $ManifestFile)) {
        Log-Message "[FAIL] Baseline manifest not found. Run with -Generate first."
        exit 1
    }

    Log-Message "[INFO] Verifying system integrity..."
    $Baseline = Get-Content -Path $ManifestFile | ConvertFrom-Json -AsHashtable
    $CurrentState = Get-FileHashDictionary
    
    $Errors = 0
    
    # Check for modified or deleted files
    foreach ($File in $Baseline.Keys) {
        if (-not $CurrentState.ContainsKey($File)) {
            Log-Message "[FAIL] DELETED: $File"
            $Errors++
        }
        elseif ($CurrentState[$File] -ne $Baseline[$File]) {
            Log-Message "[FAIL] MODIFIED: $File"
            $Errors++
        }
    }
    
    # Check for new files (optional, but good for security)
    foreach ($File in $CurrentState.Keys) {
        if (-not $Baseline.ContainsKey($File)) {
            Log-Message "[WARN] NEW FILE: $File"
        }
    }
    
    if ($Errors -eq 0) {
        Log-Message "[OK] Verification Complete: System Integrity Verified."
    } else {
        Log-Message "[FAIL] Verification Complete: $Errors integrity violations found."
        exit 1
    }
}
