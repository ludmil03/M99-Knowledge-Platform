@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%"
py -3 -m scripts.RUN_DIADORA_S3S_EXISTING_PRODUCT_TEST
echo.
pause
endlocal
