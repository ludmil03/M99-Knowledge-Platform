@echo off
cd /d "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
set "PYTHONPATH=%CD%"
for /d %%D in ("%LOCALAPPDATA%\GitHubDesktop\app-*") do if exist "%%D\resources\app\git\cmd\git.exe" set "M99_GIT_EXE=%%D\resources\app\git\cmd\git.exe"
"admin-platform\.venv\Scripts\python.exe" "tools\r7k4_existing_importer_recovery.py"
set RC=%errorlevel%
echo Exit code: %RC%
pause
exit /b %RC%
