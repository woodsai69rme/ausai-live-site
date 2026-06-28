#SingleInstance Force
#NoEnv
SetBatchLines, -1

; AutoHotkey script to set a browser window as live background on Windows 11
; This script launches Edge with the background HTML and keeps it behind other windows

; Path to your background HTML file
bgHtmlPath := "C:\Users\karma\background.html"
bgHtmlUri := "file:///" . StrReplace(bgHtmlPath, "\", "/")

; Check if the HTML file exists
if (!FileExist(bgHtmlPath)) {
    MsgBox, 16, Error, Background HTML file not found at %bgHtmlPath%
    ExitApp
}

; Launch Microsoft Edge with the background content
Run, "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk --disable-web-security --disable-extensions --disable-plugins --disable-default-apps --no-first-run --no-sandbox "%bgHtmlUri%"

; Wait for the window to appear
WinWait, ahk_exe msedge.exe,, 10
if (ErrorLevel) {
    MsgBox, 16, Error, Could not launch Edge browser
    ExitApp
}

; Get the handle of the Edge window
WinGet, hwnd, ID, ahk_exe msedge.exe

; Set the window to stay behind other windows
WinSet, Bottom,, ahk_id %hwnd%

; Maximize the window to cover the screen
WinMaximize, ahk_id %hwnd%

; Optional: Make it semi-transparent (uncomment to use)
; WinSet, TransColor, 000000 220, ahk_id %hwnd%

; Keep the script running
return

; Exit script with Escape key
Esc::ExitApp