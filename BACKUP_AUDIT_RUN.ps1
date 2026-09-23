# ============================================================
# BACKUP_AUDIT_RUN.ps1
# Purpose: Daily backup integrity checker (first concrete).
#          Reads BACKUP_MANIFEST.json (read-only).
#          Appends ONE audit row per backup to BACKUP_AUDIT.log.
# Compliance: ADDITIVE ONLY. Never deletes, never modifies the
#             manifest, never overwrites the log.
# ============================================================

# ---- Constants ----------------------------------------------
$GOLDEN_RULES = @(
    'No Set-Content / Clear-Content / Remove-Item against registry/ledger/report/manifest/log/source.',
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
$BACKUP_STATUS_ENUM = @(
    'ok','size_mismatch','sha256_mismatch','missing','stale','unreadable'
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

function Read-Manifest {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $text = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if (-not $text) { return @() }
    try {
        $obj = $text | ConvertFrom-Json
        if ($obj -is [array]) { return $obj } else { return @($obj) }
    } catch { return $null }
}

function Test-Backup {
    param($Entry)
    if (-not $Entry.path) {
        return @{ status='unreadable'; detail='manifest_entry_missing_path' }
    }
    if (-not (Test-Path -LiteralPath $Entry.path)) {
        return @{ status='missing'; detail="path_absent=$($Entry.path)" }
    }
    $info = Get-Item -LiteralPath $Entry.path
    if ($Entry.expected_min_size_bytes) {
        $expected = [int64]$Entry.expected_min_size_bytes
        if ($info.Length -lt $expected) {
            return @{ status='size_mismatch'; detail="actual=$($info.Length) expected_min=$expected" }
        }
    }
    if ($Entry.max_age_days) {
        $ageDays = ((Get-Date) - $info.LastWriteTime).TotalDays
        if ($ageDays -gt [double]$Entry.max_age_days) {
            return @{ status='stale'; detail="age_days=$([math]::Round($ageDays,1)) max=$($Entry.max_age_days)" }
        }
    }
    if ($Entry.expected_sha256) {
        $actual = (Get-FileHash -LiteralPath $Entry.path -Algorithm SHA256).Hash.ToLower()
        if ($actual -ne $Entry.expected_sha256.ToLower()) {
            return @{ status='sha256_mismatch'; detail="actual=$actual" }
        }
    }
    return @{ status='ok'; detail="size=$($info.Length)" }
}

function Append-AuditRow {
    param([string]$LogPath, [hashtable]$Row)
    if (-not ($BACKUP_STATUS_ENUM -contains $Row.status)) {
        throw "refused: status '$($Row.status)' outside closed enum"
    }
    $line = '{0} | event=backup_audit | name={1} | status={2} | detail={3}' -f `
        $Row.ts, $Row.name, $Row.status, $Row.detail
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

# ---- Main ---------------------------------------------------
function Run {
    [CmdletBinding()]
    param(
        [string]$ManifestPath = 'BACKUP_MANIFEST.json',
        [string]$AuditLogPath = 'BACKUP_AUDIT.log',
        [switch]$DryRun,
        [switch]$Run
    )
    if ($DryRun -and $Run) {
        Write-Host 'refused: cannot pass both -DryRun and -Run' -ForegroundColor Yellow
        exit 5
    }
    $isDryRun = -not $Run      # absence of -Run means dry-run (the default)
    if (Test-InPersonal $ManifestPath) {
        Write-Host "refused: manifest path '$ManifestPath' under Rule #8 folder" -ForegroundColor Yellow
        exit 2
    }
    if (Test-InPersonal $AuditLogPath) {
        Write-Host "refused: audit-log path '$AuditLogPath' under Rule #8 folder" -ForegroundColor Yellow
        exit 2
    }
    if (-not (Test-Path -LiteralPath $ManifestPath)) {
        Write-Host "refused: manifest '$ManifestPath' not found" -ForegroundColor Yellow
        exit 3
    }
    $manifest = Read-Manifest -Path $ManifestPath
    if ($null -eq $manifest) {
        Write-Host 'refused: manifest could not be parsed' -ForegroundColor Yellow
        exit 4
    }
    $ts = Get-IsoNow
    Write-Host "=== Backup audit run @ $ts ==="
    Write-Host ("manifest: {0}  entries={1}" -f $ManifestPath, $manifest.Count)
    if ($isDryRun) {
        Write-Host '(dry-run: no rows will be appended to BACKUP_AUDIT.log)'
        foreach ($entry in $manifest) {
            $res = Test-Backup -Entry $entry
            Write-Host (" - {0,-30}  status={1,-16} detail={2}" -f $entry.name, $res.status, $res.detail)
        }
        Write-Host 'Dry-run OK; re-run with -Run to append.'
        exit 0
    }
    foreach ($entry in $manifest) {
        $res = Test-Backup -Entry $entry
        $row = @{ ts=$ts; name=$entry.name; status=$res.status; detail=$res.detail }
        Append-AuditRow -LogPath $AuditLogPath -Row $row
        Write-Host (" appended  {0,-30}  status={1}" -f $entry.name, $res.status)
    }
    Write-Host 'Run complete.'
    exit 0
}

Run @PSBoundParameters
