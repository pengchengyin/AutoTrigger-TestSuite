<#
.SYNOPSIS
  AutoTrigger-TestSuite 样本级批量测试（逐个样本调用，独立归档）。
.DESCRIPTION
  遍历 samples\ 下选定分组，把「组根目录下的每个条目（文件或目录）」当作一个样本，
  逐个调用 AutoTrigger，产出独立的结果 JSON / 日志 / 控制台输出；
  目录类样本（安装包目录）整体输入，不拆分子项统计。
  运行结束后生成本轮 per-sample.csv 与 summary.md。
  系统级样本需要管理员权限，建议在提权会话中运行。
.PARAMETER AutoTrigger   AutoTrigger.exe 完整路径（必填）。
.PARAMETER Groups        要测试的分组名通配（默认全部）。
.PARAMETER ExcludeGroups 要排除的分组名通配。
.PARAMETER TimeoutSec    单个样本的硬超时秒数（默认 180）。
.PARAMETER OutRoot       结果根目录（默认 <套件>\runs）。
.PARAMETER Root          套件根目录（默认脚本的上两级）。
.PARAMETER SkipCleanup   运行前不执行清理脚本。
.PARAMETER ListOnly      只列出将要执行的样本，不执行。
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-SampleTest.ps1 -AutoTrigger C:\path\AutoTrigger.exe
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-SampleTest.ps1 -AutoTrigger C:\path\AutoTrigger.exe -Groups '17-*','18-*','19-*'
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$AutoTrigger,
  [string[]]$Groups = @('*'),
  [string[]]$Samples = @(),
  [string[]]$SkipDirs = @(),
  [string[]]$ExcludeGroups = @(),
  [int]$TimeoutSec = 180,
  [string]$OutRoot,
  [string]$Root,
  [switch]$SkipCleanup,
  [switch]$ListOnly
)

$ErrorActionPreference = 'Continue'
function Say($m, $c = 'Gray') { Write-Host $m -ForegroundColor $c }

if (-not $Root) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$Root = $Root.TrimEnd([char]92)
if (-not $OutRoot) { $OutRoot = Join-Path $Root 'runs' }
$samplesRoot = Join-Path $Root 'samples'
if (-not (Test-Path -LiteralPath $AutoTrigger)) { Say "[失败] 找不到 AutoTrigger: $AutoTrigger" 'Red'; exit 2 }
if (-not (Test-Path -LiteralPath $samplesRoot)) { Say "[失败] 找不到样本目录: $samplesRoot" 'Red'; exit 2 }

# 非样本条目（运行副作用目录等），不作为输入样本
$excludeEntries = @('UsersPublicAT-SENTINEL')

Say '==== AutoTrigger-TestSuite 样本级批量测试 ====' 'Cyan'
Say "套件根目录: $Root"
Say "工具      : $AutoTrigger"
Say "单样本超时: $TimeoutSec s"
Say ''

$adm = (New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($adm) { Say '权限: 管理员' 'Green' } else { Say '权限: 未提权（系统级样本会失败）' 'Yellow' }

# 选定分组
$allDirs = @(Get-ChildItem -LiteralPath $samplesRoot -Directory -ErrorAction SilentlyContinue | Sort-Object Name)
$groupDirs = @()
$seenNames = @{}
foreach ($p in $Groups) {
  foreach ($d in $allDirs) {
    if ($d.Name -notlike $p) { continue }
    if ($seenNames.ContainsKey($d.Name)) { continue }
    $drop = $false
    foreach ($x in $ExcludeGroups) { if ($d.Name -like $x) { $drop = $true } }
    if ($drop) { continue }
    $seenNames[$d.Name] = $true
    $groupDirs += $d
  }
}

# 顶层层级条目 = 一个样本（目录样本整体输入）
$items = @()
foreach ($g in $groupDirs) {
  foreach ($e in (Get-ChildItem -LiteralPath $g.FullName -Force -ErrorAction SilentlyContinue | Sort-Object Name)) {
    if ($excludeEntries -contains $e.Name) { continue }
    $rel = $g.Name + '\' + $e.Name
    $items += [pscustomobject]@{ Group = $g.Name; Rel = $rel; Full = $e.FullName; IsDir = $e.PSIsContainer }
  }
}
foreach ($s in $Samples) {
  $full = Join-Path $samplesRoot $s
  if (-not (Test-Path -LiteralPath $full)) { Say "[警告] 找不到指定样本: $s" 'Yellow'; continue }
  if (@($items | Where-Object { $_.Rel -eq $s }).Count -gt 0) { continue }
  $parts = $s.Split([char]92)
  $item = Get-Item -LiteralPath $full
  $items += [pscustomobject]@{ Group = $parts[0]; Rel = $s; Full = $full; IsDir = $item.PSIsContainer }
}

Say ("选中分组 {0} 个，样本条目 {1} 个。" -f $groupDirs.Count, $items.Count)
$items | Group-Object Group | Sort-Object Name | ForEach-Object { Say ("   {0,-28} {1}" -f $_.Name, $_.Count) }
if ($ListOnly) { $items | ForEach-Object { Say ('   ' + $_.Rel) 'DarkGray' }; exit 0 }

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir = Join-Path $OutRoot $stamp
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
Say ''
Say "结果目录: $outDir" 'Cyan'

if (-not $SkipCleanup) {
  $clean = Join-Path $Root 'scripts\Cleanup-SyntheticSamples.ps1'
  if (Test-Path -LiteralPath $clean) {
    Say '---- 运行前清理 ----' 'Cyan'
    & $clean *>&1 | ForEach-Object { Say "   $_" 'DarkGray' }
  }
}

if (-not $SkipDirs -or $SkipDirs.Count -eq 0) {
  $SkipDirs = @(Get-ChildItem -LiteralPath $OutRoot -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^[0-9]{8}-[0-9]{6}$' -and $_.FullName -ne $outDir } | Select-Object -ExpandProperty FullName)
}
if ($SkipDirs.Count -gt 0) { Say ("续跑：跳过 $($SkipDirs.Count) 个已有结果目录中的样本") 'Yellow' }

$sentinel = 'C:\Users\Public\AT-SENTINEL'
$rows = @()
$i = 0
foreach ($it in $items) {
  $i++
  $safe = ($it.Rel -replace '[\\/:*?"<>|]', '_')
  $json = Join-Path $outDir ($safe + '.json')
  $log  = Join-Path $outDir ($safe + '.log')
  $con  = Join-Path $outDir ($safe + '.console.txt')
  $skipHit = $false
  foreach ($sd in $SkipDirs) { if (Test-Path -LiteralPath (Join-Path $sd ($safe + '.json'))) { $skipHit = $true; break } }
  if ($skipHit) { Say ("[{0}/{1}] {2} -> 已有结果，跳过" -f $i, $items.Count, $it.Rel) 'DarkGray'; continue }
  Say ("[{0}/{1}] {2}" -f $i, $items.Count, $it.Rel) 'White'
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $qa = '"' + $AutoTrigger + '" --input "' + $it.Full + '" --output "' + $json + '" --log-file "' + $log + '" --timeout ' + $TimeoutSec + ' --log-level debug --no-lock'
  cmd.exe /c ($qa + ' > "' + $con + '" 2>&1') | Out-Null
  $code = $LASTEXITCODE
  $sw.Stop()

  $status = ''; $conf = ''; $ev = ''; $byStatus = ''; $flags = ''; $err = ''
  if (Test-Path -LiteralPath $json) {
    try {
      $j = Get-Content -LiteralPath $json -Raw -Encoding utf8 | ConvertFrom-Json
      $res = @($j.results)
      if ($res.Count -eq 1) {
        $status = $res[0].final_status
        $conf = $res[0].install_confidence
      } elseif ($res.Count -gt 1) {
        $status = '容器展开'
      } else {
        $status = '(无结果项)'
      }
      if ($res.Count -ge 1) {
        $ids = @()
        foreach ($a in @($res[0].attempts)) { foreach ($e in @($a.install_evidence)) { if ($e.id) { $ids += $e.id } } }
        $ev = ($ids | Select-Object -Unique) -join '/'
      }
      $byStatus = (@($j.summary.by_status.PSObject.Properties | Where-Object { $_.Value -gt 0 } | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ')
      $flags = (@($j.summary.flags.PSObject.Properties | Where-Object { $_.Value -gt 0 } | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ')
      $err = $j.error
      if ($res.Count -gt 1) { $byStatus = "results=$($res.Count) " + $byStatus }
    } catch { $status = '(解析失败)' }
  } else { $status = '(无结果)' }

  $viol = 0
  if (Test-Path -LiteralPath $sentinel) { $viol = @(Get-ChildItem -LiteralPath $sentinel -Filter 'VIOLATION-*' -ErrorAction SilentlyContinue).Count }

  $rows += [pscustomobject]@{
    分组 = $it.Group; 样本 = $it.Rel; 类型 = $(if ($it.IsDir) { '目录' } else { '文件' });
    最终状态 = $status; 置信度 = $conf; 证据 = $ev; 状态分布 = $byStatus; 标记 = $flags;
    退出码 = $code; 耗时秒 = [math]::Round($sw.Elapsed.TotalSeconds, 1); VIOLATION = $viol
  }
  Say ("       => {0}  置信度={1}  {2}s  {3}" -f $status, $conf, [math]::Round($sw.Elapsed.TotalSeconds, 1), $byStatus) 'DarkGray'
}

if (Test-Path -LiteralPath $sentinel) { Copy-Item -LiteralPath $sentinel -Destination (Join-Path $outDir 'sentinel') -Recurse -Force -ErrorAction SilentlyContinue }

Say ''
Say '---- 汇总 ----' 'Cyan'
$rows | Format-Table 分组,最终状态,置信度,耗时秒 -AutoSize | Out-String | Write-Host
$rows | Export-Csv -LiteralPath (Join-Path $outDir 'per-sample.csv') -NoTypeInformation -Encoding UTF8

$byGroup = $rows | Group-Object 分组 | Sort-Object Name | ForEach-Object {
  $c = @($_.Group | Group-Object 最终状态 | ForEach-Object { "$($_.Name)=$($_.Count)" })
  [pscustomobject]@{ 分组 = $_.Name; 样本数 = $_.Count; 状态分布 = ($c -join ' ') }
}
$byGroup | Format-Table -AutoSize | Out-String | Write-Host

$verLine = ((& $AutoTrigger --version 2>&1 | Out-String).Trim())
$md = @()
$md += "# 样本级批量测试 $stamp"
$md += ""
$md += "- 工具: $AutoTrigger"
$md += "- 版本: $verLine"
$md += "- 权限: $(if ($adm) { '管理员' } else { '未提权' })"
$md += "- 单样本超时: $TimeoutSec s"
$md += "- 样本条目: $($items.Count)（分组 $($groupDirs.Count) 个）"
$md += ""
$md += "## 分组状态分布"
$md += ""
$md += "| 分组 | 样本数 | 状态分布 |"
$md += "|---|---|---|"
foreach ($g in $byGroup) { $md += "| $($g.分组) | $($g.样本数) | $($g.状态分布) |" }
$md += ""
$md += "## 逐样本结果"
$md += ""
$md += "| 分组 | 样本 | 类型 | 最终状态 | 置信度 | 证据 | 退出码 | 耗时秒 | VIOLATION |"
$md += "|---|---|---|---|---|---|---|---|---|"
foreach ($r in $rows) { $md += "| $($r.分组) | $($r.样本) | $($r.类型) | $($r.最终状态) | $($r.置信度) | $($r.证据) | $($r.退出码) | $($r.耗时秒) | $($r.VIOLATION) |" }
$md += ""
$md += "> install_unverified / triggered / install_partial / killed_on_timeout 不等于安装成功。"
$md | Out-File -LiteralPath (Join-Path $outDir 'summary.md') -Encoding utf8

Say ''
if (Test-Path -LiteralPath $sentinel) {
  $viol = @(Get-ChildItem -LiteralPath $sentinel -Filter 'VIOLATION-*' -ErrorAction SilentlyContinue)
  if ($viol.Count -gt 0) { Say ("[失败] 黑名单文件被执行: " + ($viol.Name -join ', ')) 'Red' } else { Say '[通过] 未发现黑名单文件被执行' 'Green' }
}
Say "结果与日志已归档: $outDir" 'Cyan'
