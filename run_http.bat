@echo off
cd /d "C:\Users\karma"
"C:\Program Files\Python313\python.exe" -m http.server 8080 --bind 127.0.0.1 > "C:\Users\karma\http-out.log" 2> "C:\Users\karma\http-err.log"

