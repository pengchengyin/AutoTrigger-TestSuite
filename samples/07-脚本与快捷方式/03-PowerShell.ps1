$d='C:\Users\Public\AT-SENTINEL'
if(!(Test-Path $d)){New-Item -ItemType Directory -Path $d | Out-Null}
Add-Content -Path (Join-Path $d 'ran.log') -Value 'SCRIPT-ps1'
Write-Host 'ps1 executed'
