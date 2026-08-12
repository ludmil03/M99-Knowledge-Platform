$ErrorActionPreference = "Stop"
$Repo = "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo
$env:PYTHONPATH = $Repo
Write-Host "M99 v0.6.7.1.4 - Repaired v0.6.7.0 launcher"
Write-Host "GET ONLY - NO WEBSITE WRITE" -ForegroundColor Cyan
$key = Read-Host "mela99.com Webservice API key"
if ([string]::IsNullOrWhiteSpace($key)) { exit 1 }
$env:M99_MELA99_API_KEY = $key
try {
    py -3 -m scripts.RUN_V0670_CHEROKEE_WW601_DISCOVERY_PREVIEW
    if ($LASTEXITCODE) { throw "Python runner failed with exit code $LASTEXITCODE" }
}
finally {
    Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
}
Read-Host "Press Enter"
