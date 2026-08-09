$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

Write-Host "Bultex99 B2B SAFE READ-ONLY LIVE TEST"
Write-Host "Credentials exist only in this PowerShell process."
Write-Host ""

$client = Read-Host "Client code"
$user = Read-Host "Username"
$secure = Read-Host "Password" -AsSecureString

$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$oldPythonPath = $env:PYTHONPATH

try {
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)

    $env:BULTEX_B2B_CLIENT_CODE = $client
    $env:BULTEX_B2B_USERNAME = $user
    $env:BULTEX_B2B_PASSWORD = $plain

    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
        $env:PYTHONPATH = $RepoRoot
    } else {
        $env:PYTHONPATH = "$RepoRoot;$oldPythonPath"
    }

    Write-Host ""
    py -3 -m scripts.test_bultex_safe_live_auth
}
finally {
    $env:BULTEX_B2B_CLIENT_CODE = $null
    $env:BULTEX_B2B_USERNAME = $null
    $env:BULTEX_B2B_PASSWORD = $null
    $env:PYTHONPATH = $oldPythonPath

    if ($ptr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

Write-Host ""
Write-Host "Credentials removed from process environment." -ForegroundColor Green
Read-Host "Press Enter to close"
