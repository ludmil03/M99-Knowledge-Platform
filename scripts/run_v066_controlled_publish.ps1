$ErrorActionPreference="Stop"
$Repo="C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
Set-Location $Repo

Write-Host "M99 v0.6.6 CONTROLLED SINGLE PRODUCT WRITE" -ForegroundColor Yellow
Write-Host "Target: mela99.com / M99 100002 only"
Write-Host ""
$mode = Read-Host "Mode (WRITE_DRAFT or PUBLISH_LIVE)"
$mode = $mode.Trim().ToUpper()

if($mode -ne "WRITE_DRAFT" -and $mode -ne "PUBLISH_LIVE"){
    Write-Host "Invalid mode." -ForegroundColor Red
    Read-Host "Press Enter"
    exit 1
}

$key = Read-Host "mela99.com Webservice API key"
if([string]::IsNullOrWhiteSpace($key)){
    Write-Host "API key required." -ForegroundColor Red
    Read-Host "Press Enter"
    exit 1
}

$env:M99_MELA99_API_KEY=$key
$env:M99_PUBLISH_MODE=$mode
$env:M99_OPERATOR_APPROVED="YES"

if($mode -eq "PUBLISH_LIVE"){
    $pricing = Read-Host "Pricing approved? Type YES"
    $availability = Read-Host "Availability approved? Type YES"
    if($pricing.Trim().ToUpper() -ne "YES" -or $availability.Trim().ToUpper() -ne "YES"){
        Write-Host "LIVE publish blocked: pricing and availability approval are required." -ForegroundColor Red
        Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue
        Read-Host "Press Enter"
        exit 1
    }
    $price = Read-Host "Approved sale price EX VAT"
    $env:M99_PRICING_APPROVED="YES"
    $env:M99_AVAILABILITY_APPROVED="YES"
    $env:M99_APPROVED_PRICE_EX_VAT=$price
}else{
    $env:M99_PRICING_APPROVED="NO"
    $env:M99_AVAILABILITY_APPROVED="NO"
}

Write-Host ""
Write-Host "Existing product name policy:"
Write-Host "By default the current name is kept together with product ID, slug and URL."
Write-Host "A name change requires PROVEN_BETTER + separate operator approval."
$nameChange = Read-Host "Approve proposed name change on an EXISTING product? Type YES or NO"
if($nameChange.Trim().ToUpper() -eq "YES"){
    $proof = Read-Host "Evidence status. Type exactly PROVEN_BETTER to allow the name change"
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

$decisionFile="output\diadora_glove_abox_low_pro_s1ps_v065_live_internal_discovery.json"
if(-not (Test-Path $decisionFile)){
    Write-Host "LIVE internal discovery result is missing. Run v0.6.5 LIVE discovery first." -ForegroundColor Red
    Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue
    Read-Host "Press Enter"
    exit 1
}

$data=Get-Content $decisionFile -Raw | ConvertFrom-Json
$result=$data.results.'mela99.com'
$decision=$result.decision
if($decision -ne "EXISTING" -and $decision -ne "NEW"){
    Write-Host "Publish blocked by discovery decision: $decision" -ForegroundColor Red
    Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue
    Read-Host "Press Enter"
    exit 1
}

$action = if($decision -eq "EXISTING"){"UPDATE"}else{"CREATE"}
$required="$mode $action M99 100002 MELA99"

Write-Host ""
Write-Host "FINAL CONFIRMATION REQUIRED" -ForegroundColor Yellow
Write-Host "Type exactly:"
Write-Host $required -ForegroundColor Cyan
$confirmation=Read-Host "Confirmation"
$env:M99_PUBLISH_CONFIRMATION=$confirmation

try{
    py -3 -m scripts.RUN_V066_CONTROLLED_PUBLISH
}finally{
    Remove-Item Env:M99_MELA99_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:M99_PUBLISH_MODE -ErrorAction SilentlyContinue
    Remove-Item Env:M99_OPERATOR_APPROVED -ErrorAction SilentlyContinue
    Remove-Item Env:M99_PRICING_APPROVED -ErrorAction SilentlyContinue
    Remove-Item Env:M99_AVAILABILITY_APPROVED -ErrorAction SilentlyContinue
    Remove-Item Env:M99_APPROVED_PRICE_EX_VAT -ErrorAction SilentlyContinue
    Remove-Item Env:M99_NAME_CHANGE_APPROVED -ErrorAction SilentlyContinue
    Remove-Item Env:M99_NAME_CHANGE_EVIDENCE -ErrorAction SilentlyContinue
    Remove-Item Env:M99_PUBLISH_CONFIRMATION -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Credentials and one-time approval variables removed from this PowerShell process."
Read-Host "Press Enter"
