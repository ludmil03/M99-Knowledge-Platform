$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot
$oldPythonPath = $env:PYTHONPATH
try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
        $env:PYTHONPATH = $RepoRoot
    } else {
        $env:PYTHONPATH = "$RepoRoot;$oldPythonPath"
    }
    py -3 -m scripts.diagnose_bultex_login_js
}
finally {
    $env:PYTHONPATH = $oldPythonPath
}
Write-Host ""
Read-Host "Press Enter to close"
