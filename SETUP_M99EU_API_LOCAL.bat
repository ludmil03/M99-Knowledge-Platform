@echo off
setlocal
title M99EU API Local Setup
color 0A
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p='admin-platform\.env.local';" ^
  "if (!(Test-Path $p)) { New-Item -ItemType File -Path $p -Force | Out-Null };" ^
  "$base=Read-Host 'M99EU base URL [https://m99.eu]'; if ([string]::IsNullOrWhiteSpace($base)) {$base='https://m99.eu'};" ^
  "$key=Read-Host 'WooCommerce Consumer Key (ck_...)';" ^
  "$sec=Read-Host 'WooCommerce Consumer Secret (cs_...)';" ^
  "if (!$key.StartsWith('ck_') -or !$sec.StartsWith('cs_')) { Write-Host 'Invalid key/secret format.' -ForegroundColor Red; exit 2 };" ^
  "$lines=@(); if (Test-Path $p) {$lines=Get-Content $p | Where-Object {$_ -notmatch '^M99EU_'}};" ^
  "$lines += 'M99EU_BASE_URL='+$base;" ^
  "$lines += 'M99EU_API_PATH=/wp-json/wc/v3';" ^
  "$lines += 'M99EU_WC_CONSUMER_KEY='+$key;" ^
  "$lines += 'M99EU_WC_CONSUMER_SECRET='+$sec;" ^
  "$lines += 'M99EU_TIMEOUT_SECONDS=20';" ^
  "Set-Content -Path $p -Value $lines -Encoding UTF8;" ^
  "Write-Host ''; Write-Host 'Saved locally to admin-platform/.env.local' -ForegroundColor Green; Write-Host 'This file is Git-ignored.' -ForegroundColor Green"
echo.
pause
