@echo off
setlocal
title M99EU PrestaShop 9 Dry Run
color 0A
cd /d "%~dp0"
"admin-platform\.venv\Scripts\python.exe" -m scripts.m99eu_prestashop.dry_run
echo.
pause
