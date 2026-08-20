@echo off
setlocal
title M99EU Create Draft Sandbox Product
color 0E
cd /d "%~dp0"
echo ================================================================
echo   WARNING: THIS COMMAND CAN CREATE ONE DRAFT PRODUCT ON m99.eu
echo ================================================================
echo.
"admin-platform\.venv\Scripts\python.exe" "scripts\m99eu_api\create_draft.py"
echo.
pause
