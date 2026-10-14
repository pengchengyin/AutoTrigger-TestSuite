# 自制样本的构建说明

> 本目录保存 **全部自制样本的源码与生成脚本**。
> 真实第三方安装包（`samples\01-06\`）**不在本仓库**，见 `manifests/samples.thirdparty.json`。

## 一、根目录约定

所有脚本通过环境变量 `ATS_ROOT` 定位仓库根目录；未设置时按脚本位置推断。
构建命令统一用 `-D` / `/D` 传入绝对路径：

```powershell
$Root = (Get-Location).Path          # 仓库根目录（含 samples\ sources\）
$Root
```

## 二、工具链（不随仓库分发）

| 工具 | 用途 | 官方来源 |
|---|---|---|
| Inno Setup 6.7.1 | 编译 `sources\innosetup\*` | https://jrsoftware.org/isdl.php |
| NSIS 3.13 | 编译 `sources\nsis\*` | https://nsis.sourceforge.io/Download |
| WiX Toolset 3.14 | 编译 `sources\wix\*` | https://github.com/wixtoolset/wix3/releases |
| .NET Framework 4 `csc.exe` | 编译 C# 合成样本（Windows 自带） | 系统内置 `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe` |
| 7-Zip 26.03 | 压缩包处理（运行套件需要） | https://www.7-zip.org/ |
| PaddleOCR-json 1.4.1 | OCR（可选，自绘样本需要） | 见 AutoTrigger 主项目说明 |

◆ 版本号取自原始制作环境记录（`manifests/toolchain.json`）；**实际请以官方最新稳定版为准**。

## 三、已实测可复现的构建（2026-10-13 本机验证）

### 3.1 Inno Setup（11 个）

```powershell
& "<ISCC>" /Qp /DATS_ROOT=$Root "$Root\sources\innosetup\INNO-01-静默安装成功.iss"
```

- ✅ 实测 **INNO-01 编译成功**，产物写入 `$Root\samples\17-合成安装器(Inno)\`
- 脚本内用 `{#ATS_ROOT}` 引用根目录；`.iss` 为 **UTF-8 with BOM**（不要改成无 BOM）

### 3.2 NSIS（7 个）

```powershell
& "<makensis>" /DATS_ROOT=$Root "$Root\sources\nsis\NSIS-01-静默安装成功.nsi"
```

- ✅ 实测 **NSIS-01 编译成功**，产物 **248,040 字节**，与仓库内样本**大小完全一致**
- 脚本内用 `${ATS_ROOT}`；`.nsi` **必须保留 UTF-8 BOM**，否则 makensis 按 ANSI 读取会导致中文乱码/报错

### 3.3 WiX（7 个 MSI）

```powershell
$B = $Root
& "<candle.exe>" -nologo -dATS_ROOT=$B -out "$B\_out\MSI-01.wixobj" "$Root\sources\wix\MSI-01-标准安装成功.wxs"
& "<light.exe>"  -nologo -ext WixUIExtension -sice:ICE80 -out "$B\_out\MSI-01-标准安装成功.msi" "$B\_out\MSI-01.wixobj"
```

- ✅ 实测 **7/7 全部编译成功**，大小与仓库内样本一致：
  `MSI-01/02/03/04/06V1/06V2 = 450,560` 字节；`MSI-05 = 933,888` 字节
- 必须加 `-ext WixUIExtension`（否则报 `WixUI:WixUI_Minimal` 未解析）
- 建议加 `-sice:ICE80`：组件是 32 位而目录取自 `ProgramFiles64Folder`，会触发 ICE80 噪声告警（不影响产物）

#### ⚠️ MSI-05 需要额外的载荷文件

`sources\payload\` 中**没有** `bigpayload.bin`（原制作环境用后未保留）。要让 MSI-05 可编译，先生成同尺寸占位文件：

```powershell
$p = "$Root\sources\payload\bigpayload.bin"
if (-not (Test-Path $p)) { fsutil file createnew $p 268435456 }   # 256 MB
```

- ✅ 实测：生成后 MSI-05 编译产出 **933,888 字节**，与仓库内样本一致
- ⚠️ 占位内容（全零）与原始文件**不保证逐字节相同**，仅保证体积与可编译性

### 3.4 C# 合成样本（`sources\csharp\`，45 个源文件）

```powershell
python "$Root\sources\generators\gen_csharp.py"       # 需要 ATS_ROOT
```

- 编译用系统自带 `csc.exe`，**无需额外安装**
- ⚠️ **未实测**：本次发布流程**没有重新运行**该生成器（会重写 `samples\` 下的自制样本）。
  脚本只做了**路径参数化与脱敏**，未做端到端复现验证。

### 3.5 ISO 映像（`sources\iso\`，10 个）

```powershell
python "$Root\sources\generators\gen_iso_trees.py"
powershell -NoProfile -ExecutionPolicy Bypass -File "$Root\sources\generators\gen_iso.ps1"
```

- 用 Windows 自带 `IMAPI2FS` 打包，无需第三方工具
- ⚠️ **未实测**：同上，只做路径参数化与脱敏，未重新打包验证。

## 四、目录对照（原 `_build\` → 本仓库）

| 原路径 | 本仓库路径 |
|---|---|
| `_build\cs\` | `sources\csharp\` |
| `_build\*\*.iss` | `sources\innosetup\` |
| `_build\*\*.nsi` | `sources\nsis\` |
| `_build\wix\*\*.wxs` | `sources\wix\`（去掉 `.wixobj`） |
| `_build\payload\` | `sources\payload\` |
| `_build\isotrees\` | `sources\iso\trees\` |
| `_build\*\*.py / *.ps1` | `sources\generators\` |
| `_build\sample-index.json` | `manifests\sample-index.json` |

## 五、脱敏与改动记录

对发布副本做了以下**非功能性**改动（原始目录未改动）：

| 改动 | 范围 | 说明 |
|---|---|---|
| 绝对路径宏化 | 11 `.iss` + 7 `.nsi` + 7 `.wxs` | `C:\Users\<用户名>\...\` → `{#ATS_ROOT}` / `${ATS_ROOT}` / `$(var.ATS_ROOT)` |
| 根路径参数化 | 9 个生成脚本 | 改为读环境变量 `ATS_ROOT`，回退到脚本相对位置 |
| `_build\` → `sources\` | 全部生成/构建脚本 | 适配本仓库目录结构 |
| 用户名/机器名 | — | 本目录内**无残留**（已核查） |
| BOM 保持 | 全部 `.iss\/.nsi\` | 与原始文件一致保留 UTF-8 BOM |

## 六、未验证项（如实标注）

| 项 | 状态 |
|---|---|
| Inno / NSIS / WiX 编译 | ✅ 已实测（含产物大小比对） |
| C# 生成器端到端重跑 | ❌ 未实测 |
| ISO 打包重跑 | ❌ 未实测 |
