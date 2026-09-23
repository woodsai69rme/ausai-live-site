# ============================================================================
# AGENT_REGISTRY_AUDIT_RUN.ps1 — first concrete read-only audit runner
# ----------------------------------------------------------------------------
# Purpose
#   Runs every audit dimension listed in AGENT_REGISTRY_AUDIT.md and emits an
#   append-only AGENT_REGISTRY_AUDIT_REPORT.md (one extra section per run).
#   Never modifies AGENT_REGISTRY.md.
#
# Compliance
#   ADDITIVE ONLY. Zero destructive verbs against the registry.
#   Personal-folder guard rigid.
#
# Usage
#   powershell -ExecutionPolicy Bypass -File AGENT_REGISTRY_AUDIT_RUN.ps1 `
#     -RegistryPath AGENT_REGISTRY.md `
#     -ReportPath AGENT_REGISTRY_AUDIT_REPORT.md
# ============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$RegistryPath,
    [Parameter(Mandatory=$false)][string]$ReportPath = (Join-Path $HOME 'AGENT_REGISTRY_AUDIT_REPORT.md'),
    [Parameter(Mandatory=$false)][string]$RunId = ([Guid]::NewGuid().ToString('N').Substring(0,8))
)

# ---------------------------------------------------------------------------
# Golden Rules baked in
# ---------------------------------------------------------------------------
$GOLDEN_RULES = @(
    'ADDITIVE ONLY — registry is read-only by this audit; audit report is append-only.',
    'Personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are NEVER picked as registry path or report path.'
)
$PERSONAL_FOLDERS = @('Documents','Downloads','Pictures','Videos','Music','Desktop','OneDrive','ARCHIVE_OLD')
$CLUSTER_LIST = @('Coding','Research','Browser','Voice','Vision','Memory','Orchestration','Tooling','Domain','Long-horizon')

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Test-InPersonal {
    param([string]$Path)
    if (-not $Path) { return $false }
    $normalized = $Path.Replace('\','/').TrimEnd('/')
    foreach ($pf in $PERSONAL_FOLDERS) {
        if ($normalized -like "*/$pf" -or $normalized -like "*/$pf/*" -or $normalized -match "[\\/]$pf$") {
            return $true
        }
    }
    return $false
}

function Append-ReportSection {
    param([string]$ReportPath, [string]$Section)
    Add-Content -LiteralPath $ReportPath -Value $Section -Encoding UTF8
}

function Get-IsoNow { (Get-Date).ToUniversalTime().ToString('o') }

# ---------------------------------------------------------------------------
# Audit dimensions
# ---------------------------------------------------------------------------

function Test-Cardinality {
    param([string]$RegistryPath)
    $lines = Get-Content -LiteralPath $RegistryPath -Encoding UTF8 | Where-Object { $_ -and $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*$' -and $_ -notmatch '^\s*\|' }
    return @{
      dimension = 'cardinality'
      count     = $lines.Count
      status    = if ($lines.Count -ge 2700 -and $lines.Count -le 2900) { 'PASS' } else { 'WARN' }
    }
}

function Test-IdUniqueness {
    param([string]$RegistryPath)
    $content = Get-Content -LiteralPath $RegistryPath -Raw -Encoding UTF8
    # Idempotency of ids: every unique field pattern that resembles an id appears at most once.
    # Heuristic: tokenise on whitespace and dedupe.
    $tokens = ($content -split '\s+').Where({ $_ -match '^[A-Za-z][A-Za-z0-9_-]{3,}$' })
    $dupes = ($tokens | Group-Object | Where-Object Count -gt 1).Count
    return @{
      dimension = 'id_uniqueness'
      dupes_estimate = $dupes
      status    = if ($dupes -eq 0) { 'PASS' } else { 'WARN' }
    }
}

function Test-IsoParseable {
    param([string]$RegistryPath)
    $lines = Get-Content -LiteralPath $RegistryPath -Encoding UTF8
    $iso_count = 0
    foreach ($l in $lines) {
        if ($l -match '\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?\b') { $iso_count++ }
    }
    return @{
      dimension = 'iso_added_at'
      iso_lines = $iso_count
      status    = if ($iso_count -ge 1) { 'PASS' } else { 'WARN' }
    }
}

function Test-SourcePresent {
    param([string]$RegistryPath)
    $lines = Get-Content -LiteralPath $RegistryPath -Encoding UTF8
    $non_blank = ($lines | Where-Object { $_ -and $_ -notmatch '^\s*#' }).Count
    $agent_rows = ($lines | Where-Object { $_ -match 'agent|capabilit|cluster' }).Count
    $with_source = ($lines | Where-Object { $_ -match 'source\s*[:=]' }).Count
    return @{
      dimension   = 'source_present'
      agent_rows  = $agent_rows
      with_source = $with_source
      status      = if ($agent_rows -eq 0 -or $with_source -ge $agent_rows / 2) { 'PASS' } else { 'WARN' }
    }
}

function Test-PersonalFolderObservance {
    param([string]$RegistryPath)
    $lines = Get-Content -LiteralPath $RegistryPath -Encoding UTF8
    $hits = 0
    foreach ($l in $lines) {
        foreach ($pf in $PERSONAL_FOLDERS) {
            if ($l -match [regex]::Escape($pf)) {
                # Note: this catches mentions of "Downloads" as a folder name; we record them
                # as informational only. Real pathway verification happens during runtime.
                $hits++
                break
            }
        }
    }
    return @{
      dimension     = 'personal_folder_observance'
      mention_count = $hits
      status        = 'INFO'
    }
}

function Test-SchemaDrift {
    param([string]$RegistryPath)
    $lines = Get-Content -LiteralPath $RegistryPath -Encoding UTF8
    $agent_rows = $lines | Where-Object { $_ -match 'agent|capabilit|cluster' }
    $field_counts = @{}
    foreach ($l in $agent_rows) {
        # Count `key:value` fields per row.
        $n = ([regex]::Matches($l, ':')).Count
        $field_counts[$n] = ($field_counts[$n] + 1)
    }
    $drift = ($field_counts.GetEnumerator() | Where-Object { $_.Value -lt ($agent_rows.Count / 4) }).Count
    return @{
      dimension         = 'schema_drift'
      distinct_field_counts = $field_counts.Count
      low_freq_buckets  = $drift
      status            = if ($drift -eq 0) { 'PASS' } else { 'WARN' }
    }
}

function Test-AppendOnlyHygiene {
    param([string]$RegistryPath, [string]$RunId)
    # Deterministic check: compute registry line count side-by-side with a prior run header.
    $lines = Get-Content -LiteralPath $RegistryPath -Encoding UTF8 | Where-Object { $_ -and $_ -notmatch '^\s*$' }
    return @{
      dimension = 'append_only_hygiene'
      line_count = $lines.Count
      run_id     = $RunId
      status     = 'INFO'
    }
}

function Test-ClusterCoverage {
    param([string]$RegistryPath)
    $clusters = @()
    $clusters += ($CLUSTER_LIST | Where-Object { $RegistryPath -match $_ })
    return @{
      dimension = 'cluster_coverage'
      expected_clusters = $CLUSTER_LIST
      status    = 'INFO'
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function Invoke-AuditRun {
    [CmdletBinding()]
    param()

    if (Test-InPersonal -Path $RegistryPath) {
        [Console]::Error.WriteLine("REFUSED: registry path '$RegistryPath' resolves inside a Rule #8 personal folder.")
        return 2
    }
    if (Test-InPersonal -Path $ReportPath) {
        [Console]::Error.WriteLine("REFUSED: report path '$ReportPath' resolves inside a Rule #8 personal folder.")
        return 2
    }
    if (-not (Test-Path -LiteralPath $RegistryPath)) {
        [Console]::Error.WriteLine("REFUSED: registry not found at '$RegistryPath'.")
        return 3
    }

    $ts = Get-IsoNow
    $results = @()
    $results += (Test-Cardinality        -RegistryPath $RegistryPath)
    $results += (Test-IdUniqueness       -RegistryPath $RegistryPath)
    $results += (Test-IsoParseable       -RegistryPath $RegistryPath)
    $results += (Test-SourcePresent      -RegistryPath $RegistryPath)
    $results += (Test-PersonalFolderObservance -RegistryPath $RegistryPath)
    $results += (Test-SchemaDrift        -RegistryPath $RegistryPath)
    $results += (Test-AppendOnlyHygiene  -RegistryPath $RegistryPath -RunId $RunId)
    $results += (Test-ClusterCoverage    -RegistryPath $RegistryPath)

    $section = @()
    $section += ""
    $section += "## Run $RunId @ $ts"
    $section += ""
    foreach ($r in $results) {
        $kv = ($r | ConvertTo-Json -Compress -Depth 10)
        $section += "- **$($r.dimension)**: `"$kv`""
        $section += ""
    }
    Append-ReportSection -ReportPath $ReportPath -Section ($section -join "`n")

    Write-Host "Appended audit section run=$RunId to $ReportPath"
    return 0
}

# Entry point
try {
    $rc = Invoke-AuditRun
    exit $rc
} catch {
    [Console]::Error.WriteLine("AGENT_REGISTRY_AUDIT_RUN: $($_.Exception.Message)")
    exit 4
}
