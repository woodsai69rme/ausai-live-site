# ============================================================================
# MCP_HOST_CONNECTOR.ps1 — first concrete MCP host-side adapter
# ----------------------------------------------------------------------------
# Purpose
#   Provide a single, additive PowerShell entrypoint that mounts an MCP server
#   listed in MCP_REGISTRY.md, performs a health-check, and (optionally)
#   registers it for downstream Project Brain tooling.
#
# Source of truth
#   ~/.config/mcp/registry.json (or $MCP_REGISTRY_PATH if set).
#   Built by hand off MCP_REGISTRY.md; this script reads it.
#
# Behaviour
#   - Reads (NEVER writes) the registry.
#   - Performs GET <endpoint>/health with a 5s timeout.
#   - Appends ONE line per call to MCP_HOST_HEALTH_LOG (default:
#       $HOME/MCP_HOST_HEALTH.log); no rotation needed; per-day offset.
#   - Idempotent: re-running safe — no state files created on success.
#
# Compliance
#   ADDITIVE ONLY. Never deletes. Never rewrites prior scripts / docs.
#   Personal-folder guard: refuses any root inside Documents, Downloads,
#   Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
#
# Usage
#   powershell -ExecutionPolicy Bypass -File MCP_HOST_CONNECTOR.ps1 `
#       -ServerName zen-mcp-server `
#       [-DryRun]`
#       [-LogPath C:\path\to\MCP_HOST_HEALTH.log]
# ============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$ServerName,

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [string]$LogPath = (Join-Path $HOME 'MCP_HOST_HEALTH.log')
)

# ---------------------------------------------------------------------------
# Golden Rules baked in
# ---------------------------------------------------------------------------
$GOLDEN_RULES = @(
    'ADDITIVE ONLY — never delete or rewrite anything that already exists.',
    'Personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are NEVER touched for write; presence-only reads allowed.'
)
$PERSONAL_FOLDERS = @(
    'Documents', 'Downloads', 'Pictures', 'Videos', 'Music', 'Desktop', 'OneDrive', 'ARCHIVE_OLD'
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Test-InPersonal {
    param([string]$Path)
    if (-not $Path) { return $false }
    $normalized = $Path.Replace('\', '/').TrimEnd('/')
    foreach ($pf in $PERSONAL_FOLDERS) {
        if ($normalized -like "*/$pf" -or $normalized -like "*/$pf/*" -or $normalized -match "[\\/]$pf$") {
            return $true
        }
    }
    return $false
}

function Read-McpRegistry {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Registry not found at: $Path. Run Build-McpRegistry.ps1 first or set MCP_REGISTRY_PATH."
    }
    # Read-only parse — no writes.
    try {
        $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
        $obj = $raw | ConvertFrom-Json
        return $obj
    }
    catch {
        throw "Registry parse failed at: $Path. $($_.Exception.Message)"
    }
}

function Resolve-ServerEndpoint {
    param([object]$Registry, [string]$Name)
    $entry = $null
    foreach ($e in $Registry.servers) {
        if ($e.name -eq $Name) {
            $entry = $e
            break
        }
    }
    if (-not $entry) {
        throw "Server '$Name' not found in registry."
    }
    return $entry
}

function Invoke-HealthCheck {
    param(
        [Parameter(Mandatory=$true)][string]$Url,
        [Parameter(Mandatory=$true)][int]$TimeoutSeconds
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec $TimeoutSeconds -UseBasicParsing -ErrorAction Stop
        return @{ ok = $true; status = $response.StatusCode; body_excerpt = ($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length))) }
    }
    catch {
        return @{ ok = $false; status = -1; error = $_.Exception.Message }
    }
}

function Append-HealthLog {
    param(
        [Parameter(Mandatory=$true)][string]$LogPath,
        [Parameter(Mandatory=$true)][string]$Line
    )
    # Append-only. No truncation. No rotation. Pure additive.
    Add-Content -LiteralPath $LogPath -Value $Line -Encoding UTF8
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function Invoke-McpHostConnector {
    [CmdletBinding()]
    param()

    $RegistryPath = $env:MCP_REGISTRY_PATH
    if (-not $RegistryPath) {
        $RegistryPath = Join-Path $HOME '.config/mcp/registry.json'
    }

    Write-Host "MCP_HOST_CONNECTOR: registry=$RegistryPath server=$ServerName dry_run=$DryRun"

    # Personal-folder guard for the registry path itself.
    if (Test-InPersonal -Path $RegistryPath) {
        throw "REFUSED: registry path '$RegistryPath' resolves inside a Rule #8 personal folder. Set MCP_REGISTRY_PATH to a non-personal location and re-run."
    }
    if (Test-InPersonal -Path $LogPath) {
        throw "REFUSED: log path '$LogPath' resolves inside a Rule #8 personal folder."
    }

    # Read-only parse of the registry.
    $Registry = Read-McpRegistry -Path $RegistryPath
    $Entry = Resolve-ServerEndpoint -Registry $Registry -Name $ServerName

    $HealthUrl = "$($Entry.endpoint.TrimEnd('/'))/health"
    Write-Host "MCP_HOST_CONNECTOR: GET $HealthUrl (timeout 5s)"

    if ($DryRun) {
        Write-Host "DRY-RUN: would perform GET $HealthUrl and append one audit line."
        return 0
    }

    $h = Invoke-HealthCheck -Url $HealthUrl -TimeoutSeconds 5
    $ts = (Get-Date).ToUniversalTime().ToString('o')
    if ($h.ok) {
        $line = "$ts | ok=$($h.ok) | status=$($h.status) | server=$ServerName | endpoint=$($Entry.endpoint) | bytes_shown=$(([byte[]][char[]]$h.body_excerpt).Count)"
    } else {
        $line = "$ts | ok=$($h.ok) | status=$($h.status) | server=$ServerName | endpoint=$($Entry.endpoint) | error=$($h.error)"
    }
    Append-HealthLog -LogPath $LogPath -Line $line

    Write-Host "MCP_HOST_CONNECTOR: appended -> $LogPath"
    if ($h.ok) {
        return 0
    }
    return 1
}

# Entry point
try {
    $rc = Invoke-McpHostConnector
    exit $rc
}
catch {
    [Console]::Error.WriteLine("MCP_HOST_CONNECTOR: $_.Exception.Message")
    exit 2
}
