$ErrorActionPreference="Stop"
Set-Location "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Write-Host "M99 v0.6.6.4.4 - CANONICAL MASTER BUILD PREVIEW"
Write-Host "GET ONLY - NO WEBSITE WRITE"
$key=Read-Host "mela99.com Webservice API key"
if([string]::IsNullOrWhiteSpace($key)){exit 1}
$env:M99_MELA99_API_KEY=$key
try{
  py -3 -m scripts.RUN_V06644_CANONICAL_MASTER_BUILD_PREVIEW
}finally{
  Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue
}
Write-Host "Temporary credential removed."
Read-Host "Press Enter"
