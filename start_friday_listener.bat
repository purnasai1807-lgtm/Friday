@echo off
title FRIDAY AI - Always-On Listener
echo ============================================
echo   FRIDAY AI - Always-On Voice Listener
echo ============================================
echo.
echo This runs FRIDAY in the background so it
echo auto-wakes when you say "friday" - even when
echo the app or VS Code is closed.
echo.
echo Close this window to stop FRIDAY.
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
python -c "import speech_recognition, pyttsx3, google.generativeai" 2>nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    python -m pip install speechrecognition pyttsx3 pyaudio google-generativeai requests
)

python friday_listener.py --test
pause
