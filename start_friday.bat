@echo off
title FRIDAY AI - Web Server (Phone/Laptop/Desktop)
echo ============================================================
echo   FRIDAY AI - Always-On Assistant - Web Server
echo ============================================================
echo.
echo This starts the web server so you can use FRIDAY from:
echo   - This computer:  http://127.0.0.1:5000
echo   - Your phone:     http://YOUR_COMPUTER_IP:5000  (same Wi-Fi)
echo.
echo The web app listens continuously for "FRIDAY" using your
echo browser's microphone - no buttons needed.
echo.
echo For FRIDAY to auto-wake EVEN when the browser/app is closed,
echo run "start_friday_listener.bat" or install auto-start.
echo.
echo Close this window to stop the web server.
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b
)

REM Install dependencies if needed
python -c "import flask, flask_cors, pyttsx3, speech_recognition" 2>nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    python -m pip install flask flask-cors pyttsx3 speechrecognition pyaudio requests google-generativeai
)

REM Install Gemini for AI mode if not present
python -c "import google.generativeai" 2>nul
if %errorlevel% neq 0 (
    echo Installing Gemini AI library...
    python -m pip install google-generativeai
)

REM Get and display network IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%
echo Starting server...
echo When ready, access from:
echo   - This PC:  http://127.0.0.1:5000
echo   - Network:  http://%IP%:5000
echo.

python app.py
pause
