@echo off
setlocal
title M99EU PrestaShop 9 Create Inactive Test Product
color 0E
cd /d "%~dp0"
echo ================================================================
echo   WARNING: CAN CREATE ONE INACTIVE PRODUCT ON m99.eu
echo   active=0 - no public publish action
echo ================================================================
echo.
"admin-platform\.venv\Scripts\python.exe" -m scripts.m99eu_prestashop.create_inactive
echo.
pause
