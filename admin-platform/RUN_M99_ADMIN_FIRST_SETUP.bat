@echo off
setlocal
title M99 v0.7.0.3 RBAC Relationship Setup
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_M99_ADMIN_FIRST_SETUP.ps1"
set EC=%ERRORLEVEL%
echo.
echo ============================================================
echo Exit code: %EC%
echo ============================================================
echo.
pause
exit /b %EC%
