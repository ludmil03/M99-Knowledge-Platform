@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_v0671_supplier_intelligence_preview.ps1"
set EXITCODE=%ERRORLEVEL%
endlocal & exit /b %EXITCODE%
