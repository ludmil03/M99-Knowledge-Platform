$ErrorActionPreference="Stop"
$Repo="C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo

Write-Host "M99 v0.6.6.3 - OPERATOR MASTER SELECTION" -ForegroundColor Yellow
Write-Host "This action DOES NOT write to the website."
Write-Host ""

$id=Read-Host "Enter master product ID from the candidate list"
$required="CONFIRM MASTER $id M99 100017 MELA99"
Write-Host "Type exactly:"
Write-Host $required -ForegroundColor Cyan
$confirmation=Read-Host "Confirmation"

$env:M99_MASTER_PRODUCT_ID=$id
$env:M99_MASTER_CONFIRMATION=$confirmation

try{
  py -3 -m scripts.RUN_V0663_CONFIRM_MASTER
}finally{
  Remove-Item Env:M99_MASTER_PRODUCT_ID -ErrorAction SilentlyContinue
  Remove-Item Env:M99_MASTER_CONFIRMATION -ErrorAction SilentlyContinue
}

Read-Host "Press Enter"
