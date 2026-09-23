@echo off
set CORS_ORIGINS=http://localhost:3737,http://127.0.0.1:3737,http://localhost:8080,http://127.0.0.1:8080
cd /d "C:\Users\karma\python"
"C:\Users\karma\.local\bin\uv.exe" run python -m src.server.main > "C:\Users\karma\fastapi-out.log" 2> "C:\Users\karma\fastapi-err.log"

