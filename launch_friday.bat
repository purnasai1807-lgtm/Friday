@echo off
title FRIDAY AI - Launcher
echo ============================================================
echo   FRIDAY AI - Main Launcher
echo ============================================================
echo.

cd /d "%~dp0"

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found. Please install Python from python.org
    pause
    exit /b
)

echo Choose launch mode:
echo.
echo [1] Web Server (access from any device on network)
echo [2] Desktop App (voice-first desktop window)
echo [3] Background Listener (always-on, no window)
echo [4] Setup for Public Access (one-time setup)
echo [5] Check Status
echo [6] Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto web
if "%choice%"=="2" goto desktop
if "%choice%"=="3" goto listener
if "%choice%"=="4" goto setup
if "%choice%"=="5" goto status
if "%choice%"=="6" goto end
goto end

:web
echo.
echo Starting FRIDAY Web Server...
echo Access from:
echo   - This PC:  http://127.0.0.1:5000
echo   - Network:  http://%COMPUTERNAME%:5000
echo.
echo Close this window to stop.
echo.
python app.py
pause
goto end

:desktop
echo.
echo Starting FRIDAY Desktop App...
echo Close the window to stop.
echo.
python friday_app.py
pause
goto end

:listener
echo.
echo Starting FRIDAY Background Listener...
echo FRIDAY will always listen for "friday" even when closed.
echo Close this window to stop.
echo.
python friday_listener.py --test
pause
goto end

:setup
echo.
echo Running Public Setup...
echo.
python setup_public.py
pause
goto end

:status
echo.
python check_status.py
pause
goto end

:end
