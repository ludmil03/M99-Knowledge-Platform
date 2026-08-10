@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%"
set "M99_PUBLISH_MODE=DRY_RUN"
py -3 -m scripts.RUN_V066_CONTROLLED_PUBLISH
echo.
pause
endlocal
