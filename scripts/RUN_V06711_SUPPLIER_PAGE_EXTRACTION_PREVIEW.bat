@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_v06711_supplier_page_extraction_preview.ps1"
set EXITCODE=%ERRORLEVEL%
endlocal & exit /b %EXITCODE%
