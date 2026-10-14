<#
.SYNOPSIS   AutoTrigger-TestSuite 快速冒烟验证
.DESCRIPTION 默认只跑少量可控的自制样本；运行前检查工具/依赖/权限/桌面/样本完整性；
             显示样本与副作用，确认后执行；每轮每样本独立结果与日志，不覆盖历史；
             生成本轮汇总并列出「预期 vs 实际」差异。
.PARAMETER AutoTrigger  AutoTrigger.exe 完整路径（必填）
.PARAMETER Profile      quick | standard | blacklist
.PARAMETER Unattended   显式跳过确认（默认不跳过）
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-SmokeTest.ps1 -AutoTrigger C:\path\AutoTrigger.exe
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$AutoTrigger,
  [ValidateSet('quick','standard','blacklist')][string]$Profile = 'quick',
  [string]$Root,
  [switch]$Unattended,
  [int]$TimeoutSec = 120
)
$ErrorActionPreference = 'Continue'

function Say($m, $c = 'Gray') { Write-Host $m -ForegroundColor $c }
function Fail($m) { Say "[失败] $m" 'Red'; exit 2 }
function Warn($m) { Say "[警告] $m" 'Yellow' }

if (-not $Root) { try { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) } catch { } }
if (-not $Root) { $Root = (Get-Location).Path }
$Root = $Root.TrimEnd([char]92)

Say "==== AutoTrigger-TestSuite 冒烟验证 ====" 'Cyan'
Say "套件根目录: $Root"
Say "Profile    : $Profile"
Say ""

Say "---- 1/6 前置检查 ----" 'Cyan'
if (-not (Test-Path -LiteralPath $AutoTrigger)) { Fail "找不到 AutoTrigger: $AutoTrigger" }
$verLine = ((& $AutoTrigger --version 2>&1 | Out-String) -split [char]10 | Where-Object { $_.Trim().StartsWith("{") } | Select-Object -First 1)
if (-not $verLine) { Fail "无法获取 --version（核对 AutoTrigger 路径）" }
Say "  工具版本: $($verLine.Trim())"

$adm = (New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($adm) { Say "  权限: 管理员" 'Green' } else { Warn "  当前未提权：需要管理员的样本会被排除，结果不代表安装能力" }

$cap = $null
$capLine = ((& $AutoTrigger --capabilities 2>&1 | Out-String) -split [char]10 | Where-Object { $_.Trim().StartsWith("{") } | Select-Object -First 1)
if ($capLine) { try { $cap = $capLine | ConvertFrom-Json } catch { } }
if ($cap) {
  Say ("  7-Zip : " + $cap.prereq.archive_backend_status)
  Say ("  OCR   : " + $cap.prereq.ocr_engine_status)
  Say ("  GUI   : " + $cap.capabilities.gui_automation + " / 内置模板: " + $cap.capabilities.builtin_templates)
} else { Warn "  无法解析 --capabilities 输出" }

$sess = (Get-Process -Id $PID).SessionId
$expl = Get-Process explorer -ErrorAction SilentlyContinue | Where-Object { $_.SessionId -eq $sess }
if ($expl) { Say "  交互式桌面: 有 explorer（会话 $sess）" 'Green' } else { Warn "  会话 $sess 未检测到 explorer：GUI 自动化样本可能失败" }

Say ""
Say "---- 2/6 选择样本 ----" 'Cyan'
$sets = @{
  quick = @(
    @{ rel='samples\14-跳过与兜底\01-空文件.exe';     expect='skipped'; side='无' },
    @{ rel='samples\14-跳过与兜底\02-空文件.dat';     expect='skipped'; side='无' },
    @{ rel='samples\14-跳过与兜底\03-单字节文件.bin'; expect='failed';  side='无' }
  )
  standard = @(
    @{ rel='samples\14-跳过与兜底\01-空文件.exe';     expect='skipped'; side='无' },
    @{ rel='samples\14-跳过与兜底\03-单字节文件.bin'; expect='failed';  side='无' },
    @{ rel='samples\09-类型识别与伪装\实际是ZIP的exe.exe'; expect='triggered'; side='解压到 %TEMP%' },
    @{ rel='samples\20-静默参数探测\F13-参数探测桩-见VERYSILENT即成功.exe'; expect='install_completed'; side='写哨兵日志'; needAdmin=$true },
    @{ rel='samples\17-合成安装器(Inno)\INNO-01-静默安装成功.exe'; expect='install_completed'; side='安装到 Program Files'; needAdmin=$true },
    @{ rel='samples\18-合成安装器(NSIS)\NSIS-01-静默安装成功.exe'; expect='install_completed'; side='安装到 Program Files'; needAdmin=$true }
  )
  blacklist = @(
    @{ rel='samples\10-入口分层与黑名单\A25-01-规范包-含黑名单'; expect='无 VIOLATION'; side='入口脚本会跑；11 个黑名单陷阱不得执行' }
  )
}
$sel = @($sets[$Profile])

if (-not $adm) {
  $adminJobs = @($sel | Where-Object { $_.needAdmin })
  if ($adminJobs.Count -gt 0) {
    Warn "  本轮有 $($adminJobs.Count) 个样本需要管理员权限，当前未提权，已排除："
    foreach ($x in $adminJobs) { Warn ("      - " + $x.rel) }
    $sel = @($sel | Where-Object { -not $_.needAdmin })
  }
}
if ($sel.Count -eq 0) { Fail "没有可执行的样本（可能全部需要管理员）" }

$missing = @($sel | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Root $_.rel)) })
if ($missing.Count -gt 0) {
  foreach ($m in $missing) { Say ("  缺失: " + $m.rel) 'Red' }
  Fail "样本缺失，请确认套件完整（可运行 scripts\Get-SampleManifest.ps1 校验）"
}
Say "  本次将执行 $($sel.Count) 项："
foreach ($s in $sel) {
  Say ("    - {0}" -f $s.rel)
  Say ("        预期: {0}   副作用: {1}" -f $s.expect, $s.side) 'DarkGray'
}

Say ""
Say "---- 3/6 确认 ----" 'Cyan'
if ($Unattended) { Say "  -Unattended：跳过确认" 'Yellow' }
else {
  Say "  即将在本机执行上述样本，可能产生文件/注册表/进程变化。" 'Yellow'
  $a = Read-Host "  继续？(yes/no)"
  if ($a -ne 'yes') { Say "已取消。" 'Yellow'; exit 0 }
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir = Join-Path $Root ("runs\" + $stamp)
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
Say ""
Say "---- 4/6 执行（结果目录 runs\$stamp）----" 'Cyan'
$rows = @()
foreach ($s in $sel) {
  $full = Join-Path $Root $s.rel
  $safe = ($s.rel -replace '[\\/:*?"<>|]','_')
  $json = Join-Path $outDir ($safe + '.json')
  $log  = Join-Path $outDir ($safe + '.log')
  $con  = Join-Path $outDir ($safe + '.console.txt')
  Say "  >> $($s.rel)"
  $sw = [Diagnostics.Stopwatch]::StartNew()
  & $AutoTrigger --input $full --output $json --log-file $log --timeout $TimeoutSec --log-level debug --no-lock 2>&1 | Out-File -LiteralPath $con -Encoding utf8
  $code = $LASTEXITCODE
  $sw.Stop()
  $status = '(无结果)'; $conf = ''
  if (Test-Path -LiteralPath $json) {
    try { $j = Get-Content -LiteralPath $json -Raw -Encoding utf8 | ConvertFrom-Json
          if ($j.results -and $j.results.Count -gt 0) { $status = $j.results[0].final_status; $conf = $j.results[0].install_confidence } }
    catch { $status = '(解析失败)' }
  }
  $viol = 0
  if ($Profile -eq 'blacklist') { $viol = @(Get-ChildItem 'C:\Users\Public\AT-SENTINEL' -Filter 'VIOLATION-*' -ErrorAction SilentlyContinue).Count }
  $rows += [pscustomobject]@{ 样本=$s.rel; 预期=$s.expect; 实际=$status; 置信度=$conf; 退出码=$code; 耗时秒=[math]::Round($sw.Elapsed.TotalSeconds,1); VIOLATION=$viol }
}

Say ""
Say "---- 5/6 汇总 ----" 'Cyan'
$rows | Format-Table 样本,预期,实际,置信度,耗时秒 -AutoSize | Out-String | Write-Host
$bad = @($rows | Where-Object { ($_.预期 -eq '无 VIOLATION' -and $_.VIOLATION -gt 0) -or ($_.预期 -ne '无 VIOLATION' -and $_.实际 -ne $_.预期) })
$md = @()
$md += "# 冒烟验证 $stamp"
$md += ""
$md += "- 工具: $AutoTrigger"
$md += "- 版本: $($verLine.Trim())"
$md += "- 权限: $(if($adm){'管理员'}else{'未提权'})"
$md += "- Profile: $Profile   超时: $TimeoutSec s"
$md += ""
$md += "| 样本 | 预期 | 实际 | 置信度 | 退出码 | 耗时秒 | VIOLATION |"
$md += "|---|---|---|---|---|---|---|"
foreach ($r in $rows) { $md += "| $($r.样本) | $($r.预期) | $($r.实际) | $($r.置信度) | $($r.退出码) | $($r.耗时秒) | $($r.VIOLATION) |" }
$md += ""
if ($bad.Count -gt 0) {
  $md += "## 与预期不符（$($bad.Count)）"
  foreach ($r in $bad) { $md += "- $($r.样本)：预期 $($r.预期)，实际 $($r.实际)" }
} else { $md += "## 与预期不符：无（全部符合）" }
$md += ""
$md += "> install_unverified / triggered 不等于安装成功；成功率口径见 reports/README.md。"
$mdPath = Join-Path $outDir 'summary.md'
$md | Set-Content -LiteralPath $mdPath -Encoding utf8
Say "  汇总: $mdPath"

Say ""
Say "---- 6/6 结论 ----" 'Cyan'
if ($bad.Count -gt 0) { Say "  有 $($bad.Count) 项与预期不符（见上表）" 'Yellow'; exit 1 }
Say "  全部符合预期" 'Green'; exit 0
