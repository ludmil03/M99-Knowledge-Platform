@echo off
setlocal
title M99 v0.7.3 Phase 4 - APPLY PRODUCTION MIGRATION
echo ================================================================
echo   M99 v0.7.3 PHASE 4 - PRODUCTION MIGRATION
echo ================================================================
echo This WILL modify M99_ADMIN_DATABASE_URL.
echo Backup and review first.
set /p ANSWER=Type APPLY to continue:
if /I not "%ANSWER%"=="APPLY" exit /b 0
"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform\admin-platform\.venv\Scripts\python.exe" -m scripts.m99_phase4.apply_migration
pause
