$ErrorActionPreference="Stop"
Set-Location "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Write-Host "M99 v0.6.7.1 - Multi-Source Evidence & Supplier Intelligence"
Write-Host "GET ONLY - NO WEBSITE WRITE" -ForegroundColor Cyan
py -3 -m scripts.RUN_V0671_SUPPLIER_INTELLIGENCE_PREVIEW
Read-Host "Press Enter"
