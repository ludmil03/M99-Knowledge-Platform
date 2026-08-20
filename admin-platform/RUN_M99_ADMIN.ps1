$ErrorActionPreference="Stop"
$Here=Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here
if(-not(Test-Path ".venv\Scripts\python.exe")){throw "Run RUN_M99_ADMIN_FIRST_SETUP.bat first."}
if(-not(Test-Path ".env.local")){throw "Missing .env.local. Run first setup."}
. ".\scripts\Load-Env.ps1" -Path ".\.env.local"
Write-Host "M99 Knowledge Platform"
Write-Host "Admin URL: http://$env:M99_HOST`:$env:M99_PORT"
Write-Host "Press Ctrl+C to stop."
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host $env:M99_HOST --port $env:M99_PORT
