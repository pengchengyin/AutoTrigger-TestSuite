<#
.SYNOPSIS  比较两次运行的结果（例如修复前 vs 修复后）
.EXAMPLE   ... -Before .\evidence\A-pre-fix\...\x.json -After .\runs\2026...\summary.json
#>
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Before, [Parameter(Mandatory=$true)][string]$After)
$ErrorActionPreference = 'Stop'
function Load($p) {
  $j = Get-Content -LiteralPath $p -Raw -Encoding utf8 | ConvertFrom-Json
  $h = @{}
  foreach ($r in $j.results) { $h[(Split-Path $r.file_path -Leaf)] = $r.final_status }
  return $h
}
$a = Load $Before; $b = Load $After
$keys = @($a.Keys + $b.Keys | Sort-Object -Unique)
Write-Host "==== 结果对比 ====" -ForegroundColor Cyan
Write-Host ("  左(基准): $Before"); Write-Host ("  右(对比): $After"); Write-Host ""
$diff = 0
"{0,-46} {1,-22} {2,-22}" -f '样本','基准','对比' | Write-Host
foreach ($k in $keys) {
  $x = if ($a.ContainsKey($k)) { $a[$k] } else { '(无)' }
  $y = if ($b.ContainsKey($k)) { $b[$k] } else { '(无)' }
  if ($x -ne $y) { $diff++; "{0,-46} {1,-22} {2,-22}" -f $k,$x,$y | Write-Host -ForegroundColor Yellow }
}
Write-Host ""
Write-Host ("差异 $diff / 共 $($keys.Count) 个样本") -ForegroundColor $(if($diff -eq 0){'Green'}else{'Yellow'})
