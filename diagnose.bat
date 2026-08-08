@echo off
title FRIDAY AI - Diagnostic Tool
echo ============================================================
echo   FRIDAY AI - Diagnostic Tool
echo ============================================================
echo.

echo [1] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Python not found. Install from python.org
    pause
    exit /b
)
echo [OK] Python found

echo.
echo [2] Checking Flask server...
curl -s http://127.0.0.1:5000/api/status >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Flask server is running at http://127.0.0.1:5000
) else (
    echo [FAIL] Flask server is NOT running
    echo.
    echo Start it with: python app.py
    echo.
    echo Would you like to start it now? (Y/N)
    set /p start_now=""
    if /i "%start_now%"=="Y" (
        echo.
        echo Starting FRIDAY server...
        echo After it starts, open http://127.0.0.1:5000 in your browser
        echo.
        python app.py
    )
    pause
    exit /b
)

echo.
echo [3] Checking browser compatibility...
echo.
echo IMPORTANT: Use Chrome or Edge browser for best compatibility.
echo Firefox does NOT support voice recognition by default.
echo Safari works but requires different setup.
echo.
echo Open http://127.0.0.1:5000 in Chrome or Edge
echo.
echo [4] Troubleshooting steps:
echo   1. Allow microphone permission when prompted
echo   2. Say "wake up friday" clearly
echo   3. Check browser console (F12) for errors
echo   4. Make sure no other app is using the microphone
echo.
echo Press any key to open browser...
pause >nul
start http://127.0.0.1:5000
echo.
echo Browser opened. Try saying "wake up friday"
echo.
pause
