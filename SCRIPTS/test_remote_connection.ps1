# ===============================================================
#  test_remote_connection.ps1  --  read-only readiness probe for the
#  Chrome Remote Desktop (chromoting) host on this box.
#
#  What it checks (in order, with [OK]/[WARN]/[FAIL] tags):
#    1. chromoting service: installed, State, StartMode, PID, path
#    2. host enrollment file: present, parses, host id + email
#    3. CRD watchdog scheduled task: present, last run, log tail
#    4. DNS: remotedesktop.google.com resolves
#    5. TCP/443: Test-NetConnection to the canonical hostname
#    6. HTTPS HEAD probe on /access
#    7. Verdict line printed; $LASTEXITCODE-like value emitted via `exit N`
#
#  Exit codes:
#    0  all green
#    1  chromoting service missing or STOPPED
#    2  service running but StartMode != AUTO (no watchdog repair)
#    3  watchdog task missing (degrades but doesn't gate remote)
#    4  DNS resolution failed for remotedesktop.google.com
#    5  TCP/443 unreachable
#    6  HTTPS HEAD probe failed
#
#  Usage:
#    powershell -NoProfile -ExecutionPolicy Bypass -File test_remote_connection.ps1
#    .\test_remote_connection.bat                   <- from cmd
# ===============================================================

$ErrorActionPreference = 'SilentlyContinue'

# Match the host OEM codepage so any path captured from sc.exe renders
# cleanly under cmd or in any redirect-to-file consumer.
$OEM = [System.Text.Encoding]::GetEncoding(
    [System.Globalization.CultureInfo]::CurrentCulture.TextInfo.OEMCodePage)
[Console]::InputEncoding  = $OEM
[Console]::OutputEncoding = $OEM

# Highest-severity exit code observed across all sections. Always emits
# the WORST finding, never an early success.
$script:exitCode = 0

function Section {
    param([string]$Title)
    Write-Host ''
    Write-Host ("=== {0} ===" -f $Title) -ForegroundColor Cyan
}

function Status {
    param([string]$Verdict, [string]$Msg)
    $color = switch ($Verdict) {
        'OK'    { 'Green' }
        'WARN'  { 'Yellow' }
        'FAIL'  { 'Red' }
        default { 'Gray' }
    }
    $tag = ('[{0}]' -f $Verdict).PadRight(6)
    Write-Host "$tag $Msg" -ForegroundColor $color
}

function Elevate-Exit {
    param([int]$Code)
    if ($Code -gt $script:exitCode) { $script:exitCode = $Code }
}

# -----------------------------------------------------------------
Section 'chromoting service'

$svc = Get-CimInstance Win32_Service -Filter "Name='chromoting'" -ErrorAction SilentlyContinue
if (-not $svc) {
    # Continue without `return`: downstream sections (DNS, TCP/443, HTTPS) still
    # run so the user sees the full diagnostic picture. Top-of-file exit severity
    # picks the worst finding across all sections.
    Status 'FAIL' "chromoting service is NOT installed -- run the Google CRD host setup at https://remotedesktop.google.com/remote-access (cvd_taskbar_fix and install_crd_watchdog will not help; CRD host enrollment is required)"
    Elevate-Exit 1
}

$running = $svc.State -eq 'Running'
$auto    = $svc.StartMode -eq 'Auto'
$verdict = if ($running -and $auto) { 'OK' } elseif ($running) { 'WARN' } else { 'FAIL' }

$pathDisplay = if ($svc.PathName) { $svc.PathName } else { '(empty)' }
Status $verdict ("State: {0,-11} StartMode: {1,-12} PID: {2}" -f $svc.State, $svc.StartMode, $svc.ProcessId)
Write-Host "        Binary path:" -ForegroundColor Gray
Write-Host "          $pathDisplay" -ForegroundColor Gray

if (-not $running) { Elevate-Exit 1 }
elseif (-not $auto) { Elevate-Exit 2 }

# -----------------------------------------------------------------
Section 'CRD host enrollment (host.json)'

$hostJsonPath = 'C:\ProgramData\Google\Chrome Remote Desktop\host.json'
if (-not (Test-Path $hostJsonPath)) {
    Status 'WARN' "host.json missing at $hostJsonPath -- host setup incomplete"
    Elevate-Exit 1
} else {
    try {
        $h = Get-Content $hostJsonPath -Raw | ConvertFrom-Json -ErrorAction Stop
        $email   = $h.id        # Google account that enrolled
        $localId = $h.localId   # last-6 of the host id (matches the GUI URL)
        $name    = $h.name      # human-readable machine label
        if ($email -or $localId -or $name) {
            Status 'OK'    "host.json present"
            Write-Host "        Email       : $email" -ForegroundColor Gray
            Write-Host "        Local host ID: $localId" -ForegroundColor Gray
            Write-Host "        Display name: $name" -ForegroundColor Gray
        } else {
            Status 'WARN' "host.json present but no recognizable id/name fields -- may be a partial enrollment"
        }
    } catch {
        Status 'WARN' "host.json present but not valid JSON: $($_.Exception.Message)"
    }
}

# -----------------------------------------------------------------
Section 'CRD AutoStart Watchdog (scheduled task)'

$taskErr  = ''
$taskOut  = schtasks /query /tn "CRD AutoStart Watchdog" /v /fo LIST 2>&1 | ForEach-Object {
    if ($_ -is [System.Management.Automation.ErrorRecord]) { $taskErr += [string]$_ + '|' }
    else { $_ }
}
$taskExit = $LASTEXITCODE
if ($taskExit -ne 0) {
    if ($taskErr -match 'cannot find the file specified|does not exist') {
        Status 'WARN' "watchdog task NOT installed -- run scripts\install_crd_watchdog.bat as administrator to register it. (Start=AUTO invariant not protected.)"
    } elseif ($taskErr -match 'access|access is denied') {
        Status 'WARN' "watchdog present but query was ACCESS DENIED -- running from a regular user; right-click cmd and 'Run as administrator' to see details. (Start=AUTO invariant not protected.)"
    } else {
        Status 'WARN' ("watchdog query failed (schtasks exit {0}): {1}" -f $taskExit, $taskErr)
    }
    Elevate-Exit 3
} else {
    # schtasks /v /fo LIST prints each field on its own line as "FieldName: value".
    # Pull the four most useful fields for the user.
    # The `schtasks` capture above wrote to $taskOut; alias to $task for the
    # parser below (kept historical variable name to minimize diff churn).
    $task = $taskOut
    $taskLines = ($task -split "`r?`n") | Where-Object { $_ -match '^\s*(Run As User|Next Run Time|Last Run Result|Schedule Type|TaskName):' }
    foreach ($line in $taskLines) {
        Write-Host "        $line".TrimEnd() -ForegroundColor Gray
    }

    $lastRun = (($task -split "`r?`n") | Where-Object { $_ -match 'Last Run Result' }) -replace '.*:\s*', ''
    $lastRun = $lastRun.Trim()
    # Standard scheduled-task result codes:
    #   0      success
    #   267011 task hasn't run yet (fresh install)
    #   1      denied
    #   267014 task killed mid-run
    $isFreshInstall = $lastRun -eq '267011'
    if ($lastRun -eq '0' -or $isFreshInstall) {
        Status 'OK' "watchdog task installed and healthy"
    } else {
        Status 'WARN' "watchdog task installed but last run returned non-success code '$lastRun'"
    }
}

# -----------------------------------------------------------------
Section 'CRD-Watchdog log tail'

$logPath = 'C:\ProgramData\CRD-Watchdog\log.txt'
if (-not (Test-Path $logPath)) {
    Write-Host "        (no log present -- watch ..." -ForegroundColor DarkGray
    Write-Host "        the watchdog has not had to act yet)" -ForegroundColor DarkGray
} else {
    Get-Content $logPath -Tail 10 | ForEach-Object { Write-Host "        $_" -ForegroundColor Gray }
}

# -----------------------------------------------------------------
Section 'DNS resolution'

# CRD frontend host is the entrypoint for the access page. Its relay pool
# spans many IPs -- we don't enumerate them; we just confirm reachability.
$dnsAddrs = [System.Net.Dns]::GetHostAddresses('remotedesktop.google.com') | ForEach-Object { $_.IPAddressToString }
if (-not $dnsAddrs -or $dnsAddrs.Count -eq 0) {
    Status 'FAIL' "DNS resolution failed for remotedesktop.google.com -- outbound DNS likely blocked or offline"
    Elevate-Exit 4
} else {
    Status 'OK' "remotedesktop.google.com -> $($dnsAddrs -join ', ')"
}

# -----------------------------------------------------------------
Section 'TCP/443 reachability'

# Use a direct TcpClient.BeginConnect with a hard 5-second timeout instead
# of Test-NetConnection.  Test-NetConnection runs an ICMP ping before the
# TCP test, and a filtered egress can sit for ~10 s waiting on the timeout
# which makes the whole probe feel slow.  TcpClient + a small wait gives
# us a deterministic 5-second bound and no ICMP dependency.
$tcpOk      = $false
$remoteAddr = 'unknown'
$latencyMs  = -1
$client     = $null
try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $client    = New-Object System.Net.Sockets.TcpClient
    $iar       = $client.BeginConnect('remotedesktop.google.com', 443, $null, $null)
    $hit       = $iar.AsyncWaitHandle.WaitOne(5000)
    if ($hit) {
        $client.EndConnect($iar)
        $tcpOk      = $true
        $latencyMs  = [int]$stopwatch.ElapsedMilliseconds
        $remoteAddr = $client.RemoteEndPoint.ToString()
    } else {
        # Async path did not complete; cancel so we don't leak a half-open
        # socket on a slow / unreachable host.
        try { $client.Close() } catch {}
    }
} catch {
    # Socket error: name resolution failed on connect, RST, etc. Any state
    # we can't reach here will still be cleaned up by the finally block.
} finally {
    if ($client) {
        try { $client.Close() } catch {}
    }
}

if ($tcpOk) {
    Status 'OK'  ("TCP/443 reachable -- remote {0} latency {1} ms" -f $remoteAddr, $latencyMs)
} else {
    Status 'FAIL' "TCP/443 unreachable from this host within 5 s -- egress firewall likely blocking outbound HTTPS"
    Elevate-Exit 5
}

# -----------------------------------------------------------------
Section 'HTTPS HEAD probe on /access'

try {
    $req = Invoke-WebRequest -Method Head -UseBasicParsing -Uri 'https://remotedesktop.google.com/access' -TimeoutSec 10
    Status 'OK' ("HTTPS HEAD returned {0} {1} ({2} bytes response after redirect)" -f $req.StatusCode, $req.StatusDescription, $req.RawContentLength)
} catch {
    # HEAD to remotedesktop.google.com may be answered with a redirect to
    # a different host -- that's still proof of life; only hard network
    # failures count as WARN-or-better.
    $msg = $_.Exception.Message
    if ($msg -match '\b(200|301|302|307)\b') {
        Status 'OK' "HTTPS HEAD probe succeeded (redirect observed, network path is live)"
    } else {
        Status 'WARN' "HTTPS HEAD probe returned: $msg"
        Elevate-Exit 6
    }
}

# -----------------------------------------------------------------
Section 'Verdict'

if ($script:exitCode -eq 0) {
    Write-Host ''
    Status 'OK'  "Ready to receive incoming Chrome Remote Desktop connections"
    Write-Host ''
    Write-Host '  From any remote device, open https://remotedesktop.google.com/access,' -ForegroundColor Gray
    Write-Host "  sign in with the host's enrollment Google account (see 'Email' above)," -ForegroundColor Gray
    Write-Host '  click your machine, enter your 6+ digit CRD PIN.' -ForegroundColor Gray
} else {
    Write-Host ''
    Status 'WARN' ("One or more WARN/FAIL findings above. Exit code: {0}" -f $script:exitCode)
    Write-Host ''
    Write-Host '  Investigate each finding in reverse order before relying on remote access.' -ForegroundColor Gray
}

exit $script:exitCode
