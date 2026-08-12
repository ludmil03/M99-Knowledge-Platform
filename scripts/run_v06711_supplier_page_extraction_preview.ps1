$ErrorActionPreference="Stop"
Set-Location "C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Write-Host "M99 v0.6.7.1.1 - Supplier Product Page Extraction & Evidence Merge"
Write-Host "GET ONLY - NO WEBSITE WRITE" -ForegroundColor Cyan
py -3 -m scripts.RUN_V06711_SUPPLIER_PAGE_EXTRACTION_PREVIEW
Read-Host "Press Enter"
