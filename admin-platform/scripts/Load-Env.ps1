param([string]$Path)
if(-not(Test-Path -LiteralPath $Path)){throw "Env file not found: $Path"}
Get-Content -LiteralPath $Path | ForEach-Object {
 $line=$_.Trim()
 if(-not $line -or $line.StartsWith("#")){return}
 $i=$line.IndexOf("=");if($i -lt 1){return}
 [Environment]::SetEnvironmentVariable($line.Substring(0,$i).Trim(),$line.Substring($i+1),"Process")
}
