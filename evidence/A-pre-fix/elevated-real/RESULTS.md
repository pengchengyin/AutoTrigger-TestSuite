# 真实软件安装效果（已提权，01–06 组）

> 会话：\Start-Process -Verb RunAs\ 启动的高完整性进程（\administrator: true\）。
> 目的：直接测量"AutoTrigger 能把多少真实软件装上"。

## 0. 结论

| 组 | 结果 | 通过率 |
|---|---|---|
| 01 真实 Inno Setup | 4 装成 / 1 部分成功（Notepad3） | 4/5 |
| 02 真实 NSIS | **5/5 全部 \install_completed\** | 5/5 |
| 03 真实 MSI | 5 装成 / 1 失败（MobaXterm，样本缺文件） | 5/6 |
| 04 WiX Burn | 2 装成 / 1 部分成功（VC_redist，升级误判） | 2/3 |
| 05 其它厂商安装器 | 2 装成 / 1 部分成功（VeraCrypt，GUI 触顶） | 2/3 |
| 06 压缩包 | **进程崩溃，结果全丢**（见 ISSUE-20） | 崩溃 |

**真实安装器合计：18 / 22 判为 \install_completed\（约 82%）**，
其中 NSIS 类 100% 通过（包括刻意保留的难点样本 \Firefox-Setup-zh-CN.exe\，UPX 压缩 + 中文 GUI 向导）。

> 提权是前提：同样的样本在**未提权**会话下，NSIS 7/7 全部无法启动（ISSUE-01）。

## 1. 逐条对照

### 01 真实 Inno Setup

| 样本 | 期望 | 实测 | 置信度 | 耗时 | 判定 | 备注 |
|---|---|---|---|---|---|---|
| WinMerge-2.16.46-x64-Setup.exe | install_completed | **install_completed** | high | 40s | ✅ |  |
| Notepad3-Setup.exe | install_completed | **install_partial** | low | 291s | ❌ | 走完向导被硬超时截断 |
| ShareX-17.0.0-setup.exe | install_completed | **install_completed** | high | 305s | ✅ | terminated on timeout; installation evidence still collected |
| audacity-win-3.7.1-64bit.exe | install_completed | **install_completed** | high | 10s | ✅ |  |
| Git-2.47.1-64-bit.exe | install_completed | **install_completed** | high | 92s | ✅ |  |

### 02 真实 NSIS

| 样本 | 期望 | 实测 | 置信度 | 耗时 | 判定 | 备注 |
|---|---|---|---|---|---|---|
| Everything-1.4.1.1026.x64-Setup.exe | install_completed | **install_completed** | high | 6s | ✅ |  |
| npp.8.8.1.Installer.x64.exe | install_completed | **install_completed** | high | 21s | ✅ |  |
| Firefox-Setup-zh-CN.exe | install_completed | **install_completed** | high | 69s | ✅ |  |
| Defraggler.exe | install_completed | **install_completed** | high | 15s | ✅ |  |
| Recuva.exe | install_completed | **install_completed** | high | 24s | ✅ |  |

### 03 真实 MSI

| 样本 | 期望 | 实测 | 置信度 | 耗时 | 判定 | 备注 |
|---|---|---|---|---|---|---|
| MobaXterm_installer_26.5.msi | install_completed | **install_partial** | low | 270s | ❌ | 样本缺 .dat（Error 1308） |
| putty-64bit-0.85-installer.msi | install_completed | **install_completed** | high | 11s | ✅ |  |
| 7z2600-x64.msi | install_completed | **install_completed** | medium | 7s | ✅ | 无 S2 落盘证据 |
| KeePassXC-2.7.9-Win64.msi | install_completed | **install_completed** | high | 6s | ✅ |  |
| node-v22.11.0-x64.msi | install_completed | **install_completed** | high | 45s | ✅ |  |
| TortoiseGit-2.17.0.0-64bit.msi | install_completed | **install_completed** | high | 20s | ✅ |  |

### 04 WiX Burn bootstrapper

| 样本 | 期望 | 实测 | 置信度 | 耗时 | 判定 | 备注 |
|---|---|---|---|---|---|---|
| VC_redist.x64.exe | install_completed | **install_partial** | low | 307s | ❌ | 升级被误判 N4 |
| python-3.13.0-amd64.exe | install_completed | **install_completed** | high | 178s | ✅ |  |
| windowsdesktop-runtime-8.0-win-x64.exe | install_completed | **install_completed** | high | 37s | ✅ |  |

### 05 其它厂商安装器

| 样本 | 期望 | 实测 | 置信度 | 耗时 | 判定 | 备注 |
|---|---|---|---|---|---|---|
| ZoomInstallerFull.exe | install_completed | **install_completed** | high | 73s | ✅ |  |
| TeraCopy.exe | install_completed | **install_completed** | high | 302s | ✅ | terminated on timeout; installation evidence still collected |
| VeraCrypt.exe | install_completed | **install_partial** | low | 300s | ❌ | 重复点确定触顶 |

## 2. 未通过项的归属

| 样本 | 归属 | 问题 |
|---|---|---|
| \Notepad3-Setup.exe\ | **工具** | 已走完 GUI 向导并取得 S1+S2，却被硬超时判 partial → [ISSUE-16](../../../reports/issues/ISSUE-16-走完GUI向导仍被硬超时判partial.md) |
| \VC_redist.x64.exe\ | **工具** | 正常升级（旧 VC++2019 条目被 VC++2022 取代）被误判为回滚 N4 → [ISSUE-17](../../../reports/issues/ISSUE-17-升级式安装被误判为回滚N4.md) |
| \VeraCrypt.exe\ | **工具** | 10 次点击全打在同一个 \确定\ 上，触顶后空转到超时 → [ISSUE-19](../../../reports/issues/ISSUE-19-重复点击同一控件触顶后空转到超时.md) |
| \MobaXterm_installer_26.5.msi\ | **样本** | MSI 缺外部数据文件 \MobaXterm_installer.dat\（Error 1308），必然失败 → [ISSUE-18](../../../reports/issues/ISSUE-18-样本不完整MobaXterm缺dat且错误未提炼.md) |
| \ShareX\ / \TeraCopy\ | **工具（不影响结论）** | 装成功但被拉起的应用窗口拖到硬超时 → [ISSUE-15](../../../reports/issues/ISSUE-15-安装后拉起的应用窗口被持续自动化至硬超时.md) |
| \06-压缩包\ | **工具** | Go 回调表耗尽崩溃，1613 条结果全丢 → [ISSUE-20](../../../reports/issues/ISSUE-20-Go回调表耗尽导致致命崩溃.md) |

## 3. 复现命令

\\\powershell
$Exe = "<DESKTOP>\AutoTrigger.exe"
$S   = "<SUITE_ROOT>\samples"
# 需要先取得高完整性会话（本机 ConsentPromptBehaviorAdmin=0，不会弹窗）
& $Exe --input "$S\02-NSIS" --output ".\02.json" --timeout 300 --log-level debug --no-lock
\\\

## 4. 产生的实际副作用（请注意）

本次测试**真实安装**了以下软件（如需卸载请自行在"应用和功能"中处理）：

- 组 01：WinMerge、ShareX、Audacity、Git for Windows（Notepad3 部分）
- 组 02：Notepad++、Everything、Firefox、Defraggler、Recuva
- 组 03：7-Zip 26.00、PuTTY、KeePassXC、Node.js 22、TortoiseGit
- 组 04：Python 3.13、Windows Desktop Runtime 8.0、VC++ 2022 运行库（VC_redist）
- 组 05：Zoom、TeraCopy（VeraCrypt 未装成）

合成样本（17/18/19 组）另装到 \C:\Program Files\ATSynth*\。
