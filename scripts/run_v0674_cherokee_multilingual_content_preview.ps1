$ErrorActionPreference="Stop"
$Repo="C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo
$env:PYTHONPATH=$Repo
try { py -3 -m scripts.RUN_V0674_CHEROKEE_MULTILINGUAL_CONTENT_PREVIEW; if($LASTEXITCODE){throw "Preview failed"} } finally { Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue }
Read-Host "Press Enter"
