@echo off
cd /d "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
"admin-platform\.venv\Scripts\python.exe" "scripts\RUN_PRODUCT_2041_COMPLETE_EVIDENCE_PREFLIGHT.py"
set RC=%errorlevel%
echo Exit code: %RC%
pause
exit /b %RC%
