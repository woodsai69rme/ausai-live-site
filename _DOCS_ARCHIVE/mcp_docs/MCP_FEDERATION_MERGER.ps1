# ============================================================================
# MCP_FEDERATION_MERGER.ps1
# ----------------------------------------------------------------------------
# Purpose
#   Second-stage executor for SEARCH_FEDERATION_DESIGN.md's merger concept.
#   Reads MCP_QUERY_AUDIT.log (read-only) AND a local chunks.jsonl (read-only),
#   drops rows whose `project_id` mismatches the operator-supplied --project_id,
#   and appends ONE section per invocation to MCP_FEDERATION_RESULT.jsonl.
#
# Compliance
#   ADDITIVE ONLY. Both input files are read-only. The result file grows
#   append-only. Personal-folder guard rigid.
#
# Refusal matrix
#   --query-log in personal folder       => REFUSED (exit 2)
#   --chunks-path in personal folder     => REFUSED (exit 2)
#   --result-path in personal folder     => REFUSED (exit 2)
#   --query-log not found                => REFUSED (exit 3)
#   --chunks-path not found              => REFUSED (exit 3)
#   --project-id empty                   => REFUSED (exit 4)
#
# Usage
#   powershell -ExecutionPolicy Bypass -File MCP_FEDERATION_MERGER.ps1 `
#     -ProjectId default `
#     -QueryLog MCP_QUERY_AUDIT.log `
#     -ChunksPath PROJECT_BRAIN_2_0/chunks.jsonl `
#     -ResultPath MCP_FEDERATION_RESULT.jsonl `
#     [-DryRun]
# ============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$ProjectId,
    [Parameter(Mandatory=$false)][string]$QueryLog = (Join-Path $HOME 'MCP_QUERY_AUDIT.log'),
    [Parameter(Mandatory=$false)][string]$ChunksPath = 'PROJECT_BRAIN_2_0/chunks.jsonl',
    [Parameter(Mandatory=$false)][string]$ResultPath = (Join-Path $HOME 'MCP_FEDERATION_RESULT.jsonl'),
    [Parameter(Mandatory=$false)][switch]$DryRun
)

# ---------------------------------------------------------------------------
# Golden Rules baked in
# ---------------------------------------------------------------------------
$GOLDEN_RULES = @(
    'ADDITIVE ONLY — query log and chunks file are read-only; result file grows append-only.',
    'Personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are NEVER picked as query log, chunks path, or result path.'
)
$PERSONAL_FOLDERS = @('Documents','Downloads','Pictures','Videos','Music','Desktop','OneDrive','ARCHIVE_OLD')

# Closed outcome enum for the merger.
$MERGE_OUTCOME_ENUM = @('kept','dropped_project_mismatch','dropped_unknown_status','dropped_unreadable','dropped_personal_source')

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

function Get-IsoNow { (Get-Date).ToUniversalTime().ToString('o') }

function Append-ResultLine {
    param([string]$Path, [string]$Line)
    Add-Content -LiteralPath $Path -Value $Line -Encoding UTF8
}

function Parse-QueryRow {
    # Returns hashtable if a query row parses; $null otherwise.
    param([string]$Line)
    if (-not $Line -or ($Line -notmatch ' \| ')) { return $null }
    $fields = @{}
    foreach ($part in ($Line -split '\|')) {
        $p = $part.Trim()
        if ($p -match '^(.+?)=(.+?)$') {
            $fields[$Matches[1].Trim()] = $Matches[2].Trim()
        }
    }
    if (-not $fields.ContainsKey('event')) { return $null }
    return $fields
}

function Test-PersonalInPath {
    param([string]$SourcePath)
    if (-not $SourcePath) { return $false }
    $norm = $SourcePath.Replace('\','/').TrimEnd('/')
    foreach ($pf in $PERSONAL_FOLDERS) {
        if ($norm -like "*/$pf" -or $norm -like "*/$pf/*") { return $true }
    }
    return $false
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function Invoke-FederationMerger {
    [CmdletBinding()]
    param()

    if (-not $ProjectId -or [string]::IsNullOrWhiteSpace($ProjectId)) {
        [Console]::Error.WriteLine("REFUSED: --project-id is empty (Phase G mandate).")
        return 4
    }
    if (Test-InPersonal -Path $QueryLog) {
        [Console]::Error.WriteLine("REFUSED: --query-log '$QueryLog' resolves inside a Rule #8 personal folder.")
        return 2
    }
    if (Test-InPersonal -Path $ChunksPath) {
        [Console]::Error.WriteLine("REFUSED: --chunks-path '$ChunksPath' resolves inside a Rule #8 personal folder.")
        return 2
    }
    if (Test-InPersonal -Path $ResultPath) {
        [Console]::Error.WriteLine("REFUSED: --result-path '$ResultPath' resolves inside a Rule #8 personal folder.")
        return 2
    }
    if (-not (Test-Path -LiteralPath $QueryLog)) {
        [Console]::Error.WriteLine("REFUSED: --query-log not found at '$QueryLog'.")
        return 3
    }
    if (-not (Test-Path -LiteralPath $ChunksPath)) {
        [Console]::Error.WriteLine("REFUSED: --chunks-path not found at '$ChunksPath'.")
        return 3
    }

    $ts = Get-IsoNow
    $counts = @{
      kept                 = 0
      dropped_project_mismatch = 0
      dropped_unknown_status = 0
      dropped_unreadable   = 0
      dropped_personal_source = 0
      total_query_rows     = 0
      total_chunk_rows     = 0
    }

    # Phase 1: scan query log; identify rows for this project's federation envelope.
    $query_lines = Get-Content -LiteralPath $QueryLog -Encoding UTF8
    foreach ($l in $query_lines) {
        $row = Parse-QueryRow -Line $l
        if ($null -eq $row) { continue }
        if ($row['event'] -ne 'federation_search') { continue }
        $counts.total_query_rows += 1
        $proj = [string]$row['project']
        if ($proj -ne $ProjectId) { $counts.dropped_project_mismatch += 1; continue }
        if (-not (Test-Path Variable:PSVersionTable) -or $true) { } # placeholder
        if ($null -eq $proj) { $counts.dropped_unknown_status += 1; continue }
    }

    # Phase 2: scan chunks.jsonl; drop rows whose project_id mismatches; drop rows with personal source path.
    try {
        $chunk_lines = Get-Content -LiteralPath $ChunksPath -Encoding UTF8
        foreach ($l in $chunk_lines) {
            if (-not $l) { continue }
            try {
                $cj = $l | ConvertFrom-Json -ErrorAction Stop
                $counts.total_chunk_rows += 1
                $pid = [string]$cj.project_id
                $src = [string]$cj.source_path
                # Sourced personal-folder values are always dropped pre-merge.
                if (Test-PersonalInPath -SourcePath $src) { $counts.dropped_personal_source += 1; continue }
                if ($pid -ne $ProjectId) { $counts.dropped_project_mismatch += 1; continue }
                $counts.kept += 1
            } catch {
                $counts.dropped_unreadable += 1
            }
        }
    } catch {
        [Console]::Error.WriteLine("REFUSED: cannot read chunks path: $($_.Exception.Message)")
        return 3
    }

    if ($DryRun) {
        Write-Host "DRY-RUN MCP_FEDERATION_MERGER: would append section to $ResultPath"
        Write-Host ("  kept={0} project_mismatch={1} personal_source={2} unreadable={3} total_chunks={4}" -f `
            $counts.kept, $counts.dropped_project_mismatch, $counts.dropped_personal_source, $counts.dropped_unreadable, $counts.total_chunk_rows)
        return 0
    }

    # Append one JSONL row per the closed outcome enum's summary.
    # Encode the order-preserving pseudocode below as a single JSON object.
    $summary = [ordered]@{
      ts              = $ts
      project_id      = $ProjectId
      kept            = $counts.kept
      dropped_project_mismatch = $counts.dropped_project_mismatch
      dropped_unknown_status = $counts.dropped_unknown_status
      dropped_unreadable = $counts.dropped_unreadable
      dropped_personal_source = $counts.dropped_personal_source
      total_query_rows = $counts.total_query_rows
      total_chunk_rows = $counts.total_chunk_rows
    }
    Append-ResultLine -Path $ResultPath -Line ($summary | ConvertTo-Json -Compress -Depth 5)
    Write-Host ("MCP_FEDERATION_MERGER: appended 1 summary row to {0} (kept={1} dropped={2})" -f `
        $ResultPath, $counts.kept, ($counts.dropped_project_mismatch + $counts.dropped_personal_source + $counts.dropped_unreadable))
    return 0
}

# Entry point
try {
    $rc = Invoke-FederationMerger
    exit $rc
} catch {
    [Console]::Error.WriteLine("MCP_FEDERATION_MERGER: $($_.Exception.Message)")
    exit 5
}
