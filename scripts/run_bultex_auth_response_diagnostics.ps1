$ErrorActionPreference="Stop"
$ScriptDir=Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot=Split-Path -Parent $ScriptDir
Set-Location $RepoRoot
$client=Read-Host "Client code"
$user=Read-Host "Username"
$secure=Read-Host "Password" -AsSecureString
$ptr=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$oldPythonPath=$env:PYTHONPATH
try {
  $plain=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
  $env:BULTEX_B2B_CLIENT_CODE=$client.Trim()
  $env:BULTEX_B2B_USERNAME=$user.Trim()
  $env:BULTEX_B2B_PASSWORD=$plain
  if([string]::IsNullOrWhiteSpace($oldPythonPath)){$env:PYTHONPATH=$RepoRoot}else{$env:PYTHONPATH="$RepoRoot;$oldPythonPath"}
  py -3 -m scripts.diagnose_bultex_auth_response
}
finally {
  $env:BULTEX_B2B_CLIENT_CODE=$null
  $env:BULTEX_B2B_USERNAME=$null
  $env:BULTEX_B2B_PASSWORD=$null
  $env:PYTHONPATH=$oldPythonPath
  if($ptr -ne [IntPtr]::Zero){[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)}
}
Write-Host ""
Write-Host "Credentials removed from process environment." -ForegroundColor Green
Read-Host "Press Enter to close"
