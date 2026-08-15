@echo off
setlocal
cd /d "%~dp0.."
echo M99 v0.6.7.5 - Cherokee WW601 REAL WRITE_DRAFT
echo REQUIRED WRITE CHANNELS: mela99.com, rabotni-drehi.com, medicinski-drehi.com, laviro.ro, alviro.ro
echo m99.eu: TASK ONLY / EXCLUDED - NO WRITE
python scripts\RUN_V0675_CHEROKEE_REAL_PUBLISH.py write
echo.
pause
