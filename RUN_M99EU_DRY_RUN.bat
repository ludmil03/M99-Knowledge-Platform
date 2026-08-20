@echo off
setlocal
title M99EU Sandbox Dry Run
color 0A
cd /d "%~dp0"
"admin-platform\.venv\Scripts\python.exe" "scripts\m99eu_api\dry_run.py"
echo.
pause
