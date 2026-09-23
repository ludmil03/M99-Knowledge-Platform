param([ValidateSet("restart","start","stop","status")][string]$Action="restart")
$ErrorActionPreference="Stop"
$Repo="C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
$Admin=Join-Path $Repo "admin-platform"
$VenvPython=Join-Path $Admin ".venv\Scripts\python.exe"
$State=Join-Path $Repo "_m99_runtime"
$SecretFile=Join-Path $State "session_secret.txt"
$Port=8070
New-Item -ItemType Directory -Force $State | Out-Null

function Get-Listener {
  try { return Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -State Listen -ErrorAction Stop | Select-Object -First 1 }
  catch { return $null }
}
function Get-Proc([int]$ProcessId) {
  try { return Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" }
  catch { return $null }
}
function Get-Identity([int]$ProcessId) {
  $p=Get-Proc -ProcessId $ProcessId
  if(-not $p){ return @{Ok=$false; Reason="PROCESS_NOT_FOUND"} }
  $cmd=[string]$p.CommandLine
  $exe=[string]$p.ExecutablePath
  $venvQuoted=[regex]::Escape('"' + $VenvPython + '"')
  $venvPlain=[regex]::Escape($VenvPython)
  $launcherOk=($cmd -match $venvQuoted -or $cmd -match $venvPlain)
  $uvicornOk=($cmd -match '(?i)(-m\s+uvicorn|uvicorn(?:\.exe|\.py)?)')
  $appOk=($cmd -match '(?i)app\.main:app')
  $hostOk=($cmd -match '(?i)--host\s+127\.0\.0\.1')
  $portOk=($cmd -match '(?i)--port\s+8070')
  return @{Ok=($launcherOk -and $uvicornOk -and $appOk -and $hostOk -and $portOk);
           Exe=$exe; Cmd=$cmd; LauncherOk=$launcherOk; UvicornOk=$uvicornOk; AppOk=$appOk; HostOk=$hostOk; PortOk=$portOk}
}
function Show-Identity([int]$ProcessId) {
  $i=Get-Identity -ProcessId $ProcessId
  Write-Host "LISTENER_PID: $ProcessId"
  Write-Host "LISTENER_EXE: $($i.Exe)"
  Write-Host "LISTENER_CMD: $($i.Cmd)"
  Write-Host "IDENTITY: launcher=$($i.LauncherOk) uvicorn=$($i.UvicornOk) app=$($i.AppOk) host=$($i.HostOk) port=$($i.PortOk)"
}
function Get-Secret {
  if(Test-Path $SecretFile){
    $s=(Get-Content -Raw $SecretFile).Trim()
    if($s.Length -ge 32){ return $s }
  }
  $s=[guid]::NewGuid().ToString("N")+[guid]::NewGuid().ToString("N")
  Set-Content -NoNewline -Encoding ASCII $SecretFile $s
  return $s
}
function Stop-M99 {
  $l=Get-Listener
  if(-not $l){ Write-Host "[PASS] port 8070 already free"; return 0 }
  Show-Identity -ProcessId $l.OwningProcess
  $id=Get-Identity -ProcessId $l.OwningProcess
  if(-not $id.Ok){ Write-Host "[STOP] foreign/unverified listener; refusing kill"; return 20 }
  Stop-Process -Id $l.OwningProcess -Force
  for($n=0;$n-lt 40;$n++){ Start-Sleep -Milliseconds 200; if(-not(Get-Listener)){Write-Host "[PASS] verified M99 runtime stopped; port free";return 0}}
  Write-Host "[STOP] verified runtime did not release port"; return 21
}
function Start-M99 {
  if(Get-Listener){ Write-Host "[STOP] port 8070 is occupied before start"; return 10 }
  $env:M99_SESSION_SECRET=Get-Secret
  Push-Location $Admin
  try {
    $import=& $VenvPython -c "import app.main; print('IMPORT_OK')" 2>&1
    if($LASTEXITCODE-ne 0){$import|ForEach-Object{Write-Host $_};Write-Host "[STOP] import gate";return 11}
    Write-Host "[PASS] session-secret bootstrap + import"
    $out=Join-Path $State "admin_8070_stdout.log";$err=Join-Path $State "admin_8070_stderr.log"
    Start-Process -FilePath $VenvPython -ArgumentList @("-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8070") -WorkingDirectory $Admin -RedirectStandardOutput $out -RedirectStandardError $err -WindowStyle Hidden | Out-Null
  } finally { Pop-Location }
  $l=$null
  for($n=0;$n-lt 60;$n++){Start-Sleep -Milliseconds 250;$l=Get-Listener;if($l){break}}
  if(-not $l){Write-Host "[STOP] no listener after start";return 12}
  Show-Identity -ProcessId $l.OwningProcess
  $id=Get-Identity -ProcessId $l.OwningProcess
  if(-not $id.Ok){Write-Host "[STOP] listener identity failed; no kill";return 13}
  try{$h=Invoke-RestMethod -Uri "http://127.0.0.1:8070/r43/health" -TimeoutSec 5}catch{Write-Host "[STOP] /r43/health failed";return 14}
  if($h.status-ne "ok" -or $h.version-ne "R4.3"){Write-Host "[STOP] health contract mismatch";return 15}
  try{$r=Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8070/r43/control-center" -TimeoutSec 5}catch{Write-Host "[STOP] Control Center route failed";return 16}
  if($r.StatusCode-ne 200){Write-Host "[STOP] Control Center HTTP != 200";return 17}
  Write-Host "[PASS] WINDOWS VENV LAUNCHER IDENTITY"
  Write-Host "[PASS] R4.3 HEALTH"
  Write-Host "[PASS] CONTROL CENTER HTTP 200"
  Start-Process "http://127.0.0.1:8070/r43/control-center"
  return 0
}
function Status-M99 {
  $l=Get-Listener
  if(-not $l){Write-Host "M99 RUNTIME: STOPPED";return 3}
  Show-Identity -ProcessId $l.OwningProcess
  $id=Get-Identity -ProcessId $l.OwningProcess
  if($id.Ok){Write-Host "M99 RUNTIME: VERIFIED";return 0}
  Write-Host "M99 RUNTIME: FOREIGN/UNVERIFIED";return 4
}
if($Action-eq"stop"){exit(Stop-M99)}
if($Action-eq"status"){exit(Status-M99)}
if($Action-eq"start"){exit(Start-M99)}
$ec=Stop-M99
if($ec-ne 0){exit $ec}
exit(Start-M99)
