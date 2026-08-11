$ErrorActionPreference="Stop"
$Repo="C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo
Write-Host "M99 v0.6.6.4.2 - GET-ONLY LIVE ANALYSIS" -ForegroundColor Cyan
Write-Host "NO WEBSITE WRITE"
$key=Read-Host "mela99.com Webservice API key"
if([string]::IsNullOrWhiteSpace($key)){Write-Host "API key required." -ForegroundColor Red; Read-Host "Press Enter"; exit 1}
$env:M99_MELA99_API_KEY=$key
try{py -3 -m scripts.RUN_V06642_LIVE_ANALYSIS_PREVIEW}finally{Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue}
Write-Host "Temporary credential removed."
Read-Host "Press Enter"
