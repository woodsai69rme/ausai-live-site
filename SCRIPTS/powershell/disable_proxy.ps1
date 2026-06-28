# Disable Windows Proxy Settings
Write-Host "Disabling Windows proxy settings..." -ForegroundColor Green
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Value 0
Write-Host "Proxy disabled successfully." -ForegroundColor Green
Write-Host ""
Write-Host "Note: You may need to restart your browsers for changes to take full effect." -ForegroundColor Yellow
Read-Host "Press Enter to exit"