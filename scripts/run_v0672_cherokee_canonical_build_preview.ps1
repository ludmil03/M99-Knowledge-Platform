$ErrorActionPreference = "Stop"
$Repo = "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo
$env:PYTHONPATH = $Repo
Write-Host "M99 v0.6.7.2 - Cherokee Canonical Product Build Preview"
Write-Host "GET ONLY - NO WEBSITE WRITE" -ForegroundColor Cyan
try {
    py -3 -m scripts.RUN_V0672_CHEROKEE_CANONICAL_BUILD_PREVIEW
    if ($LASTEXITCODE) { throw "Python runner failed with exit code $LASTEXITCODE" }
}
finally {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
}
Read-Host "Press Enter"
