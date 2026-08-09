$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Set-Location $RepoRoot

Write-Host "Bultex99 B2B credentials - CURRENT POWERSHELL PROCESS ONLY"
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

    # Ensure repository packages (core/, integrations/, etc.) are importable.
    $previousPythonPath = $env:PYTHONPATH
    if ([string]::IsNullOrWhiteSpace($previousPythonPath)) {
        $env:PYTHONPATH = $RepoRoot
    } else {
        $env:PYTHONPATH = "$RepoRoot;$previousPythonPath"
    }

    Write-Host ""
    Write-Host "Credentials loaded into this PowerShell process only." -ForegroundColor Green
    Write-Host "Repository root: $RepoRoot"
    Write-Host "Now the READ-ONLY live test will run."
    Write-Host ""

    py -3 -m scripts.test_bultex_live_read
}
finally {
    $env:BULTEX_B2B_CLIENT_CODE = $null
    $env:BULTEX_B2B_USERNAME = $null
    $env:BULTEX_B2B_PASSWORD = $null

    if ($null -ne $previousPythonPath) {
        $env:PYTHONPATH = $previousPythonPath
    } else {
        $env:PYTHONPATH = $null
    }

    if ($ptr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

Write-Host ""
Write-Host "Credentials removed from process environment." -ForegroundColor Green
Read-Host "Press Enter to close"
