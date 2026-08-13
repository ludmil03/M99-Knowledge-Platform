$ErrorActionPreference="Stop"
$Repo="C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo
$env:PYTHONPATH=$Repo
try { py -3 -m scripts.RUN_V06742_CHEROKEE_FULL_CONTENT_PREVIEW; if($LASTEXITCODE){throw "Preview failed"} } finally { Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue }
Read-Host "Press Enter"
