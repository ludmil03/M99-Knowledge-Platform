$ErrorActionPreference = "Stop"
$Repo = "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo
$env:PYTHONPATH = $Repo
Write-Host "M99 v0.6.7.1.4 - REPAIRED SUPPLIER PREVIEW"
Write-Host "GET ONLY - NO WEBSITE WRITE" -ForegroundColor Cyan
try {
    py -3 -m scripts.RUN_V067114_LAUNCHER_SELF_CHECK
    if ($LASTEXITCODE) { throw "Launcher self-check failed" }
    py -3 -m scripts.RUN_V067113_SUPPLIER_NOISE_FILTER_PREVIEW
    if ($LASTEXITCODE) { throw "Supplier preview failed" }
}
finally {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
}
Read-Host "Press Enter"
