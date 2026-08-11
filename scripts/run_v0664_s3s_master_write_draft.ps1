$ErrorActionPreference="Stop"
$Repo="C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo

Write-Host "M99 v0.6.6.4.1 - SAFE WRITABLE S3S MASTER WRITE_DRAFT" -ForegroundColor Yellow
Write-Host "REAL API WRITE: mela99.com product ID 2076 ONLY"
Write-Host "The live blank product schema will be fetched first; only schema-supported fields will be PUT."
Write-Host "Existing categories are preserved."
Write-Host "Existing name and URL are preserved by default."
Write-Host ""

$key=Read-Host "mela99.com Webservice API key"
if([string]::IsNullOrWhiteSpace($key)){
  Write-Host "API key required." -ForegroundColor Red
  Read-Host "Press Enter"
  exit 1
}

$env:M99_MELA99_API_KEY=$key
$env:M99_OPERATOR_APPROVED="YES"

Write-Host ""
Write-Host "Name policy:"
Write-Host "Default: KEEP current name. URL/slug always KEEP."
$nameChange=Read-Host "Approve a proven-better product name change now? Type YES or NO"
if($nameChange.Trim().ToUpper() -eq "YES"){
  $proof=Read-Host "Type exactly PROVEN_BETTER"
  if($proof.Trim().ToUpper() -eq "PROVEN_BETTER"){
    $env:M99_NAME_CHANGE_APPROVED="YES"
    $env:M99_NAME_CHANGE_EVIDENCE="PROVEN_BETTER"
  }else{
    $env:M99_NAME_CHANGE_APPROVED="NO"
    $env:M99_NAME_CHANGE_EVIDENCE="NOT_PROVEN"
  }
}else{
  $env:M99_NAME_CHANGE_APPROVED="NO"
  $env:M99_NAME_CHANGE_EVIDENCE="NOT_PROVEN"
}

$required="WRITE_DRAFT UPDATE 2076 M99 100017 MELA99"
Write-Host ""
Write-Host "FINAL WRITE CONFIRMATION" -ForegroundColor Yellow
Write-Host "Type exactly:"
Write-Host $required -ForegroundColor Cyan
$confirmation=Read-Host "Confirmation"
$env:M99_WRITE_DRAFT_CONFIRMATION=$confirmation

try{
  py -3 -m scripts.RUN_V0664_S3S_MASTER_WRITE_DRAFT
}finally{
  Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue
  Remove-Item Env:M99_OPERATOR_APPROVED -ErrorAction SilentlyContinue
  Remove-Item Env:M99_NAME_CHANGE_APPROVED -ErrorAction SilentlyContinue
  Remove-Item Env:M99_NAME_CHANGE_EVIDENCE -ErrorAction SilentlyContinue
  Remove-Item Env:M99_WRITE_DRAFT_CONFIRMATION -ErrorAction SilentlyContinue
}
Write-Host ""
Write-Host "Temporary credentials and approvals removed from this PowerShell process."
Read-Host "Press Enter"
