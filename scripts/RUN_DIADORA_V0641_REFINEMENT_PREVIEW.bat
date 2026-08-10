@echo off
setlocal
cd /d "%~dp0.."
py -3 -m scripts.RUN_DIADORA_V0641_REFINEMENT_PREVIEW
if errorlevel 1 (
  echo.
  echo ERROR - preview failed.
  pause
  exit /b 1
)
echo.
pause
