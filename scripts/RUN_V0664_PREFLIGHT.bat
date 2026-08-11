@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%"
py -3 -m scripts.RUN_V0664_PREFLIGHT
echo.
pause
endlocal
