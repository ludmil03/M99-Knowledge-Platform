@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_v067114_repaired_supplier_preview.ps1"
set EXITCODE=%ERRORLEVEL%
endlocal & exit /b %EXITCODE%
