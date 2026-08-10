@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%"
if "%~1"=="" (
  set "SOURCE=tests\fixtures\product_acquisition_sample.json"
) else (
  set "SOURCE=%~1"
)
py -3 -m scripts.run_product_acquisition_preview "%SOURCE%" --output "output\acquisition_preview.json"
echo.
echo Open output\acquisition_preview.json to review the result.
pause
endlocal
