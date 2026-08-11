$ErrorActionPreference="Stop"
Set-Location "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Write-Host "M99 v0.6.6.4.3 - LIVE 2076 vs 2100 FULL PARAMETER AUDIT"
Write-Host "GET ONLY - NO WEBSITE WRITE"
$key=Read-Host "mela99.com Webservice API key"
if([string]::IsNullOrWhiteSpace($key)){exit 1}
$env:M99_MELA99_API_KEY=$key
try{py -3 -m scripts.RUN_V06643_LIVE_FULL_PARAMETER_AUDIT}finally{Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue}
Write-Host "Temporary credential removed."
Read-Host "Press Enter"
