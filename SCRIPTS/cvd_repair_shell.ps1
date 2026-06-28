# ===============================================================
#  cvd_repair_shell.ps1
#  Aggressive shell recovery for: no taskbar AND no Start menu.
#  REQUIRES RUN-AS-ADMINISTRATOR.
#
#  Sequence:
#    1. End known shell-extension killer processes
#    2. Hard-kill explorer.exe
#    3. Reset-AppxPackage the XAML shell hosts
#    4. Re-launch explorer.exe
#    5. Verify Shell_TrayWnd is visible
# ===============================================================
# All kill/reset/etc. are non-fatal so a second invocation after a successful first one does not throw.
$ErrorActionPreference = 'SilentlyContinue'

function Step($label, [scriptblock]$body) {
    Write-Host ''
    Write-Host "--- $label ---" -ForegroundColor Cyan
    # No try/catch: $ErrorActionPreference is SilentlyContinue, so any error is
    # already swallowed before the catch handler could see it. The body runs
    # straight through; visible failures print their own -ForegroundColor output.
    & $body
}

Step '1/5  Ending known shell-extension killers (helper exes + poll-loop)' {
    $killerNames = 'TranslucentTB','TranslucentTB.Server','StartAllBack','Startallback64','StartAllBackX','DisplayFusion','DesktopOK'
    for ($i = 0; $i -lt 6; $i++) {
        $alive = Get-Process -Name $killerNames -ErrorAction SilentlyContinue
        if (-not $alive) { break }
        $alive | ForEach-Object {
            Write-Host ("    Killing {0} (PID {1})" -f $_.Name, $_.Id)
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 1
    }
    Write-Host "    (If any helper installs as a Windows service, also run:  Stop-Service -Name <ServiceName>.)"
}

Step '2/5  Hard-killing explorer.exe' {
    Get-Process explorer -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Host ("    Stopping explorer.exe (PID {0})" -f $_.Id)
            Stop-Process -Id $_.Id -Force
        }
    Start-Sleep -Seconds 2
}

Step '3/5  Reset-AppxPackage shell XAML hosts' {
    # -ForceApplicationShutdown is REQUIRED -- without it Reset-AppxPackage silently
    # no-ops when a live process still holds the package registration.
    foreach ($pkg in 'Microsoft.Windows.ShellExperienceHost',
                     'Microsoft.Windows.StartMenuExperienceHost',
                     'Microsoft.Windows.SearchApp',
                     'Microsoft.Windows.Cortana') {
        $ap = Get-AppxPackage $pkg -ErrorAction SilentlyContinue
        if ($ap) {
            Write-Host ("    Resetting {0} (-ForceApplicationShutdown) ..." -f $pkg)
            $ap | Reset-AppxPackage -ForceApplicationShutdown -ErrorAction SilentlyContinue
            foreach ($a in @($ap)) {
                if ($a.InstallLocation -and (Test-Path $a.InstallLocation)) {
                    Add-AppxPackage -DisableDevelopmentMode -ForceApplicationShutdown `
                        -Register (Join-Path $a.InstallLocation 'AppXManifest.xml') `
                        -ErrorAction SilentlyContinue 2>$null | Out-Null
                }
            }
        } else {
            Write-Host ("    {0}: not installed" -f $pkg)
        }
    }
}

Step '4/5  Re-launching explorer.exe (poll until back)' {
    Start-Process explorer.exe
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 1
        $e = Get-Process explorer -ErrorAction SilentlyContinue
        if ($e) {
            Write-Host ("    explorer.exe relaunched (PID {0} after {1}s)" -f $e[0].Id, ($i + 1))
            break
        }
    }
    if (-not $e) {
        Write-Host "    WARNING: explorer.exe did not come back within 20s." -ForegroundColor Yellow
    }
}

Step '5/5  Verifying Shell_TrayWnd (primary + secondary) is on-screen' {
    if (-not ('TrayCheck' -as [type])) {
        Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class TrayCheck {
    [DllImport("user32.dll")] public static extern IntPtr FindWindow(string c, string n);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern int  GetClassName(IntPtr h, StringBuilder s, int nMax);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc lpEnumFunc, IntPtr lParam);
    public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left,Top,Right,Bottom; }
}
"@
    }
    # Tally both primary and secondary taskbar class names -- multi-monitor
    # hosts a secondary tray on each display.
    $results = @()
    $cb = [TrayCheck+EnumProc]{
        param($h, $l)
        $sb = New-Object System.Text.StringBuilder 128
        [TrayCheck]::GetClassName($h, $sb, 128) | Out-Null
        if ($sb.ToString() -in 'Shell_TrayWnd','Shell_SecondaryTrayWnd') {
            [TrayCheck+RECT]$r = New-Object TrayCheck+RECT
            [TrayCheck]::GetWindowRect($h, [ref]$r) | Out-Null
            $script:results += [pscustomobject]@{
                Class      = $sb.ToString()
                Hwnd       = $h
                Visible    = [TrayCheck]::IsWindowVisible($h)
                Left       = $r.Left
                Top        = $r.Top
                Right      = $r.Right
                Bottom     = $r.Bottom
            }
        }
        return $true
    }
    [TrayCheck]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null

    if (-not $results) {
        Write-Host "    No taskbar window class found -- explorer did not register a tray." -ForegroundColor Red
    } else {
        $results | Format-Table -AutoSize | Out-String | Write-Host
        $onScreen = $results | Where-Object { $_.Visible -and $_.Right -gt $_.Left -and $_.Bottom -gt $_.Top }
        if ($onScreen) {
            Write-Host "    OK --- taskbar ON-SCREEN." -ForegroundColor Green
        } else {
            Write-Host "    WARNING: tray class is registered but not on-screen (broken host or off-screen coordinate)." -ForegroundColor Yellow
        }
    }
}

Write-Host ''
Write-Host 'Next steps if this did not bring everything back:' -ForegroundColor Cyan
Write-Host '  1. Reboot the machine -- some Start-menu XAML state cannot be re-established without a full boot.'
Write-Host '  2. If Start menu still missing after reboot, in elevated cmd run:'
Write-Host '       sfc /scannow'
Write-Host '       Dism /Online /Cleanup-Image /RestoreHealth'
Write-Host '  3. If just Start menu is gone (taskbar is back): clear user package cache and reboot.'
Write-Host '       Ren C:\Users\karma\AppData\Local\Packages\Microsoft.Windows.StartMenuExperienceHost_*\LocalCache'
Write-Host '  4. Last resort:  Ren-Item HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer Explorer.old - then re-launch explorer.exe.'

