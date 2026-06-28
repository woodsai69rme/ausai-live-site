# ===== Part A: CRD service + processes + files =====
$ErrorActionPreference = 'Continue'

Write-Host '==== CRD service / process / file diagnostic ===='
Write-Host ('User      : {0}' -f $env:USERNAME)
Write-Host ('Session   : {0}' -f ([System.Diagnostics.Process]::GetCurrentProcess().SessionId))
Write-Host ('Machine   : {0}' -f $env:COMPUTERNAME)
Write-Host ''

Write-Host '--- CRD service (chromoting) ---'
$s = Get-CimInstance Win32_Service -Filter "Name='chromoting'" -ErrorAction SilentlyContinue
if ($s) {
    $s | Format-List Name, DisplayName, Status, StartMode, DelayedAutoStart, StartName | Out-String | Write-Host
} else {
    Write-Host 'chromoting service NOT installed on this machine.'
}

Write-Host '--- All Chrome-family runnin processes ---'
Get-Process | Where-Object {
    $_.Name -match '^chromoting$|chrome-remote-desktop|^remoting' -or
    ($_.Path -and $_.Path -like '*Chrome Remote Desktop*')
} | Sort-Object Id | Format-Table Id, Name, @{N='Path';E={ Split-Path $_.Path -Leaf }}, StartTime -AutoSize | Out-String | Write-Host

Write-Host '--- CRD install paths ---'
foreach ($p in @(
    'C:\Program Files\Google\Chrome Remote Desktop',
    'C:\Program Files (x86)\Google\Chrome Remote Desktop',
    (Join-Path $env:ProgramFiles 'Google\Chrome Remote Desktop')
)) {
    if (Test-Path $p) {
        Write-Host ('FOUND  : {0}' -f $p)
        Get-ChildItem $p -Filter '*.exe' -ErrorAction SilentlyContinue |
            Format-Table FullName -AutoSize | Out-String | Write-Host
    } else {
        Write-Host ('absent : {0}' -f $p)
    }
}
