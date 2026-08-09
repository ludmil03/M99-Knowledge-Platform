$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

Write-Host "Bultex99 B2B login diagnostics"
Write-Host "READ-ONLY - NO LOGIN ATTEMPT"
Write-Host ""
Write-Host "Optional: enter Client code only if you want the request URL"
Write-Host "to match the portal's normal login link."
Write-Host "It will NOT be printed or saved."
Write-Host ""

$client = Read-Host "Client code hint (or press Enter to skip)"

$oldHint = $env:BULTEX_B2B_CLIENT_CODE_HINT
$oldPythonPath = $env:PYTHONPATH

try {
    if (-not [string]::IsNullOrWhiteSpace($client)) {
        $env:BULTEX_B2B_CLIENT_CODE_HINT = $client
    } else {
        $env:BULTEX_B2B_CLIENT_CODE_HINT = $null
    }

    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
        $env:PYTHONPATH = $RepoRoot
    } else {
        $env:PYTHONPATH = "$RepoRoot;$oldPythonPath"
    }

    py -3 -m scripts.diagnose_bultex_login_live
}
finally {
    $env:BULTEX_B2B_CLIENT_CODE_HINT = $oldHint
    $env:PYTHONPATH = $oldPythonPath
}

Write-Host ""
Read-Host "Press Enter to close"
