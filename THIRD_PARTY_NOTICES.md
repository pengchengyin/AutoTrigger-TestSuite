# 第三方软件与许可声明

本仓库**不代发任何第三方安装包或编译器**，只登记其官方获取方式与校验值。
所有第三方软件的权利归其各自所有者，使用时请遵守对应许可。

## 一、被测试的第三方安装包（samples\01-06，不随仓库分发）

共 23 个。清单见 [manifests/samples.thirdparty.json](manifests/samples.thirdparty.json)，
含名称、版本、大小、SHA-256 与官方下载地址。

| 厂商 | 样本 |
|---|---|
| Git for Windows | Git-2.47.1-64-bit.exe |
| Mozilla | Firefox-Setup-zh-CN.exe |
| Rizonesoft | Notepad3-Setup.exe |
| ShareX Team | ShareX-17.0.0-setup.exe |
| WinMerge | WinMerge-2.16.46-x64-Setup.exe |
| Audacity | audacity-win-3.7.1-64bit.exe |
| Notepad++ | npp.8.8.1.Installer.x64.exe / npp.8.8.1.portable.x64.zip |
| voidtools | Everything-1.4.1.1026.x64-Setup.exe |
| 7-Zip / Igor Pavlov | 7z2600-x64.msi / 7z2501-extra.7z / 7z2600-x64-32bit.exe |
| Simon Tatham | putty-64bit-0.85-installer.msi / putty-0.85-w64.zip |
| OpenJS Foundation | node-v22.11.0-x64.msi |
| TortoiseGit | TortoiseGit-2.17.0.0-64bit.msi |
| KeePassXC | KeePassXC-2.7.9-Win64.msi |
| Microsoft | python-3.13.0-amd64.exe（PSF 许可）/ VC_redist.x64.exe / windowsdesktop-runtime-8.0-win-x64.exe |
| NSSM | nssm-2.24.zip |
| Piriform / CCleaner | Defraggler.exe / Recuva.exe |
| Mobatek | MobaXterm_Installer.zip / MobaXterm_installer_26.5.msi |
| Code Sector | TeraCopy.exe |
| IDRIX | VeraCrypt.exe |
| Zoom Video Communications | ZoomInstallerFull.exe |

### ⚠️ 再分发许可提示

这些软件的再分发条款**逐项不同**，其中若干为**专有 EULA，明确限制再分发**（如 Zoom、MobaXterm、
TeraCopy、Defraggler、Recuva、VeraCrypt）。因此本仓库的策略是：

1. **不收录二进制**，只登记官方下载地址 + 精确版本 + SHA-256；
2. **8 个样本的官方直链未登记**（原始下载脚本未记录来源），清单中标记为
   `"官方下载地址未提供（原始下载脚本未登记，请自行从厂商官网获取）"`，**不猜测、不补造**。

◆ 如果你要 fork 本仓库并想附带这些安装包，**请自行逐项确认许可**，风险自负。

## 二、构建自制样本所需的编译器（不随仓库分发）

见 [manifests/toolchain.json](manifests/toolchain.json)。

| 工具 | 版本（原始环境） | 许可 | 官方来源 |
|---|---|---|---|
| Inno Setup | 6.7.1 | Inno Setup License（允许免费使用与分发） | https://jrsoftware.org/isdl.php |
| NSIS | 3.13 | zlib/libpng-like | https://nsis.sourceforge.io/Download |
| WiX Toolset | 3.14 | MS-RL | https://github.com/wixtoolset/wix3/releases |
| 7-Zip | 26.03 | LGPL + unRAR 限制 | https://www.7-zip.org/ |
| PaddleOCR-json | 1.4.1 | Apache-2.0 | 见 AutoTrigger 主项目说明 |
| .NET Framework csc.exe | 系统自带 | 随 Windows | — |

## 三、自制样本中出现的第三方名称

自制样本（组 07–20）与黑名单陷阱（`samples\10\`、`sources\csharp\`）中，
**文件名**模仿了常见卸载/更新/调试程序（`uninstall.exe`、`unins000.exe`、`update.exe`、
`crashpad_handler.exe`、`卸载.exe` 等）。

这些**只是文件名**，实际是 3–4 KB 的惰性测试桩（源码在 `sources\csharp\`），
**不包含**任何第三方代码。列出仅为避免误解。

> 注意：这类文件名可能触发杀毒软件启发式告警。它们在仓库中的作用是
> **验证 AutoTrigger 的黑名单是否真的拦住了这些入口**（见 `scripts\Invoke-SmokeTest.ps1 -Profile blacklist`）。

## 四、证据中出现的第三方内容

`evidence\` 中的日志片段可能包含第三方安装器输出的文本（如 MSI 详细日志）。
这些内容仅用于测试留痕，**其权利归各自所有者**；如需引用请注明来源。
