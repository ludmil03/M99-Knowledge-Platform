$ErrorActionPreference="Stop"
$Store=Join-Path $env:LOCALAPPDATA "M99\credentials\v06754"
New-Item -ItemType Directory -Force -Path $Store | Out-Null

$items=@(
  @{Name="M99_MELA99_COM_API_KEY"; Label="mela99.com Webservice API key"},
  @{Name="M99_RABOTNI_DREHI_COM_USERNAME"; Label="rabotni-drehi.com WordPress username"},
  @{Name="M99_RABOTNI_DREHI_COM_APP_PASSWORD"; Label="rabotni-drehi.com Application Password"},
  @{Name="M99_MEDICINSKI_DREHI_COM_API_KEY"; Label="medicinski-drehi.com Webservice API key"},
  @{Name="M99_LAVIRO_RO_API_KEY"; Label="laviro.ro Webservice API key"},
  @{Name="M99_ALVIRO_RO_API_KEY"; Label="alviro.ro Webservice API key"}
)

Write-Host "M99 v0.6.7.5.4 - LOCAL CREDENTIAL SETUP" -ForegroundColor Cyan
Write-Host "Storage: Windows DPAPI, current Windows user, outside Git repository."
Write-Host "Secrets will not be printed."
Write-Host ""

foreach($i in $items){
  $path=Join-Path $Store ($i.Name+".dpapi")
  if(Test-Path $path){
    $ans=Read-Host "$($i.Label) already exists. Type REPLACE to overwrite, or Enter to keep"
    if($ans -ne "REPLACE"){
      Write-Host "$($i.Name): KEPT"
      continue
    }
  }
  $sec=Read-Host $i.Label -AsSecureString
  if($sec.Length -eq 0){ throw "Empty value is not allowed for $($i.Name)" }
  $enc=ConvertFrom-SecureString $sec
  Set-Content -LiteralPath $path -Value $enc -Encoding ASCII
  Write-Host "$($i.Name): SAVED (encrypted)"
}

Write-Host ""
Write-Host "Credential setup complete." -ForegroundColor Green
Write-Host "No credential was written into the repository."
Read-Host "Press Enter"
