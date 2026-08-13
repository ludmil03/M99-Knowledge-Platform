@echo off
cd /d C:\Users\user\Documents\GitHub\M99-Knowledge-Platform
py -3 -m scripts.RUN_V06744_REAL_ALL_SITES_WRITE_DRAFT
set EC=%ERRORLEVEL%
pause
exit /b %EC%
