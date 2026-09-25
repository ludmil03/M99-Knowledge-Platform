@echo off
setlocal
chcp 65001 >nul
set "REPO=C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
set "PY=C:\Users\user\Documents\GitHub\M99-Knowledge-Platform\admin-platform\.venv\Scripts\python.exe"
if not exist "%PY%" (
 echo [STOP] Python not found: %PY%
 pause
 exit /b 2
)
cd /d "%REPO%\admin-platform"
if errorlevel 1 (
 echo [STOP] Cannot open admin-platform.
 pause
 exit /b 3
)
"%PY%" -m app.services.v073_multichannel.r25_controlled_publish
set "RC=%ERRORLEVEL%"
echo.
echo Exit code: %RC%
pause
exit /b %RC%
