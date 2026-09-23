param(
  [Parameter(Mandatory=$true)][ValidateSet("start","stop","status","restart")][string]$Action
)
$ErrorActionPreference="Stop"
$Repo="C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"
$Admin=Join-Path $Repo "admin-platform"
$Python=Join-Path $Admin ".venv\Scripts\python.exe"
$RuntimeDir=Join-Path $Repo "_m99_runtime"
$PidFile=Join-Path $RuntimeDir "admin_8070.pid"
$IdentityFile=Join-Path $RuntimeDir "admin_8070_identity.json"
$OutLog=Join-Path $RuntimeDir "admin_8070_stdout.log"
$ErrLog=Join-Path $RuntimeDir "admin_8070_stderr.log"
$Port=8070
$ExpectedApp="app.main:app"
New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

function Listener {
  $c=Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if($null -eq $c){ return $null }
  return [int]$c.OwningProcess
}
function ProcInfo([int]$pidValue){
  try {
    $p=Get-CimInstance Win32_Process -Filter "ProcessId=$pidValue"
    if($null -eq $p){return $null}
    return [pscustomobject]@{Pid=[int]$p.ProcessId;Name=$p.Name;ExecutablePath=$p.ExecutablePath;CommandLine=$p.CommandLine;ParentProcessId=[int]$p.ParentProcessId}
  } catch { return $null }
}
function IsExpected($info){
  if($null -eq $info){return $false}
  $exe=[string]$info.ExecutablePath; $cmd=[string]$info.CommandLine
  return ($exe -ieq $Python -and $cmd -match [regex]::Escape("uvicorn") -and $cmd -match [regex]::Escape($ExpectedApp) -and $cmd -match "(--port\s+8070|--port=8070)")
}
function WaitPort([bool]$wantListening,[int]$seconds=12){
  for($i=0;$i -lt ($seconds*4);$i++){
    $pidNow=Listener
    if($wantListening -and $null -ne $pidNow){return $pidNow}
    if((-not $wantListening) -and $null -eq $pidNow){return $null}
    Start-Sleep -Milliseconds 250
  }
  if($wantListening){return Listener}
  return Listener
}
function KillTree([int]$pidValue){
  # taskkill /T is intentionally used only after exact listener identity is established.
  & taskkill.exe /PID $pidValue /T /F | Out-Null
  Start-Sleep -Milliseconds 400
}
function WriteIdentity([int]$pidValue){
  $i=ProcInfo $pidValue
  $obj=[ordered]@{runtime="M99 R7.3.0 R4.2.1";pid=$pidValue;port=$Port;python=$Python;app=$ExpectedApp;started_at=(Get-Date).ToString("s");identity_verified=(IsExpected $i)}
  $obj | ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath $IdentityFile
  Set-Content -LiteralPath $PidFile -Value $pidValue
}
function ShowStatus {
  $lp=Listener
  if($null -eq $lp){
    Write-Host "M99 RUNTIME: STOPPED"
    Write-Host "PORT 8070: FREE"
    return 0
  }
  $i=ProcInfo $lp
  Write-Host ("PID: "+$lp)
  Write-Host ("EXECUTABLE: "+$i.ExecutablePath)
  Write-Host ("COMMAND: "+$i.CommandLine)
  if(IsExpected $i){
    Write-Host "M99 RUNTIME: R4.2.1-compatible"
    Write-Host "PROCESS IDENTITY: VERIFIED"
    Write-Host "PORT 8070: LISTENING"
    return 0
  }
  Write-Host "PROCESS IDENTITY: FOREIGN_OR_UNVERIFIED"
  Write-Host "PORT 8070: OCCUPIED"
  return 21
}
function StopM99 {
  $lp=Listener
  if($null -eq $lp){
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "PORT 8070: FREE"
    Write-Host "M99 ADMIN: STOPPED"
    return 0
  }
  $i=ProcInfo $lp
  if(-not (IsExpected $i)){
    Write-Host ("[STOP] Port 8070 belongs to unverified process PID "+$lp+". It will NOT be killed.")
    Write-Host ("EXECUTABLE: "+$i.ExecutablePath)
    return 22
  }
  Write-Host ("Stopping verified M99 listener PID "+$lp+" and child process tree...")
  KillTree $lp
  $left=WaitPort $false 12
  if($null -ne $left){
    Write-Host ("[FAIL] PORT 8070 still LISTENING on PID "+$left)
    return 23
  }
  if($null -ne (ProcInfo $lp)){
    Write-Host ("[FAIL] PID "+$lp+" still exists after stop.")
    return 24
  }
  Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
  Write-Host ("PID "+$lp+": TERMINATED")
  Write-Host "CHILD PROCESS TREE: TERMINATED"
  Write-Host "PORT 8070: FREE"
  Write-Host "M99 ADMIN: STOPPED"
  return 0
}
function StartM99 {
  if(-not (Test-Path $Python)){Write-Host ("[STOP] Python not found: "+$Python);return 30}
  $lp=Listener
  if($null -ne $lp){
    $i=ProcInfo $lp
    if(IsExpected $i){
      Write-Host ("[INFO] Verified M99 runtime already running on PID "+$lp+". No duplicate start.")
      WriteIdentity $lp
      ShowStatus | Out-Null
      return 0
    }
    Write-Host ("[STOP] Port 8070 occupied by FOREIGN/UNVERIFIED PID "+$lp+".")
    Write-Host ("EXECUTABLE: "+$i.ExecutablePath)
    return 31
  }
  Push-Location $Admin
  try { & $Python -c "import app.main" *> $null; if($LASTEXITCODE -ne 0){Write-Host "[STOP] import app.main failed.";return 32} }
  finally { Pop-Location }
  $env:M99_SESSION_SECRET=([guid]::NewGuid().ToString("N")+[guid]::NewGuid().ToString("N"))
  $p=Start-Process -FilePath $Python -ArgumentList @("-m","uvicorn",$ExpectedApp,"--host","127.0.0.1","--port","8070") -WorkingDirectory $Admin -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog -PassThru
  $lp2=WaitPort $true 12
  if($null -eq $lp2){Write-Host "[FAIL] Runtime did not bind port 8070.";return 33}
  $i2=ProcInfo $lp2
  if(-not (IsExpected $i2)){
    Write-Host ("[FAIL] Listener PID "+$lp2+" failed runtime identity gate.")
    return 34
  }
  WriteIdentity $lp2
  Write-Host "M99 RUNTIME: R4.2.1"
  Write-Host ("PID: "+$lp2)
  Write-Host ("PYTHON: "+$Python)
  Write-Host ("APP: "+$ExpectedApp)
  Write-Host "PORT 8070: LISTENING"
  Write-Host "PROCESS IDENTITY: VERIFIED"
  Write-Host "HEALTH: PROCESS/PATH/PORT PASS"
  return 0
}

$code=0
switch($Action){
 "status" {$code=ShowStatus}
 "stop" {$code=StopM99}
 "start" {$code=StartM99}
 "restart" {$code=StopM99; if($code -eq 0){$code=StartM99}}
}
exit $code
