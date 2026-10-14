# 清理所有「合成样本」在系统中留下的痕迹（本文件源自测试集原始 _cleanup.ps1，未改动清理范围）
# 清理所有「合成样本」在系统中留下的痕迹（安装目录 / 注册表卸载项 / 哨兵日志）。
# 只清理本测试集专用的 ATSynth* / ATPackage* / ATArch* / ATF13* / AT* 前缀对象，不动其它软件。
# 用法: powershell -NoProfile -ExecutionPolicy Bypass -File _cleanup.ps1 [-WhatIf]
param([switch]$WhatIf)

$ErrorActionPreference = 'Continue'
$Sentinel = 'C:\Users\Public\AT-SENTINEL'

$dirs = @(
    "$env:ProgramFiles\ATSynthetic App A29-03", "$env:ProgramFiles\ATSynthetic Rollback",
    "$env:ProgramFiles\ATSynthetic Upgrade A29-09", "$env:ProgramFiles\ATSynthetic Idempotent A29-10",
    "$env:ProgramFiles\ATSlowInstaller A30-01", "$env:ProgramFiles\ATStallInstaller A30-03",
    "$env:ProgramFiles\ATDonePageA30", "$env:ProgramFiles\ATVeryLongA30",
    "$env:ProgramFiles\ATPackageA2501", "$env:ProgramFiles\ATArchA2503",
    "$env:ProgramFiles\ATF13Stub", "$env:ProgramFiles\ATOwnerDraw",
    "${env:ProgramFiles(x86)}\ATSynthInno01", "${env:ProgramFiles(x86)}\ATSynthInno02",
    "${env:ProgramFiles(x86)}\ATSynthInno03", "${env:ProgramFiles(x86)}\ATSynthInno07",
    "${env:ProgramFiles(x86)}\ATSynthInno08", "${env:ProgramFiles(x86)}\ATSynthInno09",
    "${env:ProgramFiles(x86)}\ATSynthInno10", "${env:ProgramFiles(x86)}\ATSynthInno11",
    "$env:ProgramFiles\ATSynthInno01", "$env:ProgramFiles\ATSynthInno02", "$env:ProgramFiles\ATSynthInno03",
    "$env:ProgramFiles\ATSynthInno07", "$env:ProgramFiles\ATSynthInno08", "$env:ProgramFiles\ATSynthInno09",
    "$env:ProgramFiles\ATSynthInno10", "$env:ProgramFiles\ATSynthInno11",
    "$env:ProgramFiles\ATSynthNsis01", "$env:ProgramFiles\ATSynthNsis02", "$env:ProgramFiles\ATSynthNsis03",
    "$env:ProgramFiles\ATSynthNsis04", "$env:ProgramFiles\ATSynthNsis05", "$env:ProgramFiles\ATSynthNsis06",
    "$env:ProgramFiles\ATSynthNsis07",
    "$env:ProgramFiles\ATSynthMsi01", "$env:ProgramFiles\ATSynthMsi02", "$env:ProgramFiles\ATSynthMsi03",
    "$env:ProgramFiles\ATSynthMsi05", "$env:ProgramFiles\ATSynthMsi06",
    "$env:LOCALAPPDATA\ATSyntheticPerUser", "$env:LOCALAPPDATA\ATPortableA29",
    "$env:LOCALAPPDATA\ATRollbackA29", "$env:LOCALAPPDATA\ATSynthInno04", "$env:LOCALAPPDATA\ATSynthMsi04",
    "$env:ProgramData\ATSyntheticLoosA29", "$env:ProgramData\ATLooseSideEffectA29", "$env:ProgramData\ATF13Nsis",
    'C:\ATOutOfScope',
    "$env:TEMP\ATSynthInno06", "$env:TEMP\A29_bootstrap_payload",
    "$env:TEMP\A30-03-progress", "$env:TEMP\A30-09-long"
)

Write-Host '===== 1. 删除安装目录 ====='
foreach ($d in $dirs) {
    if (Test-Path -LiteralPath $d) {
        if ($WhatIf) { Write-Host "[试运行] 将删除目录 $d" }
        else { Remove-Item -LiteralPath $d -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "[删除] $d" }
    }
}

Write-Host '===== 2. 删除注册表卸载项 ====='
$roots = @('HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
           'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
           'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall')
$patterns = @('ATSynthetic*', 'ATSynth*', 'ATPackage*', 'ATArch*', 'ATF13*', 'ATOwnerDraw', 'ATSynthMsi*')
foreach ($r in $roots) {
    if (-not (Test-Path $r)) { continue }
    foreach ($p in $patterns) {
        Get-ChildItem -Path $r -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -like $p } | ForEach-Object {
            if ($WhatIf) { Write-Host "[试运行] 将删除注册表项 $($_.PSPath)" }
            else { Remove-Item -Path $_.PSPath -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "[删除] $($_.PSPath)" }
        }
    }
}
# AT-TestSuite 自身写下的标记键
foreach ($k in @('HKCU:\Software\AT-TestSuite', 'HKLM:\Software\AT-TestSuite')) {
    if (Test-Path $k) {
        if ($WhatIf) { Write-Host "[试运行] 将删除 $k" }
        else { Remove-Item -Path $k -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "[删除] $k" }
    }
}

Write-Host '===== 3. 删除哨兵目录 ====='
if (Test-Path $Sentinel) {
    if ($WhatIf) { Write-Host "[试运行] 将删除 $Sentinel" }
    else { Remove-Item -LiteralPath $Sentinel -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "[删除] $Sentinel" }
} else { Write-Host '[无] 哨兵目录不存在' }

Write-Host '===== 4. 清理被测试过程改动的残留（挂载的 ISO / 临时目录）====='
Get-Volume -ErrorAction SilentlyContinue | Where-Object { $_.DriveType -eq 'CD-ROM' -and $_.DriveLetter } | ForEach-Object {
    Write-Host "[提示] 检测到仍挂载的光盘映像，盘符 $($_.DriveLetter):（F18.3 要求任务收尾必须卸载；手动卸载用 Dismount-DiskImage）"
}
Get-ChildItem 'C:\AT' -ErrorAction SilentlyContinue | ForEach-Object {
    if ($WhatIf) { Write-Host "[试运行] 将删除 $($_.FullName)" }
    else { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "[删除] $($_.FullName)" }
}

Write-Host ''
Write-Host '清理完成。注意：本脚本不会卸载你下载的「真实软件样本」被安装后的痕迹——如需彻底还原请用快照/虚拟机。'
