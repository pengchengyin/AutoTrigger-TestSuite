<#
.SYNOPSIS  校验自制样本与 manifests 是否一致（SHA-256 / 大小）
.EXAMPLE   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-SampleManifest.ps1
#>
[CmdletBinding()]
param([string]$Root, [switch]$ThirdParty)
$ErrorActionPreference = 'Continue'
if (-not $Root) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$file = if ($ThirdParty) { Join-Path $Root 'manifests\samples.thirdparty.json' } else { Join-Path $Root 'manifests\samples.selfmade.json' }
if (-not (Test-Path -LiteralPath $file)) { Write-Host "[失败] 找不到清单 $file" -ForegroundColor Red; exit 2 }
$m = Get-Content -LiteralPath $file -Raw -Encoding utf8 | ConvertFrom-Json
Write-Host "==== 校验 $($m.count) 条（$([IO.Path]::GetFileName($file))）====" -ForegroundColor Cyan
$ok = 0; $bad = 0; $gone = 0
foreach ($s in $m.samples) {
  $p = Join-Path $Root ('samples\' + ($s.rel_path -replace '/', '\'))
  if (-not (Test-Path -LiteralPath $p)) { $gone++; Write-Host ("  [缺失] " + $s.rel_path) -ForegroundColor DarkGray; continue }
  if (-not $s.sha256) { Write-Host ("  [无哈希] " + $s.rel_path) -ForegroundColor Yellow; continue }
  $h = (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash
  if ($h -eq $s.sha256) { $ok++ } else { $bad++; Write-Host ("  [不一致] " + $s.rel_path) -ForegroundColor Red; Write-Host ("      期望 " + $s.sha256); Write-Host ("      实际 " + $h) }
}
Write-Host ""
Write-Host ("结果: 一致 $ok / 不一致 $bad / 缺失 $gone") -ForegroundColor $(if($bad -eq 0){'Green'}else{'Yellow'})
if ($bad -gt 0) { exit 1 }
exit 0
