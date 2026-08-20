$ErrorActionPreference="Stop"
$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$EnvFile=Join-Path $Root ".env.local"
if(Test-Path -LiteralPath $EnvFile){Write-Host ".env.local already exists. It will NOT be overwritten.";exit 0}
$bytes=New-Object byte[] 48
[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$secret=[Convert]::ToBase64String($bytes)
@"
M99_APP_NAME=M99 Knowledge Platform
M99_ENV=development
M99_HOST=127.0.0.1
M99_PORT=8070
M99_DATABASE_URL=sqlite:///./data/m99_admin.db
M99_SESSION_SECRET=$secret
M99_SESSION_HTTPS_ONLY=false
M99_SESSION_MAX_AGE=28800
"@ | Set-Content -LiteralPath $EnvFile -Encoding UTF8
Write-Host "Created .env.local with a random session secret."
Write-Host "This file is ignored by Git."
