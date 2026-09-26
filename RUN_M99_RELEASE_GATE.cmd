@echo off
setlocal
cd /d "%~dp0"
set "PY=admin-platform\.venv\Scripts\python.exe"
if not exist "%PY%" (
 echo [NOT_RELEASEABLE] Missing M99 venv Python: %PY%
 exit /b 20
)
"%PY%" -u scripts\m99_release_gate.py %*
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" echo M99 RELEASE GATE: NOT_RELEASEABLE
if "%RC%"=="0" echo M99 RELEASE GATE: PASS
exit /b %RC%
