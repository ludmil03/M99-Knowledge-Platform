@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_v0670_cherokee_ww601_discovery_preview.ps1"
set EXITCODE=%ERRORLEVEL%
endlocal & exit /b %EXITCODE%
