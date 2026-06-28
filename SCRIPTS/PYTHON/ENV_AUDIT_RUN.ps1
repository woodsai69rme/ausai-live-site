# ============================================================
# ENV_AUDIT_RUN.ps1
# Purpose: Cross-check .env against .env.example (first concrete).
#          Reads .env + .env.example (read-only).
#          Appends ONE summary row per key to ENV_AUDIT.log.
# Compliance: ADDITIVE ONLY. Never overwrites .env or .env.example.
# ============================================================

# ---- Constants ----------------------------------------------
$GOLDEN_RULES = @(
    'No Set-Content / Clear-Content / Remove-Item against registry/ledger/report/manifest/log/source/.env/.env.example.',
    'Never touch personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, ARCHIVE_OLD).',
    'Default to -DryRun; opt-in to write with -Run.',
    'Append-only writes; never overwrite prior log lines.',
    'Closed enum statuses only; no free-form status strings.',
    'Do not replace or rewrite prior artifacts.'
)

# 8-item Rule #8 personal-folder list — exhaustive by design.
$PERSONAL_FOLDERS = @(
    'Documents','Downloads','Pictures','Videos',
    'Music','Desktop','OneDrive','ARCHIVE_OLD'
)

# Closed status enum — entries outside the enum are refused.
$ENV_KEY_STATUS_ENUM = @(
    'present','missing_in_env','extra_in_env','placeholder_value','blank_value'
)

# ---- Helpers ------------------------------------------------
# Test-InPersonal: walks the 8-item list and matches on the
# normalized forward-slash form per the collapsed nit pattern.
function Test-InPersonal {
    param([string]$Path)
    $norm = ($Path -replace '\\','/').TrimEnd('/')
    foreach ($pf in $PERSONAL_FOLDERS) {
        $suffix = '/' + $pf
        if ($norm.EndsWith($suffix) -or ($norm + '/').Contains($suffix + '/')) {
            return $true
        }
    }
    return $false
}

function Get-IsoNow { (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }

function Read-EnvKeys {
    param([string]$Path)
    $keys = @{}
    if (-not (Test-Path -LiteralPath $Path)) { return $keys }
    Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#')) { return }
        $eq = $line.IndexOf('=')
        if ($eq -lt 1) { return }
        $k = $line.Substring(0, $eq).Trim()
        $v = $line.Substring($eq + 1).Trim()
        $keys[$k] = $v
    }
    return $keys
}

# Classify-Value: returns the closed enum form. Substring
# heuristic only — operators inspect the log for false positives.
function Classify-Value {
    param([string]$Value)
    if ($null -eq $Value) { return 'blank_value' }
    if ($Value.Length -eq 0) { return 'blank_value' }
    $placeholders = @(
        'your-','changeme','example','placeholder','xxx','todo','<','>','replace-me'
    )
    foreach ($p in $placeholders) {
        if ($Value.Contains($p)) { return 'placeholder_value' }
    }
    return 'present'
}

function Append-Audit {
    param([string]$LogPath, [hashtable]$Row)
    if (-not ($ENV_KEY_STATUS_ENUM -contains $Row.status)) {
        throw "refused: status '$($Row.status)' outside closed enum"
    }
    $line = '{0} | event=env_audit | key={1} | status={2}' -f `
        $Row.ts, $Row.key, $Row.status
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

# ---- Main ---------------------------------------------------
function Invoke-EnvAudit {
    [CmdletBinding()]
    param(
        [string]$EnvPath = '.env',
        [string]$ExamplePath = '.env.example',
        [string]$AuditLogPath = 'ENV_AUDIT.log',
        [switch]$DryRun,
        [switch]$Run
    )
    if ($DryRun -and $Run) {
        Write-Host 'refused: cannot pass both -DryRun and -Run'
        exit 5
    }
    $isDryRun = -not $Run      # absence of -Run means dry-run (the default)
    foreach ($p in @($EnvPath, $ExamplePath, $AuditLogPath)) {
        if (Test-InPersonal $p) {
            Write-Host "refused: path '$p' under Rule #8 folder"
            exit 2
        }
    }
    if (-not (Test-Path -LiteralPath $ExamplePath)) {
        Write-Host "refused: example file '$ExamplePath' not found"
        exit 3
    }
    $envMap = Read-EnvKeys -Path $EnvPath
    $exMap  = Read-EnvKeys -Path $ExamplePath
    $ts = Get-IsoNow
    Write-Host "=== Env audit run @ $ts ==="
    Write-Host ("env: {0}  example: {1}" -f $EnvPath, $ExamplePath)
    if ($isDryRun) {
        Write-Host '(dry-run: no rows will be appended to ENV_AUDIT.log)'
        foreach ($k in ($exMap.Keys | Sort-Object)) {
            if (-not $envMap.ContainsKey($k)) {
                Write-Host (" - {0,-30}  status=missing_in_env" -f $k)
                continue
            }
            $cls = Classify-Value -Value $envMap[$k]
            Write-Host (" - {0,-30}  status={1}" -f $k, $cls)
        }
        foreach ($k in $envMap.Keys) {
            if (-not $exMap.ContainsKey($k)) {
                Write-Host (" - {0,-30}  status=extra_in_env" -f $k)
            }
        }
        Write-Host 'Dry-run OK; re-run with -Run to append.'
        return
    }
    foreach ($k in ($exMap.Keys | Sort-Object)) {
        if (-not $envMap.ContainsKey($k)) {
            Append-Audit -LogPath $AuditLogPath -Row @{ ts=$ts; key=$k; status='missing_in_env' }
            continue
        }
        $cls = Classify-Value -Value $envMap[$k]
        Append-Audit -LogPath $AuditLogPath -Row @{ ts=$ts; key=$k; status=$cls }
    }
    foreach ($k in $envMap.Keys) {
        if (-not $exMap.ContainsKey($k)) {
            Append-Audit -LogPath $AuditLogPath -Row @{ ts=$ts; key=$k; status='extra_in_env' }
        }
    }
    Write-Host 'Run complete.'
}

Invoke-EnvAudit @PSBoundParameters
