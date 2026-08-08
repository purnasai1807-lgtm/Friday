@echo off
title FRIDAY AI - Install Auto-Start
echo ============================================
echo   FRIDAY AI - Auto-Start Setup
echo ============================================
echo.
echo This adds FRIDAY to Windows startup so it runs
echo automatically when your computer starts - even
echo before you open the app or VS Code.
echo.
echo FRIDAY will always be listening in the background.
echo.
cd /d "%~dp0"

REM Create a shortcut in the Startup folder that runs the listener without a window
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM Create a VBS wrapper to run the listener hidden (no console window)
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%~dp0"
echo WshShell.Run "pythonw friday_listener.pyw", 0, False
) > "%STARTUP%\FRIDAY_Listener.vbs"

echo.
echo FRIDAY has been added to Windows startup.
echo It will now auto-start and always listen for "friday".
echo.
echo To remove it later, delete:
echo   %STARTUP%\FRIDAY_Listener.vbs
echo.
pause
