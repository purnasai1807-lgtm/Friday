@echo off
title FRIDAY AI - Public Setup
echo ============================================================
echo   FRIDAY AI - Public Access Setup
echo ============================================================
echo.
echo This will set up FRIDAY for public access.
echo.
echo After setup, anyone on your network can access FRIDAY at:
echo   http://%COMPUTERNAME%:5000
echo.
echo FRIDAY will also run in the background even when
echo VS Code or this window is closed.
echo.
pause
echo.

cd /d "%~dp0"

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH"
    pause
    exit /b
)

echo [1/5] Installing dependencies...
python -m pip install --quiet flask flask-cors pyttsx3 speechrecognition pyaudio requests google-generativeai pillow pyautogui pytesseract pyperclip qrcode psutil 2>nul
echo Done.

echo.
echo [2/5] Configuring firewall...
netsh advfirewall firewall add rule name="FRIDAY AI" dir=in action=allow protocol=TCP localport=5000 profile=private >nul 2>&1
echo Firewall rule added for port 5000 (private networks).

echo.
echo [3/5] Installing background service...
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
if not exist "%STARTUP%" mkdir "%STARTUP%"

REM Create VBS wrapper to run listener hidden
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%~dp0"
echo WshShell.Run "pythonw friday_listener.pyw", 0, False
) > "%STARTUP%\FRIDAY_Listener.vbs"

echo Service installed. FRIDAY will auto-start on boot.

echo.
echo [4/5] Testing server...
start /B python app.py
timeout /t 3 /nobreak >nul

REM Check if server is running
curl -s http://127.0.0.1:5000/api/status >nul 2>&1
if %errorlevel% equ 0 (
    echo Server is running.
) else (
    echo Server may need a moment to start...
)

echo.
echo [5/5] Getting network address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%
echo.
echo ============================================================
echo   SETUP COMPLETE!
echo ============================================================
echo.
echo Access FRIDAY from:
echo   - This PC:  http://127.0.0.1:5000
echo   - Network:  http://%IP%:5000
echo.
echo FRIDAY is now running in the background.
echo Say "wake up friday" to activate.
echo.
echo To stop FRIDAY, close the server window or restart.
echo To uninstall, delete:
echo   %STARTUP%\FRIDAY_Listener.vbs
echo.
pause
