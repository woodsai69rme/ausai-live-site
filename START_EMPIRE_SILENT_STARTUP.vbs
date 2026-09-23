' ==============================================================================
' EMPIRE MASTER SILENT AUTO-START SUPERVISOR (2026 PRO)
' Boots all 7 Empire engines silently in the background on Windows login
' ==============================================================================
Set WshShell = CreateObject("WScript.Shell")
WScript.Sleep 5000 ' Brief 5s pause to allow network & services to initialize
WshShell.Run "cmd.exe /c C:\Users\karma\START_ALL_EMPIRE_SYSTEMS_2026.bat 1", 0, False
