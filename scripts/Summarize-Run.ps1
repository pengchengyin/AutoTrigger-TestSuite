<#
.SYNOPSIS 汇总一次或多次「样本级测试」结果目录，合并生成 per-sample.csv 与 summary.md。
.DESCRIPTION
  按 samples\ 的「组根目录条目」枚举样本，在给定的结果目录里查找同名 .json 并解析
  final_status / install_confidence / 证据 ID / by_status，输出合并后的逐样本 CSV 与分组汇总。
  用途：把多次 Invoke-SampleTest.ps1 的运行（例如中断后续跑）合并成一份报告。
.PARAMETER RunDir        一个或多个结果目录（先出现的优先）。
.PARAMETER Root          套件根目录（默认脚本的上两级）。
.PARAMETER OutDir        输出目录（默认第一个结果目录）。
.PARAMETER Groups        纳入的分组名通配（默认全部）。
.PARAMETER ExcludeGroups 排除的分组名通配。
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string[]]$RunDir,
  [string]$Root,
  [string]$OutDir,
  [string[]]$Groups = @('*'),
  [string[]]$ExcludeGroups = @()
)
$ErrorActionPreference = 'Continue'
if (-not $Root) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$Root = $Root.TrimEnd([char]92)
$samplesRoot = Join-Path $Root 'samples'
$excludeEntries = @('UsersPublicAT-SENTINEL')
if (-not $OutDir) { $OutDir = $RunDir[0] }
if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

$allDirs = @(Get-ChildItem -LiteralPath $samplesRoot -Directory -ErrorAction SilentlyContinue | Sort-Object Name)
$groupDirs = @()
foreach ($p in $Groups) {
  foreach ($d in $allDirs) {
    if ($d.Name -notlike $p) { continue }
    if (@($groupDirs | Where-Object { $_.Name -eq $d.Name }).Count -gt 0) { continue }
    $drop = $false
    foreach ($x in $ExcludeGroups) { if ($d.Name -like $x) { $drop = $true } }
    if ($drop) { continue }
    $groupDirs += $d
  }
}

$rows = @()
foreach ($g in $groupDirs) {
  foreach ($e in (Get-ChildItem -LiteralPath $g.FullName -Force -ErrorAction SilentlyContinue | Sort-Object Name)) {
    if ($excludeEntries -contains $e.Name) { continue }
    $rel = $g.Name + '\' + $e.Name
    $safe = ($rel -replace '[\\/:*?"<>|]', '_')
    $jsonPath = $null
    foreach ($rd in $RunDir) {
      $cand = Join-Path $rd ($safe + '.json')
      if (Test-Path -LiteralPath $cand) { $jsonPath = $cand; break }
    }
    $status = ''; $conf = ''; $ev = ''; $byStatus = ''; $flags = ''; $secs = ''
    $covered = $false
    if ($jsonPath) {
      $covered = $true
      try {
        $j = Get-Content -LiteralPath $jsonPath -Raw -Encoding utf8 | ConvertFrom-Json
        $res = @($j.results)
        if ($res.Count -eq 1) { $status = $res[0].final_status; $conf = $res[0].install_confidence }
        elseif ($res.Count -gt 1) { $status = '容器展开' }
        else { $status = '(无结果项)' }
        if ($res.Count -ge 1) {
          $ids = @()
          foreach ($a in @($res[0].attempts)) { foreach ($e2 in @($a.install_evidence)) { if ($e2.id) { $ids += $e2.id } } }
          $ev = ($ids | Select-Object -Unique) -join '/'
        }
        $byStatus = (@($j.summary.by_status.PSObject.Properties | Where-Object { $_.Value -gt 0 } | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ')
        $flags = (@($j.summary.flags.PSObject.Properties | Where-Object { $_.Value -gt 0 } | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ')
        if ($j.started_at -and $j.finished_at) {
          try { $secs = [math]::Round((([datetime]$j.finished_at) - ([datetime]$j.started_at)).TotalSeconds, 1) } catch { }
        }
      } catch { $status = '(解析失败)' }
    } else { $status = '(未执行)' }
    $rows += [pscustomobject]@{
      分组 = $g.Name; 样本 = $rel; 类型 = $(if ($e.PSIsContainer) { '目录' } else { '文件' });
      最终状态 = $status; 置信度 = $conf; 证据 = $ev; 状态分布 = $byStatus; 标记 = $flags; 耗时秒 = $secs;
      覆盖 = $(if ($covered) { '是' } else { '否' })
    }
  }
}

$rows | Export-Csv -LiteralPath (Join-Path $OutDir 'per-sample.csv') -NoTypeInformation -Encoding UTF8

$byGroup = $rows | Group-Object 分组 | Sort-Object Name | ForEach-Object {
  $c = @($_.Group | Group-Object 最终状态 | ForEach-Object { "$($_.Name)=$($_.Count)" })
  [pscustomobject]@{ 分组 = $_.Name; 样本数 = $_.Count; 已覆盖 = @($_.Group | Where-Object { $_.覆盖 -eq '是' }).Count; 状态分布 = ($c -join ' ') }
}

$coveredRows = @($rows | Where-Object { $_.覆盖 -eq '是' })
$md = @()
$md += '# 合并汇总'
$md += ''
$md += "- 结果目录: $($RunDir -join ' ; ')"
$md += "- 枚举样本: $($rows.Count)（已覆盖 $($coveredRows.Count) / 未执行 $(@($rows | Where-Object { $_.覆盖 -eq '否' }).Count)）"
$md += ''
$md += '## 分组状态分布'
$md += ''
$md += '| 分组 | 样本数 | 已覆盖 | 状态分布 |'
$md += '|---|---|---|---|'
foreach ($g in $byGroup) { $md += "| $($g.分组) | $($g.样本数) | $($g.已覆盖) | $($g.状态分布) |" }
$md += ''
$md += '## 逐样本结果'
$md += ''
$md += '| 分组 | 样本 | 类型 | 最终状态 | 置信度 | 证据 | 耗时秒 | 覆盖 |'
$md += '|---|---|---|---|---|---|---|---|'
foreach ($r in $rows) { $md += "| $($r.分组) | $($r.样本) | $($r.类型) | $($r.最终状态) | $($r.置信度) | $($r.证据) | $($r.耗时秒) | $($r.覆盖) |" }
$md | Out-File -LiteralPath (Join-Path $OutDir 'summary.md') -Encoding utf8
Write-Output ("per-sample.csv: " + $rows.Count + " rows, covered=" + $coveredRows.Count)
