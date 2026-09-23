@echo off
setlocal
chcp 65001 >nul
title M99 Knowledge Platform - START R4.2.1
set "MANAGER=%~dp0M99_RUNTIME_MANAGER_R421.ps1"
if not exist "%MANAGER%" (
 echo [STOP] PACKAGE_INCOMPLETE: M99_RUNTIME_MANAGER_R421.ps1 missing
 set EC=12
 goto END
)
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%MANAGER%" -Action start
set EC=%ERRORLEVEL%
:END
echo.
echo Exit code: %EC%
pause
exit /b %EC%
