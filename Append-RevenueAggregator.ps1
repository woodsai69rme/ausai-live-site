# ============================================================================
# Append-RevenueAggregator.ps1
# ----------------------------------------------------------------------------
# Purpose
#   Sister script to Append-RevenueEvent.ps1. Reads REVENUE_LEDGER.jsonl
#   (read-only) and appends ONE section per invocation to REVENUE_SUMMARY.md.
#   The summary groups events by (event-kind, month) and reports total
#   count + realized amount (where available).
#
# Compliance
#   ADDITIVE ONLY. Zero destructive verbs. The ledger is read-mostly; the
#   summary grows append-only; never truncates; never regresses.
#   Personal-folder guard: refuses any --ledger-path or --summary-path
#   inside Documents, Downloads, Pictures, Videos, Music, Desktop,
#   OneDrive, Downloads\ARCHIVE_OLD.
#
# Refusal matrix
#   --ledger-path in personal folder       => REFUSED (exit 2)
#   --summary-path in personal folder      => REFUSED (exit 2)
#   --ledger-path not found                => REFUSED (exit 3)
#   malformed ledger line                  => audit continued + skip row
#
# Usage
#   powershell -ExecutionPolicy Bypass -File Append-RevenueAggregator.ps1 `
#     -LedgerPath REVENUE_LEDGER.jsonl `
#     -SummaryPath REVENUE_SUMMARY.md `
#     [-RunId custom-id]
# ============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)][string]$LedgerPath = (Join-Path $HOME 'REVENUE_LEDGER.jsonl'),
    [Parameter(Mandatory=$false)][string]$SummaryPath = (Join-Path $HOME 'REVENUE_SUMMARY.md'),
    [Parameter(Mandatory=$false)][string]$RunId = ([Guid]::NewGuid().ToString('N').Substring(0,8))
)

# ---------------------------------------------------------------------------
# Golden Rules baked in
# ---------------------------------------------------------------------------
$GOLDEN_RULES = @(
    'ADDITIVE ONLY — ledger is read-only; summary is append-only.',
    'Personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are NEVER picked as ledger or summary path.'
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

function Append-SummarySection {
    param([string]$SummaryPath, [string]$Section)
    # Encoding UTF8 on Windows PowerShell 5.x emits a UTF-8 BOM (3 bytes
    # 0xEF 0xBB 0xBF). Use a .NET UTF8Encoding instance with BOM explicitly
    # disabled so REVENUE_SUMMARY.md stays BOM-free (markdown consumers and
    # future diff/grep tools should not collide with a BOM prefix).
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::AppendAllText($SummaryPath, $Section, $utf8NoBom)
}

function Get-IsoNow { (Get-Date).ToUniversalTime().ToString('o') }

function Get-MonthBucket {
    # Takes an ISO timestamp; returns YYYY-MM.
    param([string]$IsoTs)
    if ($IsoTs -match '^(\d{4})-(\d{2})') { return "$($Matches[1])-$($Matches[2])" }
    return 'unknown'
}

function Parse-LedgerLine {
    # Returns a hashtable of best-effort fields from a ledger JSON line.
    param([string]$Line)
    try {
        $obj = $Line | ConvertFrom-Json -ErrorAction Stop
        return @{
          ts          = [string]$obj.ts
          event       = [string]$obj.event
          source      = [string]$obj.source
          id          = [string]$obj.id
          amount_usd  = if ($null -ne $obj.amount_usd) { [double]$obj.amount_usd } else { $null }
          meta        = $obj.meta
        }
    } catch {
        return $null  # Malformed lines are skipped (audit).
    }
}

# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------
function Invoke-Aggregate {
    [CmdletBinding()]
    param()
    if (Test-InPersonal -Path $LedgerPath) {
        [Console]::Error.WriteLine("REFUSED: ledger path '$LedgerPath' resolves inside a Rule #8 personal folder.")
        return 2
    }
    if (Test-InPersonal -Path $SummaryPath) {
        [Console]::Error.WriteLine("REFUSED: summary path '$SummaryPath' resolves inside a Rule #8 personal folder.")
        return 2
    }
    if (-not (Test-Path -LiteralPath $LedgerPath)) {
        [Console]::Error.WriteLine("REFUSED: ledger not found at '$LedgerPath'.")
        return 3
    }

    $lines = Get-Content -LiteralPath $LedgerPath -Encoding UTF8
    $groups = @{}   # key = "event|month" => @{count=N; sum=X; ids=@() }
    $malformed = 0
    $processed = 0

    foreach ($l in $lines) {
        if (-not $l) { continue }
        $record = Parse-LedgerLine -Line $l
        if ($null -eq $record) { $malformed++; continue }
        $month = Get-MonthBucket -IsoTs $record.ts
        $key = "$($record.event)|$month"
        if (-not $groups.ContainsKey($key)) {
            $groups[$key] = @{ count = 0; sum = 0.0; ids = @(); source = '' }
        }
        $groups[$key].count += 1
        if ($null -ne $record.amount_usd) { $groups[$key].sum += $record.amount_usd }
        $groups[$key].ids += $record.id
        if (-not $groups[$key].source) { $groups[$key].source = $record.source }
        $processed++
    }

    $ts = Get-IsoNow
    $section = @()
    $section += ""
    $section += "## Run $RunId @ $ts"
    $section += ""
    $section += "Aggregated $processed lines ($malformed malformed skipped)."
    $section += ""
    $section += "| event | month | count | sum (USD) | source sample |"
    $section += "| --- | --- | --- | --- | --- |"
    foreach ($key in ($groups.Keys | Sort-Object)) {
        $parts = $key -split '\|'
        $ev = $parts[0]
        $mo = $parts[1]
        $g = $groups[$key]
        $sourceTxt = if ($g.source) { $g.source } else { '-' }
        $sumTxt = ('{0:N4}' -f $g.sum)
        $section += "| $ev | $mo | $($g.count) | $sumTxt | $sourceTxt |"
    }
    Append-SummarySection -SummaryPath $SummaryPath -Section ($section -join "`n")

    Write-Host "Appended aggregator section run=$RunId to $SummaryPath (processed=$processed malformed=$malformed)"
    return 0
}

# Entry point
try {
    $rc = Invoke-Aggregate
    exit $rc
} catch {
    [Console]::Error.WriteLine("Append-RevenueAggregator: $($_.Exception.Message)")
    exit 4
}
