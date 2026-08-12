$ErrorActionPreference = "Stop"
$Repo = "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo
$env:PYTHONPATH = $Repo
Write-Host "M99 v0.6.7.1.4 - Repaired Windows launcher"
Write-Host "GET ONLY - NO WEBSITE WRITE" -ForegroundColor Cyan
try {
    py -3 -m scripts.RUN_V06711_SUPPLIER_PAGE_EXTRACTION_PREVIEW
    if ($LASTEXITCODE) { throw "Python runner failed with exit code $LASTEXITCODE" }
}
finally {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
}
Read-Host "Press Enter"
