#requires -Version 5.1
$ErrorActionPreference = 'Continue'
Write-Host '==== Chrome Remote Desktop + Taskbar diagnostic ===='
Write-Host ('User:                  {0}' -f $env:USERNAME)
Write-Host ('Session:               {0}' -f ([System.Diagnostics.Process]::GetCurrentProcess().SessionId))
Write-Host ('Machine:               {0}' -f $env:COMPUTERNAME)
Write-Host ''

Write-Host '--- CRD service (chromoting) ---'
try {
    $svc = Get-CimInstance Win32_Service -Filter "Name='chromoting'" -ErrorAction Stop
    if ($svc) {
        $svc | Format-List Name, DisplayName, Status, StartMode, DelayedAutoStart, StartName, PathName
    }
} catch {
    Write-Host 'chromoting service MISSING on this machine'
}

Write-Host '---  All Chrome / CRD runnin processes ---'
Get-Process | Where-Object {
    $_.Name -match '^(chromoting|chrome-remote-desktop|remoting|chrome)$' -or
    ($_.Name -like '*chrome*' -and $_.Path -like '*Chrome Remote Desktop*')
} | Sort-Object Id | Select-Object Id, Name, Path, StartTime | Format-Table -AutoSize | Out-String | Write-Host

Write-Host '--- CRD install / binary paths ---'
$paths = @(
    'C:\Program Files\Google\Chrome Remote Desktop',
    'C:\Program Files (x86)\Google\Chrome Remote Desktop',
    (Join-Path $env:ProgramFiles 'Google\Chrome Remote Desktop'),
    (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome Remote Desktop')
)
foreach ($p in $paths) {
    if (Test-Path $p) {
        Write-Host ('FOUND: {0}' -f $p)
        Get-ChildItem $p -Recurse -Filter '*.exe' -ErrorAction SilentlyContinue |
            Select-Object FullName | Format-Table -AutoSize | Out-String | Write-Host
    } else {
        Write-Host ('not found: {0}' -f $p)
    }
}

Write-Host '--- Taskbar visibility flags ---'
$adv = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
$props = Get-ItemProperty $adv -ErrorAction SilentlyContinue
Write-Host ('TaskbarAutoHide      : {0}' -f $props.TaskbarAutoHide)
Write-Host ('TaskbarSmallIcons    : {0}' -f $props.TaskbarSmallIcons)
Write-Host ('ShowTaskViewButton   : {0}' -f $props.ShowTaskViewButton)
Write-Host ('MMTaskbarEnabled     : {0}' -f $props.MMTaskbarEnabled)
Write-Host ('TaskbarSd            : {0}' -f $props.TaskbarSd)

Write-Host '--- StuckRects3 (Taskbar placement: bottom/top/left/right + visibility) ---'
$sr = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3'
if (Test-Path $sr) {
    $bytes = (Get-ItemProperty $sr).Settings
    if ($bytes) {
        Write-Host ('Settings bytes       : {0}' -f ([BitConverter]::ToString($bytes)))
        # Bytes 8..11 are the position struct; byte 12 is the visibility flag (1 = auto-hide)
        if ($bytes.Length -ge 13) {
            Write-Host ('AutoHide flag        : {0}' -f $bytes[8])
        }
    } else {
        Write-Host 'StuckRects3 empty'
    }
} else {
    Write-Host 'StuckRects3 KEY missing'
}

Write-Host '--- Monitors ---'
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object {
    Write-Host ('  {0}  bounds=({1},{2}) -> ({3},{4})  primary={5}' -f `
        $_.DeviceName, $_.Bounds.X, $_.Bounds.Y, $_.Bounds.Right, $_.Bounds.Bottom, $_.Primary)
}

Write-Host '--- Explorer health ---'
Get-Process explorer -ErrorAction SilentlyContinue |
    Select-Object Id, Name, StartTime, @{N='Responding';E={$_.Responding}} |
    Format-Table -AutoSize | Out-String | Write-Host

Write-Host '--- Active fullscreen / topmost windows owned by explorer ---'
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$hwnd = [Win]::GetForegroundWindow()
$text = New-Object System.Text.StringBuilder 512
[Win]::GetWindowText($hwnd, $text, 512) | Out-Null
Write-Host ('Foreground hWnd       : {0}' -f $hwnd)
Write-Host ('Foreground title      : {0}' -f $text.ToString())
Write-Host ('')
