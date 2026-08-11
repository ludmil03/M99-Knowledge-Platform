$ErrorActionPreference="Stop"
Set-Location "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
$key=Read-Host "mela99.com Webservice API key"
if([string]::IsNullOrWhiteSpace($key)){exit 1}
$env:M99_MELA99_API_KEY=$key
try{py -3 -m scripts.RUN_V066422_TEST_CATEGORY_DIAGNOSTICS}finally{Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue}
Read-Host "Press Enter"
