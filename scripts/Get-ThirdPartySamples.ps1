<#
.SYNOPSIS  按 manifests 下载第三方样本（本仓库不代发这些安装包）
.DESCRIPTION 仅使用清单中登记的官方直链；未登记来源的条目会被明确跳过并列出。
.EXAMPLE   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-ThirdPartySamples.ps1
#>
[CmdletBinding()]
param([string]$Root, [switch]$WhatIf)
$ErrorActionPreference = 'Continue'
if (-not $Root) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$file = Join-Path $Root 'manifests\samples.thirdparty.json'
$m = Get-Content -LiteralPath $file -Raw -Encoding utf8 | ConvertFrom-Json
Write-Host "==== 第三方样本 $($m.count) 条 ====" -ForegroundColor Cyan
$noUrl = @($m.samples | Where-Object { -not $_.download_url })
Write-Host "其中有官方直链 $((@($m.samples | Where-Object { $_.download_url })).Count) 条；未登记来源 $($noUrl.Count) 条" -ForegroundColor Yellow
if ($noUrl.Count -gt 0) {
  Write-Host "以下条目【官方下载地址未提供】，请自行从厂商官网获取对应版本：" -ForegroundColor Yellow
  foreach ($s in $noUrl) { Write-Host ("  - " + $s.rel_path) }
}
foreach ($s in $m.samples) {
  if (-not $s.download_url) { continue }
  $dest = Join-Path $Root ('samples\' + ($s.rel_path -replace '/', '\'))
  if (Test-Path -LiteralPath $dest) {
    $h = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash
    if ($h -eq $s.sha256) { Write-Host ("  [已存在] " + $s.rel_path) -ForegroundColor DarkGray; continue }
    Write-Host ("  [哈希不符，将重新下载] " + $s.rel_path) -ForegroundColor Yellow
  }
  if ($WhatIf) { Write-Host ("  [试运行] 将下载 " + $s.download_url); continue }
  New-Item -ItemType Directory -Force (Split-Path $dest -Parent) | Out-Null
  Write-Host ("  下载 " + $s.name) -ForegroundColor Gray
  try { Invoke-WebRequest -Uri $s.download_url -OutFile $dest -UseBasicParsing -TimeoutSec 600 } catch { Write-Host ("    [失败] " + $_.Exception.Message) -ForegroundColor Red; continue }
  $h = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash
  if ($h -eq $s.sha256) { Write-Host "    [一致]" -ForegroundColor Green } else { Write-Host ("    [哈希不一致] 期望 " + $s.sha256 + " 实际 " + $h) -ForegroundColor Red }
}
