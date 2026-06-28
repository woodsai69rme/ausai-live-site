# ===============================================================
#  crd_manager.ps1
#  Single-window GUI to manage the Chrome Remote Desktop service.
#  Lives in the system tray; clicking X hides the form, "Exit"
#  on the tray menu closes for real.
#
#  Run from crd_manager.bat (which sets -STA). Does NOT require
#  elevation; service stop/start will request elevation when needed.
#
#  Args:
#    -StartHidden   launch fully hidden (used by the shell:startup
#                   shortcut so each logon doesn't pop a window).
# ===============================================================
param([switch]$StartHidden)

$ErrorActionPreference = 'SilentlyContinue'

# Script-scope state for the tray lifecycle.
[bool]$script:reallyClosing = $false
[bool]$script:trayHintShown = $false

# Match both halves of the console codepage to the host OEM BEFORE any sc.exe call.
# sc.exe writes OEM (437 / 932 / 1252 / etc); PowerShell reads stdout via
# [Console]::InputEncoding and writes any console output via OutputEncoding.
# Both must agree with OEM, or the binary path captured under 2>&1 renders as
# boxes when re-emitted in WinForms labels and MessageBox dialog text.
$OEM = [System.Text.Encoding]::GetEncoding(
    [System.Globalization.CultureInfo]::CurrentCulture.TextInfo.OEMCodePage)
[Console]::InputEncoding  = $OEM
[Console]::OutputEncoding = $OEM

# STA mode is required for clipboard + ShowDialog to behave on
# PowerShell 7+ hosts (5.1 is STA by default and works either way).
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# === Form ===
$form = New-Object System.Windows.Forms.Form
$form.Text = 'Chrome Remote Desktop Manager'
$form.Size = New-Object System.Drawing.Size(760, 460)
$form.StartPosition = 'CenterScreen'
$form.MinimumSize = New-Object System.Drawing.Size(640, 380)
$form.Font = New-Object System.Drawing.Font('Segoe UI', 9)

# === Status labels (top) ===
$lblStatus    = New-Object System.Windows.Forms.Label
$lblStartMode = New-Object System.Windows.Forms.Label
$lblPID       = New-Object System.Windows.Forms.Label
$lblPath      = New-Object System.Windows.Forms.Label

$lblStatus.AutoSize    = $true
$lblStatus.Location    = New-Object System.Drawing.Point(20, 20)
$lblStartMode.AutoSize = $true
$lblStartMode.Location = New-Object System.Drawing.Point(20, 50)
$lblPID.AutoSize       = $true
$lblPID.Location       = New-Object System.Drawing.Point(20, 80)
$lblPath.AutoSize      = $false
$lblPath.Location      = New-Object System.Drawing.Point(20, 110)
$lblPath.Size          = New-Object System.Drawing.Size(700, 60)
$lblPath.Font          = New-Object System.Drawing.Font('Consolas', 9)
foreach ($lbl in @($lblStatus, $lblStartMode, $lblPID)) {
    $lbl.Font = New-Object System.Drawing.Font('Segoe UI', 10)
}
$form.Controls.AddRange(@($lblStatus, $lblStartMode, $lblPID, $lblPath))

# === Helper to make a button ===
function New-Button($text, $x, $y, $w = 170, $h = 36) {
    $b = New-Object System.Windows.Forms.Button
    $b.Text     = $text
    $b.Location = New-Object System.Drawing.Point($x, $y)
    $b.Size     = New-Object System.Drawing.Size($w, $h)
    $b
}

# === Row 1: refresh + service control ===
$btnRefresh = New-Button 'Refresh status'  20 185
$btnStart   = New-Button 'Start chromoting' 200 185
$btnStop    = New-Button 'Stop chromoting'  380 185
$btnRestart = New-Button 'Restart'          560 185
$form.Controls.AddRange(@($btnRefresh, $btnStart, $btnStop, $btnRestart))

# === Row 2: web + clipboard + log ===
$btnOpenCRD = New-Button 'Open CRD access page in browser' 20 235 270
$btnCopyURL = New-Button 'Copy CRD URL'                   300 235 170
$btnTailLog = New-Button 'Open watchdog log'              480 235 170
$form.Controls.AddRange(@($btnOpenCRD, $btnCopyURL, $btnTailLog))

# === Bottom: instructions ===
$lblHelp = New-Object System.Windows.Forms.Label
$lblHelp.Text = @'
Step 1.  Open CRD access page in browser (or copy the URL).
Step 2.  Sign in to remotedesktop.google.com with the host-enrollment Google account.
Step 3.  Click your machine, enter the CRD PIN.
Step 4.  You land at the Windows desktop. CRD PIN is the one you set during host setup,
         NOT your Google password and NOT your Windows password.

If a Start / Stop button shows "Access is denied" -- right-click this script and "Run as administrator".
'@
$lblHelp.AutoSize  = $false
$lblHelp.Location  = New-Object System.Drawing.Point(20, 295)
$lblHelp.Size      = New-Object System.Drawing.Size(700, 100)
$lblHelp.Font      = New-Object System.Drawing.Font('Segoe UI', 9)
$lblHelp.ForeColor = [System.Drawing.Color]::FromArgb(170, 170, 170)
$form.Controls.AddRange(@($lblHelp))

# Single reusable timer for transient UI hints (e.g. clipboard ack).
# Disposed in FormClosed so a re-run of the .bat doesn't leak refs to old
# controls. Tick fires on the UI thread, so STA clipboard ops stay safe.
$hintTimer         = New-Object System.Windows.Forms.Timer
$hintTimer.Interval = 1500
$hintTimer.Add_Tick({
    $form.Text = 'Chrome Remote Desktop Manager'
    $hintTimer.Stop()
})

# === System tray ===
# NotifyIcon gives the manager a persistent tray presence. Closing the
# form (X button or Alt+F4) hides it to the tray; "Exit" on the tray
# menu closes for real. -StartHidden (set by the Startup-folder shortcut)
# launches directly into the tray without flashing a window.

# Tray icon: try the chromoting host exe first, fall back to a stock
# Win32 app icon if extraction fails.
$icon = [System.Drawing.SystemIcons]::Application
$svcBoot = Get-CimInstance Win32_Service -Filter "Name='chromoting'" -ErrorAction SilentlyContinue
if ($svcBoot -and $svcBoot.PathName) {
    $exePath = $svcBoot.PathName
    if ($exePath.StartsWith('"')) {
        $exePath = ($exePath.Substring(1).Split('"'))[0]
    } else {
        $exePath = $exePath.Split(' ')[0]
    }
    try {
        if (Test-Path $exePath) {
            $icon = [System.Drawing.Icon]::ExtractAssociatedIcon($exePath)
        }
    } catch {}
}

$notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$notifyIcon.Icon            = $icon
$notifyIcon.Text            = 'Chrome Remote Desktop Manager'
$notifyIcon.Visible         = $true   # Always visible while the script runs.

# ContextMenuStrip (modern; MenuItem is the legacy WinForms 1.0 class).
$cmsShow = New-Object System.Windows.Forms.ToolStripMenuItem 'Show Manager'
$cmsExit = New-Object System.Windows.Forms.ToolStripMenuItem 'Exit'
$cmsShow.Add_Click({
    $form.WindowState    = 'Normal'
    $form.Opacity        = 1.0
    $form.ShowInTaskbar  = $true
    $form.Show()
    $form.Activate()
})
$cmsExit.Add_click({
    $script:reallyClosing = $true
    $form.Close()
})
$contextMenu = New-Object System.Windows.Forms.ContextMenuStrip
[void]$contextMenu.Items.Add($cmsShow)
[void]$contextMenu.Items.Add($cmsExit)
$notifyIcon.ContextMenuStrip = $contextMenu

# Double-click the tray icon to bring the manager back. This is the
# canonical WinForms pattern; works the same on PS 5.1 and PS 7+.
$notifyIcon.Add_DoubleClick({
    $form.WindowState    = 'Normal'
    $form.Opacity        = 1.0
    $form.ShowInTaskbar  = $true
    $form.Show()
    $form.Activate()
})

# Hide-on-X override. CloseReason==UserClosing covers X-button, Alt+F4,
# and the system Close from the form's system menu. Exit from the tray
# menu sets $script:reallyClosing first, so this handler lets Exit through.
$form.Add_FormClosing({
    param($sender, $e)
    if ($e.CloseReason -eq 'UserClosing' -and -not $script:reallyClosing) {
        $e.Cancel = $true
        $form.Hide()
        $form.ShowInTaskbar = $false
        # NotifyIcon was already Visible=$true at setup; keep it that way.
        if (-not $script:trayHintShown) {
            $script:trayHintShown = $true
            $notifyIcon.ShowBalloonTip(
                3000,
                'Chrome Remote Desktop Manager',
                'Still running. Right-click tray icon to Show or Exit.',
                'Info')
        }
    }
})

# Final cleanup. Order matters: Visible=$false BEFORE Dispose so the tray
# icon doesn't linger after Exit.
$form.Add_FormClosed({
    $hintTimer.Stop()
    $hintTimer.Dispose()
    if ($notifyIcon) {
        $notifyIcon.Visible = $false
        $notifyIcon.Dispose()
    }
})

# === Helpers (script-scope so event handlers can use them) ===
function Show-Info {
    param([string]$Msg, [string]$Title = 'CRD Manager')
    [System.Windows.Forms.MessageBox]::Show($Msg, $Title, 'OK', 'Information') | Out-Null
}

function Refresh-Status {
    $svc = Get-CimInstance Win32_Service -Filter "Name='chromoting'" -ErrorAction SilentlyContinue
    if (-not $svc) {
        $lblStatus.Text    = 'Service status:  (chromoting service is NOT installed)'
        $lblStartMode.Text = 'Start mode:       -'
        $lblPID.Text       = 'Process ID:       -'
        $lblPath.Text      = 'Binary path:      -'
        $btnStart.Enabled   = $false
        $btnStop.Enabled    = $false
        $btnRestart.Enabled = $false
        if ($notifyIcon) {
            $cap = 'CRD: (not installed)'
            if ($cap.Length -gt 63) { $cap = $cap.Substring(0, 63) }
            $notifyIcon.Text = $cap
        }
        return
    }
    $lblStatus.Text    = 'Service status:  {0}'  -f $svc.State
    $lblStartMode.Text = 'Start mode:       {0}'  -f $svc.StartMode
    $lblPID.Text       = 'Process ID:       {0}'  -f $svc.ProcessId
    $lblPath.Text      = 'Binary path:      {0}'  -f $svc.PathName
    $btnStart.Enabled   = ($svc.State -ne 'Running')
    $btnStop.Enabled    = ($svc.State -eq 'Running')
    $btnRestart.Enabled = $true
    if ($notifyIcon) {
        $cap = 'CRD: {0}' -f $svc.State
        if ($cap.Length -gt 63) { $cap = $cap.Substring(0, 63) }
        $notifyIcon.Text = $cap
    }
}

# === Wire up ===
$btnRefresh.Add_Click({ Refresh-Status })

$btnStart.Add_Click({
    Refresh-Status
    if (-not $btnStart.Enabled) {
        Show-Info 'chromoting is already STARTED; no action needed.'
        return
    }
    $out = sc.exe start chromoting 2>&1
    # ERROR_SERVICE_ALREADY_RUNNING comes back when another process flipped the
    # service between our pre-check and the call. Treat it as benign.
    if ($LASTEXITCODE -eq 1056) {
        Show-Info 'chromoting is already STARTED (raced back); no action needed.'
    } else {
        Show-Info ("`n".join([string[]]@('sc.exe start chromoting', $out))) 'Start chromoting'
    }
    Refresh-Status
})

$btnStop.Add_Click({
    Refresh-Status
    if (-not $btnStop.Enabled) {
        Show-Info 'chromoting is already STOPPED; no action needed.'
        return
    }
    $out = sc.exe stop chromoting 2>&1
    # ERROR_SERVICE_NOT_ACTIVE / ERROR_SERVICE_DOES_NOT_EXIST when already stopped
    # or uninstalled during the race window. Both benign.
    if ($LASTEXITCODE -in 1062, 1060) {
        Show-Info 'chromoting is already STOPPED (raced back); no action needed.'
    } else {
        Show-Info ("`n".join([string[]]@('sc.exe stop chromoting', $out))) 'Stop chromoting'
    }
    Refresh-Status
})

$btnRestart.Add_Click({
    $a = sc.exe stop chromoting 2>&1
    $stopCode = $LASTEXITCODE
    Start-Sleep -Seconds 2
    $b = sc.exe start chromoting 2>&1
    $startCode = $LASTEXITCODE

    # Honor the same race-tolerance codes as the Standalone Start/Stop handlers.
    $stopSucceeded  = ($stopCode  -eq 0) -or ($stopCode  -in 1062, 1060)
    $startSucceeded = ($startCode -eq 0) -or ($startCode -eq 1056)
    if ($stopSucceeded -and $startSucceeded) {
        Show-Info 'Restart succeeded (race outcomes tolerated as benign).' 'Restart chromoting'
    } else {
        Show-Info ("`n".join([string[]]@('sc.exe stop chromoting', $a, '', 'sc.exe start chromoting', $b))) 'Restart chromoting'
    }
    Refresh-Status
})

$btnOpenCRD.Add_Click({
    Start-Process 'https://remotedesktop.google.com/access'
})

$btnCopyURL.Add_Click({
    try {
        [System.Windows.Forms.Clipboard]::SetText('https://remotedesktop.google.com/access')
        $form.Text = 'CRD Manager  --  URL copied to clipboard'
        # Tick handler is wired once at form setup; just retrigger.
        $hintTimer.Stop()
        $hintTimer.Start()
    } catch {
        Show-Info ("Could not copy to clipboard (often needs STA mode).`n`nURL: https://remotedesktop.google.com/access")
    }
})

$btnTailLog.Add_Click({
    $logPath = 'C:\ProgramData\CRD-Watchdog\log.txt'
    if (Test-Path $logPath) {
        Start-Process notepad.exe -ArgumentList $logPath
    } else {
        Show-Info ("Watchdog log not present.`n`nIf the watchdog has not had to act yet, no log exists. The watchdog writes a line only when it has to re-assert chromoting start= auto.`n`nTo install the watchdog, run scripts\install_crd_watchdog.bat from an elevated cmd.")
    }
})

# === First paint + show ===
Refresh-Status

# Application.Run keeps the message pump alive even when the form is
# hidden -- ShowDialog would terminate the loop the moment we Hide(),
# which would break the tray-DoubleClick "show it again" path. Run() is
# the right primitive for tray-resident apps.
#
# -StartHidden: pre-position the form as Minimized/HideFromTaskbar/Opacity=0
# so the first paint is invisible, then Form.Shown hands off to Hide().
if ($StartHidden) {
    $form.WindowState    = 'Minimized'
    $form.ShowInTaskbar  = $false
    $form.Opacity        = 0
    $form.Add_Shown({
        $form.Hide()
        if (-not $script:trayHintShown) {
            $script:trayHintShown = $true
            $notifyIcon.ShowBalloonTip(
                3000,
                'Chrome Remote Desktop Manager',
                'Started hidden in tray. Double-click to show.',
                'Info')
        }
    })
}

[System.Windows.Forms.Application]::Run($form)
