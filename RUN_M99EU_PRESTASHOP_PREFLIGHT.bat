@echo off
setlocal
title M99EU PrestaShop 9 API Preflight
color 0A
cd /d "%~dp0"
"admin-platform\.venv\Scripts\python.exe" "scripts\m99eu_prestashop\preflight.py"
echo.
pause
