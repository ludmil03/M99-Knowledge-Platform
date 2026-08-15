@echo off
title M99 v0.6.7.5.4 - Write Review Gate
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_V06754_WITH_LOCAL_CREDENTIALS.ps1" -Mode write
set EC=%ERRORLEVEL%
echo.
echo Exit code: %EC%
pause
exit /b %EC%
