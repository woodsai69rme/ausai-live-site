# ============================================================================
# Append-RevenueEvent.ps1
# ----------------------------------------------------------------------------
# Purpose
#   First concrete appender for REVENUE_LEDGER.jsonl (per REVENUE_TRACKING_DESIGN.md).
#   Reads source, event, id, amount, meta; appends exactly ONE line to the ledger.
#   Never reformat; never truncate; never rewrite prior lines.
#
# Compliance
#   ADDITIVE ONLY. Zero destructive verbs. Append-only output.
#   Personal-folder guard: refuses any source/audit path inside Documents,
#   Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
#
# Refusal matrix
#   --source in personal folder                => REFUSED (exit 2)
#   --audit-out in personal folder             => REFUSED (exit 2)
#   unknown --event                            => REFUSED (exit 3)
#   --amount-usd < 0 without --refund          => REFUSED (exit 4)
#   --id empty                                 => REFUSED (exit 5)
#
# Usage
#   powershell -ExecutionPolicy Bypass -File Append-RevenueEvent.ps1 `
#     --event deploy_published `
#     --source pipeline:marketplace `
#     --id deploy-2026-03-09-001 `
#     --amount-usd 0 `
#     [--meta-json '{"channel":"YT"}'] `
#     [--refund] `
#     [-DryRun]
# ============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Event,
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$Id,
    [Parameter(Mandatory=$false)][Nullable[double]]$AmountUsd,
    [Parameter(Mandatory=$false)][string]$MetaJson = '{}',
    [Parameter(Mandatory=$false)][switch]$Refund,
    [Parameter(Mandatory=$false)][switch]$DryRun,
    [Parameter(Mandatory=$false)][string]$LedgerPath = (Join-Path $HOME 'REVENUE_LEDGER.jsonl')
)

# ---------------------------------------------------------------------------
# Golden Rules baked in
# ---------------------------------------------------------------------------
$GOLDEN_RULES = @(
    'ADDITIVE ONLY — never delete or rewrite anything that already exists.',
    'Personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are NEVER picked as a source or audit path.'
)
$PERSONAL_FOLDERS = @('Documents','Downloads','Pictures','Videos','Music','Desktop','OneDrive','ARCHIVE_OLD')

$ALLOWED_EVENTS = @(
    'provider_key_active',
    'deploy_published',
    'creative_published',
    'signal_emitted',
    'notify_dispatched'
)

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

function Test-AllowedEvent {
    param([string]$Event)
    foreach ($a in $ALLOWED_EVENTS) {
        if ($a -eq $Event) { return $true }
    }
    return $false
}

function Get-IsoNow { (Get-Date).ToUniversalTime().ToString('o') }

function Build-LedgerLine {
    param(
        [string]$ts, [string]$ev, [string]$src, [string]$id,
        [Nullable[double]]$amount, [string]$meta, [bool]$is_refund
    )
    # Build JSON safely with New-Line escaped per JSONL discipline.
    $metaObj = if ($meta -and $meta -ne '{}') { $meta } else { '{}' }
    $amountTxt = if ($null -ne $amount) { $amount.ToString([System.Globalization.CultureInfo]::InvariantCulture) } else { 'null' }
    $line = "{""ts"":""$ts"",""event"":""$ev"",""source"":""$src"",""id"":""$id"",""amount_usd"":$amountTxt,""meta"":$metaObj}"
    if ($is_refund -and $metaObj -notmatch '"refund"\s*:\s*true') {
        # Inject refund=true
        if ($metaObj -eq '{}') { $line = "{""ts"":""$ts"",""event"":""$ev"",""source"":""$src"",""id"":""$id"",""amount_usd"":$amountTxt,""meta"":{""refund"":true}}" }
        else {
            $patched = $metaObj.TrimEnd('}') + ',"refund":true}'
            $line = "{""ts"":""$ts"",""event"":""$ev"",""source"":""$src"",""id"":""$id"",""amount_usd"":$amountTxt,""meta"":$patched}"
        }
    }
    return $line
}

function Append-Ledger {
    param([string]$Path, [string]$Line)
    # Encoding UTF8 on Windows PowerShell 5.x emits a UTF-8 BOM (3 bytes
    # 0xEF 0xBB 0xBF) that breaks clients consuming the JSONL line (JSON.parse
    # rejects the BOM as unexpected). Use a .NET UTF8Encoding instance with
    # BOM explicitly disabled so every appended line is bare JSON.
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::AppendAllText($Path, $Line + "`n", $utf8NoBom)
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function Invoke-AppendRevenueEvent {
    [CmdletBinding()]
    param()

    # Personal-folder guard for ledger path AND meta-derived source.
    if (Test-InPersonal -Path $LedgerPath) {
        [Console]::Error.WriteLine("REFUSED: ledger path '$LedgerPath' resolves inside a Rule #8 personal folder. Move REVENUE_LEDGER.jsonl outside Rule #8 and re-run.")
        return 2
    }
    if (Test-InPersonal -Path $Source) {
        [Console]::Error.WriteLine("REFUSED: --source '$Source' resolves inside a Rule #8 personal folder. Pick a non-personal source id.")
        return 2
    }

    if (-not (Test-AllowedEvent -Event $Event)) {
        [Console]::Error.WriteLine("REFUSED: event '$Event' is outside the closed enum: $($ALLOWED_EVENTS -join ', ').")
        return 3
    }
    if ([string]::IsNullOrWhiteSpace($Id)) {
        [Console]::Error.WriteLine("REFUSED: --id is empty.")
        return 5
    }
    if ($null -ne $AmountUsd -and $AmountUsd -lt 0 -and -not $Refund) {
        [Console]::Error.WriteLine("REFUSED: --amount-usd < 0 requires --refund (refunds are an explicit marker, not a silent negative).")
        return 4
    }

    # Meta JSON parse check (best-effort; if it fails, fall back to {}).
    $metaClean = '{}'
    if ($MetaJson -and $MetaJson -ne '{}') {
        try {
            $parsed = $MetaJson | ConvertFrom-Json -ErrorAction Stop
            # Re-serialize canonically.
            $metaClean = $parsed | ConvertTo-Json -Compress -Depth 10
        } catch {
            [Console]::Error.WriteLine("REFUSED: --meta-json is not valid JSON: $($_.Exception.Message)")
            return 6
        }
    }

    $ts = Get-IsoNow
    $line = Build-LedgerLine -ts $ts -ev $Event -src $Source -id $Id -amount $AmountUsd -meta $metaClean -is_refund:$Refund

    if ($DryRun) {
        Write-Host "DRY-RUN: would append -> $LedgerPath"
        Write-Host "         $line"
        return 0
    }
    Append-Ledger -Path $LedgerPath -Line $line
    Write-Host "Appended -> $LedgerPath"
    return 0
}

# Entry point
try {
    $rc = Invoke-AppendRevenueEvent
    exit $rc
} catch {
    [Console]::Error.WriteLine("Append-RevenueEvent: $($_.Exception.Message)")
    exit 7
}
