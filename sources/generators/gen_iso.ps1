# 用 Windows 自带 IMAPI2FS 把 sources\iso\trees\* 打包成 ISO（无需第三方工具）
# 并生成 .lnk 快捷方式样本。全部为 UTF-8 with BOM 保存（见 sources/fix_bom.py）。
$ErrorActionPreference = 'Stop'
$Root = if ($env:ATS_ROOT) { $env:ATS_ROOT } else { Split-Path (Split-Path $PSScriptRoot -Parent) -Parent }
$Trees  = Join-Path $Root 'sources\iso\trees'
$OutDir = Join-Path $Root 'samples\13-光盘映像 ISO'
$ProgressPreference = 'SilentlyContinue'
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;

public static class IsoHelper {
    public static void SaveStream(object comStream, string path) {
        IStream s = (IStream)comStream;
        using (FileStream fs = File.Create(path)) {
            byte[] buf = new byte[1 << 16];
            IntPtr readPtr = Marshal.AllocHGlobal(sizeof(int));
            try {
                while (true) {
                    s.Read(buf, buf.Length, readPtr);
                    int n = Marshal.ReadInt32(readPtr);
                    if (n <= 0) break;
                    fs.Write(buf, 0, n);
                }
            } finally {
                Marshal.FreeHGlobal(readPtr);
            }
        }
    }
}
'@ -ErrorAction Stop

function Write-IStreamToFile($iStream, $filePath) {
    # PowerShell 5.1 无法将 __ComObject 直接转成 IStream，故用 C# 助手落盘。
    [IsoHelper]::SaveStream($iStream, $filePath)
}

function New-Iso($srcDir, $isoPath, $volumeName, $udfOnly) {
    $fsi = New-Object -ComObject IMAPI2FS.MsftFileSystemImage
    # FsiFileSystemISO9660=1, Joliet=2, UDF=4
    if ($udfOnly) { $fsi.FileSystemsToCreate = 4 } else { $fsi.FileSystemsToCreate = 7 }
    $fsi.VolumeName = $volumeName
    $fsi.FreeMediaBlocks = 0
    $fsi.Root.AddTree($srcDir, $false)
    $img = $fsi.CreateResultImage()
    Write-IStreamToFile $img.ImageStream $isoPath
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($img)
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($fsi)
}

function New-Lnk($lnkPath, $target, $args, $workdir, $desc) {
    $dir = Split-Path $lnkPath -Parent
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $sh = New-Object -ComObject WScript.Shell
    $sc = $sh.CreateShortcut($lnkPath)
    $sc.TargetPath = $target
    if ($args)    { $sc.Arguments = $args }
    if ($workdir) { $sc.WorkingDirectory = $workdir }
    else          { $sc.WorkingDirectory = $dir }
    if ($desc)    { $sc.Description = $desc }
    $sc.Save()
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($sh)
}

Write-Host '===== 1. 生成 ISO ====='
$names = Get-ChildItem $Trees -Directory | Sort-Object Name
foreach ($d in $names) {
    $iso = Join-Path $OutDir ($d.Name + '.iso')
    try {
        New-Iso $d.FullName $iso $d.Name $false
        Write-Host ("[OK]   {0,-30} {1,8:N1} KB" -f $d.Name, ((Get-Item $iso).Length / 1KB))
    } catch {
        Write-Host ("[FAIL] {0} -> {1}" -f $d.Name, $_.Exception.Message)
    }
}

Write-Host '===== 2. UDF-only 映像（A27 非标准/挂载轨用）====='
$udfSrc = Join-Path $Trees 'A26-01-installer_media'
try {
    New-Iso $udfSrc (Join-Path $OutDir 'A27-09-UDF-only.iso') 'UDFONLY' $true
    Write-Host ("[OK]   A27-09-UDF-only.iso  {0:N1} KB" -f ((Get-Item (Join-Path $OutDir 'A27-09-UDF-only.iso')).Length / 1KB))
} catch { Write-Host ("[FAIL] UDF-only -> {0}" -f $_.Exception.Message) }

Write-Host '===== 3. 截断/损坏映像（两轨均失败路径）====='
$good = Join-Path $OutDir 'A26-05-data_disc.iso'
if (Test-Path $good) {
    $bytes = [IO.File]::ReadAllBytes($good)
    [IO.File]::WriteAllBytes((Join-Path $OutDir 'A27-10-截断损坏.iso'), $bytes[0..([int]($bytes.Length * 0.35))])
    Write-Host ("[OK]   A27-10-截断损坏.iso")
}

Write-Host '===== 4. .lnk 快捷方式样本 ====='
$exe = Join-Path $Root 'samples\11-安装成功判定\A29-03-标准安装-落盘+卸载项.exe'
$pdf = Join-Path $Root 'samples\08-文档类\01-有效文档.pdf'
New-Lnk (Join-Path $Root 'samples\07-脚本与快捷方式\09-快捷方式-指向安装器.lnk') $exe '' '' 'AT 测试：指向安装器的快捷方式'
New-Lnk (Join-Path $Root 'samples\07-脚本与快捷方式\10-快捷方式-指向不存在目标.lnk') 'C:\AT-NotExist\ghost-installer.exe' '/S' 'C:\AT-NotExist' 'AT 测试：目标不存在'
New-Lnk (Join-Path $Root 'samples\07-脚本与快捷方式\11-快捷方式-指向文档.lnk') $pdf '' '' 'AT 测试：指向文档（走关联程序）'
Write-Host '[OK]   3 个 .lnk'

# malware_lure：同目录创建 -> 保留相对路径，解压后仍可解析到兄弟载荷
$lureDir = Join-Path $Trees 'A26-02-malware_lure'
New-Lnk (Join-Path $lureDir '发票明细.lnk') (Join-Path $lureDir 'payload.exe') '' $lureDir 'AT 测试：恶意投递型快捷方式'
New-Lnk (Join-Path $lureDir '订货单.lnk') (Join-Path $lureDir '发票明细.exe') '' $lureDir 'AT 测试：第二个投递快捷方式'
Write-Host '[OK]   malware_lure 内的 .lnk 已生成，重新打包该 ISO'
try {
    New-Iso $lureDir (Join-Path $OutDir 'A26-02-malware_lure.iso') 'A26-02-malware_lure' $false
    Write-Host ("[OK]   A26-02-malware_lure.iso 重打包完成 {0:N1} KB" -f ((Get-Item (Join-Path $OutDir 'A26-02-malware_lure.iso')).Length / 1KB))
} catch { Write-Host ("[FAIL] 重打包 malware_lure -> {0}" -f $_.Exception.Message) }

Write-Host ''
Write-Host '===== ISO 样本清单 ====='
Get-ChildItem $OutDir -Filter *.iso | Sort-Object Name |
    Select-Object Name, @{n='KB';e={[math]::Round($_.Length/1KB,1)}} | Format-Table -AutoSize | Out-String | Write-Host
