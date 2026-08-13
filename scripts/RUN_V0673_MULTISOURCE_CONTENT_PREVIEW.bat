@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_v0673_multisource_content_preview.ps1"
exit /b %ERRORLEVEL%
