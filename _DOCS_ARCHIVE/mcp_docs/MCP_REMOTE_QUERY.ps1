# ============================================================================
# MCP_REMOTE_QUERY.ps1
# ----------------------------------------------------------------------------
# Purpose
#   First concrete federation executor (per SEARCH_FEDERATION_DESIGN.md).
#   Reads one MCP backend entry from the registry, sends a search envelope,
#   and appends ONE line to MCP_QUERY_AUDIT.log per backend. Local search
#   is NOT invoked here; this script handles the REMOTE side.
#
# Compliance
#   ADDITIVE ONLY. Registry is read-only; audit log is append-only.
#   Personal-folder guard rigid.
#
# Refusal matrix
#   --registry-path in personal folder       => REFUSED (exit 2)
#   --audit-out in personal folder           => REFUSED (exit 2)
#   --server not in registry                 => REFUSED (exit 3)
#   --remote-timeout-ms < 50                 => REFUSED (exit 4)
#   --remote-max-results > 100               => REFUSED (exit 5)
#   --project empty                          => REFUSED (exit 6)
#
# Usage
#   powershell -ExecutionPolicy Bypass -File MCP_REMOTE_QUERY.ps1 `
#     -ServerName zen-mcp-server `
#     -Query "find transcript about widgets" `
#     -Project default `
#     [-RegistryPath C:\path\registry.json] `
#     [-RemoteTimeoutMs 1500] `
#     [-RemoteMaxResults 25] `
#     [-AuditOut MCP_QUERY_AUDIT.log] `
#     [-DryRun]
# ============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$ServerName,
    [Parameter(Mandatory=$true)][string]$Query,
    [Parameter(Mandatory=$true)][string]$Project,
    [Parameter(Mandatory=$false)][string]$RegistryPath = (Join-Path $HOME '.config/mcp/registry.json'),
    [Parameter(Mandatory=$false)][int]$RemoteTimeoutMs = 1500,
    [Parameter(Mandatory=$false)][int]$RemoteMaxResults = 25,
    [Parameter(Mandatory=$false)][string]$AuditOut = (Join-Path $HOME 'MCP_QUERY_AUDIT.log'),
    [Parameter(Mandatory=$false)][switch]$DryRun
)

# ---------------------------------------------------------------------------
# Golden Rules baked in
# ---------------------------------------------------------------------------
$GOLDEN_RULES = @(
    'ADDITIVE ONLY — registry is read-only; audit log is append-only.',
    'Personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are NEVER picked as registry path or audit-out path.'
)
$PERSONAL_FOLDERS = @('Documents','Downloads','Pictures','Videos','Music','Desktop','OneDrive','ARCHIVE_OLD')

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

function Append-AuditLine {
    param([string]$Path, [string]$Line)
    Add-Content -LiteralPath $Path -Value $Line -Encoding UTF8
}

function Read-RegistryServerEntry {
    param([string]$RegistryPath, [string]$ServerName)
    $raw = Get-Content -LiteralPath $RegistryPath -Raw -Encoding UTF8
    $obj = $raw | ConvertFrom-Json
    foreach ($e in $obj.servers) {
        if ($e.name -eq $ServerName) { return $e }
    }
    return $null
}

function Invoke-RemoteSearch {
    param(
        [Parameter(Mandatory=$true)][string]$Endpoint,
        [Parameter(Mandatory=$true)][string]$Query,
        [Parameter(Mandatory=$true)][string]$Project,
        [Parameter(Mandatory=$true)][int]$TimeoutMs,
        [Parameter(Mandatory=$true)][int]$MaxResults
    )
    # Stub corpus requires the operator to wire a real OMNI endpoint here.
    try {
        $body = @{
          query       = $Query
          project_id  = $Project
          max_results = $MaxResults
        } | ConvertTo-Json -Compress -Depth 5
        $resp = Invoke-WebRequest -Uri "$Endpoint/search" -Method POST -Body $body -ContentType 'application/json' -TimeoutSec ($TimeoutMs / 1000.0) -UseBasicParsing -ErrorAction Stop
        return @{ ok = $true; status = $resp.StatusCode; bytes = $resp.Content.Length }
    } catch {
        return @{ ok = $false; status = -1; error = $_.Exception.Message }
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function Invoke-RemoteQuery {
    [CmdletBinding()]
    param()
    if (Test-InPersonal -Path $RegistryPath) {
        [Console]::Error.WriteLine("REFUSED: registry path '$RegistryPath' resolves inside a Rule #8 personal folder.")
        return 2
    }
    if (Test-InPersonal -Path $AuditOut) {
        [Console]::Error.WriteLine("REFUSED: audit-out path '$AuditOut' resolves inside a Rule #8 personal folder.")
        return 2
    }
    if (-not (Test-Path -LiteralPath $RegistryPath)) {
        [Console]::Error.WriteLine("REFUSED: registry not found at '$RegistryPath'. Build it first.")
        return 3
    }
    if ($RemoteTimeoutMs -lt 50) {
        [Console]::Error.WriteLine("REFUSED: --remote-timeout-ms < 50 risks zero-timeout stalls.")
        return 4
    }
    if ($RemoteMaxResults -gt 100) {
        [Console]::Error.WriteLine("REFUSED: --remote-max-results > 100 risks overshoot. Cap at 100.")
        return 5
    }
    if ([string]::IsNullOrWhiteSpace($Project)) {
        [Console]::Error.WriteLine("REFUSED: --project is required (Phase G mandate).")
        return 6
    }

    $entry = Read-RegistryServerEntry -RegistryPath $RegistryPath -ServerName $ServerName
    if ($null -eq $entry) {
        [Console]::Error.WriteLine("REFUSED: --server '$ServerName' not in registry.")
        return 3
    }

    $ts = Get-IsoNow

    if ($DryRun) {
        $line = "$ts | event=federation_search_dryrun | server=$ServerName | endpoint=$($entry.endpoint) | project=$Project | timeout_ms=$RemoteTimeoutMs | max_results=$RemoteMaxResults"
        Write-Host "DRY-RUN: would append -> $AuditOut"
        Write-Host "         $line"
        return 0
    }

    $r = Invoke-RemoteSearch -Endpoint $entry.endpoint -Query $Query -Project $Project -TimeoutMs $RemoteTimeoutMs -MaxResults $RemoteMaxResults
    $statusLine = if ($r.ok) { "ok=true | status=$($r.status) | bytes=$($r.bytes)" } else { "ok=false | status=$($r.status) | error=$($r.error)" }
    $line = "$ts | event=federation_search | server=$ServerName | endpoint=$($entry.endpoint) | project=$Project | timeout_ms=$RemoteTimeoutMs | max_results=$RemoteMaxResults | result=$statusLine"
    Append-AuditLine -Path $AuditOut -Line $line

    Write-Host "MCP_REMOTE_QUERY: appended -> $AuditOut"
    return $(if ($r.ok) { 0 } else { 7 })
}

# Entry point
try {
    $rc = Invoke-RemoteQuery
    exit $rc
} catch {
    [Console]::Error.WriteLine("MCP_REMOTE_QUERY: $($_.Exception.Message)")
    exit 8
}
