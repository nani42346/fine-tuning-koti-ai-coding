@echo off
title Koti AI Coding - Launcher
cd /d "%~dp0"

echo Starting Koti AI Coding API (port 8000)...
start "Koti AI - API" cmd /k "cd /d "%~dp0" && call venv\Scripts\activate.bat && uvicorn api:app --host 127.0.0.1 --port 8000"

echo Starting web dashboard (port 3000)...
start "Koti AI - Web" cmd /k "cd /d "%~dp0frontend\coding-ai-ui" && npm start"

echo.
echo Both windows are starting. The model takes ~15 seconds to load.
echo Keep both windows open while you use http://localhost:3000
timeout /t 5 >nul
