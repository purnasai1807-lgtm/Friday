@echo off
title FRIDAY AI - Create Desktop Shortcut
echo ============================================================
echo   FRIDAY AI - Desktop Shortcut Creator
echo ============================================================
echo.

cd /d "%~dp0"

set SCRIPT=%BASE_DIR%\launch_friday.bat
set ICON=%BASE_DIR%\static\gifs\ironman.gif

REM Create desktop shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\FRIDAY AI.lnk'); $Shortcut.TargetPath = '%SCRIPT%'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = 'shell32.dll,13'; $Shortcut.Description = 'FRIDAY AI - Personal Assistant'; $Shortcut.Save()"

echo.
echo Desktop shortcut created: FRIDAY AI
echo Double-click it to launch FRIDAY.
echo.
pause
