$ErrorActionPreference = "Stop"
$Here = "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform\admin-platform"
Write-Host "============================================================"
Write-Host "M99 v0.7.0.3 - SQLALCHEMY RBAC RELATIONSHIP MODEL HOTFIX"
Write-Host "============================================================"
if(-not(Test-Path -LiteralPath $Here)){throw "admin-platform not found: $Here"}
Set-Location $Here
if(-not(Test-Path ".venv\Scripts\python.exe")){throw "Virtual environment missing."}
if(-not(Test-Path ".env.local")){throw ".env.local missing."}
. ".\scripts\Load-Env.ps1" -Path ".\.env.local"
$env:PYTHONPATH=$Here
Write-Host ".env.local: PRESERVED"
Write-Host ("PYTHONPATH="+$env:PYTHONPATH)
Write-Host ""
Write-Host "Validating RBAC mapper model..."
& ".\.venv\Scripts\python.exe" ".\scripts\validate_rbac_mappers.py"
if($LASTEXITCODE -ne 0){throw "RBAC mapper validation failed with exit code $LASTEXITCODE"}
Write-Host ""
Write-Host "Initializing / repairing M99 database..."
& ".\.venv\Scripts\python.exe" ".\scripts\init_db.py"
if($LASTEXITCODE -ne 0){throw "init_db.py failed with exit code $LASTEXITCODE"}
$DbFile=Join-Path $Here "data\m99_admin.db"
if(-not(Test-Path -LiteralPath $DbFile)){throw "Expected SQLite database file missing after init."}
Write-Host ("Database verified: "+$DbFile)
Write-Host ("Database bytes: "+(Get-Item -LiteralPath $DbFile).Length)
Write-Host ""
Write-Host "Creating first M99 Super Admin..."
& ".\.venv\Scripts\python.exe" ".\scripts\create_admin.py"
if($LASTEXITCODE -ne 0){throw "create_admin.py failed with exit code $LASTEXITCODE"}
Write-Host ""
Write-Host "============================================================"
Write-Host "M99 v0.7.0.3 SETUP COMPLETE"
Write-Host "RBAC mapper validation: PASS"
Write-Host "Database bootstrap: PASS"
Write-Host "Super Admin: CREATED"
Write-Host "Next: RUN_M99_ADMIN.bat"
Write-Host "============================================================"
