# ===== Part B: Taskbar + explorer health =====
$ErrorActionPreference = 'Continue'

Write-Host '==== Taskbar / explorer health diagnostic ===='

Write-Host '--- Advanced flags ---'
$adv = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
$props = Get-ItemProperty $adv -ErrorAction SilentlyContinue
foreach ($k in 'TaskbarAutoHide','TaskbarSmallIcons','ShowTaskViewButton','MMTaskbarEnabled','TaskbarSd','StartButtons') {
    Write-Host (('  {0,-22} : {1}' -f $k, $props.$k))
}

Write-Host '--- StuckRects3 (taskbar on-screen placement + auto-hide flag) ---'
$sr = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3'
if (Test-Path $sr) {
    $bytes = (Get-ItemProperty $sr).Settings
    if ($bytes -and $bytes.Length -ge 16) {
        Write-Host ('  raw bytes           : {0}' -f ([BitConverter]::ToString($bytes)))
        Write-Host ('  byte[8]  auto-hide? : {0}  (1 = auto-hide enabled)' -f $bytes[8])
        Write-Host ('  byte[12] align/pos  : {0}  (0=left,1=top,2=right,3=bottom)' -f $bytes[12])
    } else {
        Write-Host '  StuckRects3.Settings empty or short'
    }
} else {
    Write-Host '  StuckRects3 KEY missing'
}

Write-Host ''
Write-Host '--- Explorer.exe ---'
Get-Process explorer -ErrorAction SilentlyContinue |
    Format-Table Id, Name, StartTime, @{N='Responding';E={$_.Responding}} -AutoSize | Out-String | Write-Host

Write-Host '--- Logical monitors (Win32_DesktopMonitor / VideoController) ---'
Get-CimInstance Win32_VideoController | ForEach-Object {
    $m = $_ | Select-Object Name, CurrentHorizontalResolution, CurrentVerticalResolution, AdapterCompatibility
    Write-Host ('  {0} {1}  {2}x{3}' -f $m.AdapterCompatibility, $m.Name, $m.CurrentHorizontalResolution, $m.CurrentVerticalResolution)
}

Write-Host '--- Recent Application errors linked to taskbar/explorer ---'
Get-WinEvent -LogName Application -MaxEvents 20 -ErrorAction SilentlyContinue |
    Where-Object { $_.ProviderName -match 'Application Error' -or $_.LevelDisplayName -eq 'Error' } |
    Select-Object TimeCreated, ProviderName, Id, @{N='Msg';E={ ($_.Message -split "`n")[0] }} |
    Format-Table -AutoSize -Wrap | Out-String | Write-Host
