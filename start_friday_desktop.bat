@echo off
title FRIDAY AI - Desktop App (Always-On Voice)
echo ============================================================
echo   FRIDAY AI - Desktop Assistant (Voice-First)
echo ============================================================
echo.
echo This opens the FRIDAY desktop window. It is always listening
echo and auto-wakes when you say "friday" - no buttons needed.
echo.
echo Close this window to stop FRIDAY.
echo.
echo TIP: To have FRIDAY run even when this is closed, run
echo   "install_autostart.bat"  once to add it to Windows startup.
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
python -c "import flask, flask_cors, pyttsx3, speech_recognition, PIL" 2>nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    python -m pip install flask flask-cors pyttsx3 speechrecognition pyaudio requests pillow google-generativeai
)

REM Install Gemini for AI mode if not present
python -c "import google.generativeai" 2>nul
if %errorlevel% neq 0 (
    echo Installing Gemini AI library...
    python -m pip install google-generativeai
)

python friday_app.py
pause
