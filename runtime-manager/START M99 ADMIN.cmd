@echo off
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0M99_RUNTIME_MANAGER_R433.ps1" -Action start
set EC=%ERRORLEVEL%
echo.
echo Exit code: %EC%
pause
exit /b %EC%

