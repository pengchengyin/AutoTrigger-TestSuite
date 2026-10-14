# 解包 Chocolatey nupkg，并静默解压 Inno Setup / NSIS / WiX 到 _toolchain
$ErrorActionPreference = 'Continue'
$Root = if ($env:ATS_ROOT) { $env:ATS_ROOT } else { Split-Path (Split-Path $PSScriptRoot -Parent) -Parent }
$TC   = Join-Path $Root '_toolchain'
$Choco= Join-Path $TC 'choco'
$ProgressPreference = 'SilentlyContinue'

function Unzip($zip, $dest) {
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $dest)
}

Write-Host "===== 1. 解包 nupkg ====="
foreach ($pkg in 'innosetup', 'nsis') {
    $nupkg = Join-Path $Choco "$pkg.nupkg"
    if (-not (Test-Path $nupkg)) { Write-Host "[SKIP] missing $nupkg"; continue }
    $out = Join-Path $Choco $pkg
    if (-not (Test-Path $out)) {
        Write-Host "[..] extracting $pkg.nupkg"
        Unzip $nupkg $out
    }
    Get-ChildItem -Path $out -Recurse -Include *.exe -ErrorAction SilentlyContinue |
        Select-Object -First 5 FullName | Out-String | Write-Host
}

Write-Host "===== 2. 静默解压 Inno Setup ====="
$innoSetup = Get-ChildItem -Path (Join-Path $Choco 'innosetup') -Recurse -Filter 'innosetup-*.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
if ($innoSetup) {
    $dest = Join-Path $TC 'innosetup'
    if (-not (Test-Path (Join-Path $dest 'ISCC.exe'))) {
        Write-Host "[..] extracting Inno Setup -> $dest"
        Start-Process -FilePath $innoSetup.FullName -Wait -ArgumentList @(
            '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-','/NOICONS',"/DIR=$dest"
        )
    }
    if (Test-Path (Join-Path $dest 'ISCC.exe')) { Write-Host "[OK] ISCC.exe ready" } else { Write-Host "[FAIL] Inno Setup not ready" }
} else { Write-Host "[FAIL] innosetup installer not found" }

Write-Host "===== 3. 静默解压 NSIS ====="
$nsisSetup = Get-ChildItem -Path (Join-Path $Choco 'nsis') -Recurse -Filter 'nsis-*-setup.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
if ($nsisSetup) {
    $dest = Join-Path $TC 'nsis'
    if (-not (Test-Path (Join-Path $dest 'makensis.exe'))) {
        Write-Host "[..] extracting NSIS -> $dest"
        Start-Process -FilePath $nsisSetup.FullName -Wait -ArgumentList "/S /D=$dest"
    }
    if (Test-Path (Join-Path $dest 'makensis.exe')) { Write-Host "[OK] makensis.exe ready" } else { Write-Host "[FAIL] NSIS not ready" }
} else { Write-Host "[FAIL] nsis installer not found" }

Write-Host "===== 4. 解 WiX v3 ====="
$wixZip = Join-Path $TC 'wix\wix314-binaries.zip'
if (Test-Path $wixZip) {
    $dest = Join-Path $TC 'wix314'
    if (-not (Test-Path (Join-Path $dest 'candle.exe'))) {
        Write-Host "[..] extracting WiX v3"
        Unzip $wixZip $dest
    }
    if (Test-Path (Join-Path $dest 'candle.exe')) { Write-Host "[OK] candle.exe / light.exe ready" }
}

Write-Host "`n===== 工具链状态 ====="
foreach ($f in @('innosetup\ISCC.exe','nsis\makensis.exe','wix314\candle.exe','wix314\light.exe','wix314\torch.exe','wix314\dark.exe')) {
    $p = Join-Path $TC $f
    if (Test-Path $p) { Write-Host ("[OK]   " + $p) } else { Write-Host ("[MISS] " + $p) }
}
