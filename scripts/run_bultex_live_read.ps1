$ErrorActionPreference = "Stop"

Write-Host "Bultex99 B2B credentials - CURRENT CMD/PowerShell SESSION ONLY"
Write-Host "Nothing will be written to GitHub or to a .env file."
Write-Host ""

$client = Read-Host "Client code"
$user = Read-Host "Username"
$secure = Read-Host "Password" -AsSecureString

$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)

    $env:BULTEX_B2B_CLIENT_CODE = $client
    $env:BULTEX_B2B_USERNAME = $user
    $env:BULTEX_B2B_PASSWORD = $plain

    Write-Host ""
    Write-Host "Credentials loaded into this PowerShell process only." -ForegroundColor Green
    Write-Host "Now the live test will run."
    Write-Host ""

    py -3 scripts\test_bultex_live_read.py
}
finally {
    $env:BULTEX_B2B_CLIENT_CODE = $null
    $env:BULTEX_B2B_USERNAME = $null
    $env:BULTEX_B2B_PASSWORD = $null

    if ($ptr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

Write-Host ""
Write-Host "Credentials removed from process environment." -ForegroundColor Green
Read-Host "Press Enter to close"
