@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_v067112_robust_supplier_discovery_preview.ps1"
set EXITCODE=%ERRORLEVEL%
endlocal & exit /b %EXITCODE%
