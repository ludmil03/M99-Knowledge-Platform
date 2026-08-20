@echo off
setlocal
title M99EU PrestaShop API Local Setup
color 0A
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p='admin-platform\.env.local';" ^
  "if (!(Test-Path $p)) { New-Item -ItemType File -Path $p -Force | Out-Null };" ^
  "$base=Read-Host 'M99EU base URL [https://m99.eu]'; if ([string]::IsNullOrWhiteSpace($base)) {$base='https://m99.eu'};" ^
  "$key=Read-Host 'PrestaShop Webservice API Key';" ^
  "$cat=Read-Host 'TEST category ID for inactive product';" ^
  "if ([string]::IsNullOrWhiteSpace($key) -or $key.Length -lt 16) { Write-Host 'API key looks invalid.' -ForegroundColor Red; exit 2 };" ^
  "$tmp=0; if (![int]::TryParse($cat,[ref]$tmp) -or $tmp -le 0) { Write-Host 'Category ID must be a positive integer.' -ForegroundColor Red; exit 3 };" ^
  "$lines=@(); if (Test-Path $p) {$lines=Get-Content $p | Where-Object {$_ -notmatch '^M99EU_'}};" ^
  "$lines += 'M99EU_BASE_URL='+$base;" ^
  "$lines += 'M99EU_PS_API_KEY='+$key;" ^
  "$lines += 'M99EU_PS_TEST_CATEGORY_ID='+$cat;" ^
  "$lines += 'M99EU_TIMEOUT_SECONDS=20';" ^
  "Set-Content -Path $p -Value $lines -Encoding UTF8;" ^
  "Write-Host ''; Write-Host 'Saved locally in admin-platform/.env.local' -ForegroundColor Green; Write-Host 'This file is Git-ignored.' -ForegroundColor Green"
echo.
pause
