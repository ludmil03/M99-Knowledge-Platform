param(
  [ValidateSet("preflight","write")]
  [string]$Mode="preflight"
)
$ErrorActionPreference="Stop"
$Repo="C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
$Store=Join-Path $env:LOCALAPPDATA "M99\credentials\v06754"

$names=@(
"M99_MELA99_COM_API_KEY",
"M99_RABOTNI_DREHI_COM_USERNAME",
"M99_RABOTNI_DREHI_COM_APP_PASSWORD",
"M99_MEDICINSKI_DREHI_COM_API_KEY",
"M99_LAVIRO_RO_API_KEY",
"M99_ALVIRO_RO_API_KEY"
)

function Reveal([Security.SecureString]$s){
  $ptr=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)
  try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
  finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}

foreach($name in $names){
  $p=Join-Path $Store ($name+".dpapi")
  if(-not(Test-Path $p)){ throw "Missing local credential: $name. Run SETUP_V06754_LOCAL_CREDENTIALS.bat first." }
  $enc=(Get-Content -LiteralPath $p -Raw).Trim()
  $sec=ConvertTo-SecureString $enc
  $plain=Reveal $sec
  [Environment]::SetEnvironmentVariable($name,$plain,"Process")
  $plain=$null
}

Set-Location $Repo
Write-Host "Local credentials loaded into this process only." -ForegroundColor Green
Write-Host "Secrets are not printed and are not persisted in Git."
if($Mode -eq "preflight"){
  py -3 scripts\RUN_V06754_CHEROKEE.py preflight
} else {
  py -3 scripts\RUN_V06754_CHEROKEE.py write
}
$code=$LASTEXITCODE
foreach($name in $names){ [Environment]::SetEnvironmentVariable($name,$null,"Process") }
exit $code
