@echo off
setlocal
cd /d "%~dp0.."
echo M99 v0.6.7.5 - Cherokee WW601 PRE-FLIGHT
echo GET ONLY - NO WEBSITE WRITE
python scripts\RUN_V0675_CHEROKEE_REAL_PUBLISH.py preflight
echo.
pause
