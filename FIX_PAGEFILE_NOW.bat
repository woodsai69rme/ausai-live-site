@echo off
echo === AusAI Tech Pagefile Fix ===
echo.
echo This will set C: pagefile to Initial=16384MB Max=32768MB and restart Windows.
echo When prompted "Do you want to allow this app to make changes" -> click YES
echo.
pause
echo Elevating to admin...
powershell -Command "Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile -Command \"wmic pagefileset where name=\"\"C:\\pagefile.sys\"\" set InitialSize=16384,MaximumSize=32768\"'"
echo.
echo Pagefile configured. Restarting in 30 seconds...
echo Press CTRL+C to cancel restart.
shutdown /r /t 30 /c "Reboot required for pagefile change (AusAI Tech)"
pause
