@echo off
title SystemStart

cd /d "%~dp0"

echo ==============================
echo Starting backend service...
echo ==============================

start "Backend" python -m uvicorn backend.app:app --reload

echo Waiting for backend ready...
timeout /t 3 /nobreak >nul

echo ==============================
echo Opening frontend page...
echo ==============================

start "" "frontend\index.html"

echo.
echo Start finished!
echo Do NOT close the Backend window.
pause
