﻿# AutoTrigger-TestSuite

面向 [AutoTrigger](https://github.com/pengchengyin/AutoTrigger)（Windows 任意文件自动安装/触发工具）的**可复现测试套件**。

一句话：这里有一套**现成的分类样本 + 源码 + 脚本 + 实测结果**，用来回答一个问题——
**AutoTrigger 对各种各样的文件，到底支持到什么程度、哪些支持、哪些不支持。**

> 本套件只记录实际跑出来的结果；缺失信息一律标注「未提供」，不猜测、不补造。

---

## 一、被测工具与测试环境

| 项 | 值 |
|---|---|
| 工具 | AutoTrigger.exe |
| 构建 | 10,967,552 B / SHA-256 `11DCDB933BC3EA4A4440140E256B02B08AFD95407A80E383568CE69B7CF42727` |
| 版本 | tool_version **0.1.0**，结果 schema **2.8**，resource pack **0.1.0** |
| 操作系统 | Windows 11 专业版 build 26300，**96 DPI（100%）**，中文 |
| 权限 | **管理员会话** |
| 前置 | 7-Zip 26.03（ok）、PaddleOCR-json（ok）、GUI 自动化开启 |

> ⚠️ 跑本套件会**真实安装软件**：写 Program Files、写注册表卸载项、起进程、**移动鼠标键盘**。
> 请务必用**一次性虚拟机或可回滚快照**，不要在日常办公电脑跑。

---

## 二、工具效果总览（20 组 / 149 个输入样本）

**结论先行：**

- ✅ **静默/标准安装支持**：MSI、NSIS、WiX Burn、Inno Setup 的静默安装都能装上。
- ✅ **需要点击向导的安装器**：本轮桌面可交互，Inno / NSIS 的中英文向导、3010 需重启、完成页卡住类样本都能走完并取到安装证据。
- ✅ **压缩包、脚本、文档、伪装文件、ISO、黑名单、自绘界面**：按设计正确处理。
- ⚠️ **安装成功判定**：受「文件系统快照不完整」影响，部分已经落盘/写卸载项的样本仍只判 `install_unverified`（见问题文档 ISSUE-08 / ISSUE-11）。
- ⚠️ **超时与活动感知**：部分支持，个别样本状态判定仍有偏差。

| 状态 | 数量 |
|---|---|
| ✅ 安装成功 `install_completed` | 55 |
| 🔶 部分 `install_partial` | 10 |
| ❔ 未验证 `install_unverified` | 9 |
| ❌ 失败 `failed` | 22 |
| ⏱ 超时 `killed_on_timeout` | 9 |
| ▶ 已触发 `triggered` | 9 |
| ⏭ 跳过 `skipped` | 13 |
| 📦 容器展开（目录/压缩包输入） | 22 |

> 口径：**只有拿到安装证据（卸载项 / 落盘 / MSI 11707 / 安装器日志等）才算「安装成功」**；
> 退出码为 0、窗口关闭、流程结束，都**不算**。
>
> **全样本分母** = 149 − 跳过 13 − 容器展开 22 = **114**，安装成功 **55/114 = 48.2%**。
> 这个分母里包含大量**本来就不该安装成功**的样本（损坏包、加密包、压缩炸弹、伪装 / 非 Windows 可执行、
> 文档、脚本触发、黑名单陷阱、负向判定与超时样本、容器展开），所以 **48.2% 不代表安装器成功率**。
>
> **排除上述样本后**，只统计「样本清单期望 `install_completed` 的非容器安装器样本」（共 **56** 个）：
> 实际拿到安装证据 **46 个 → ✅ 46/56 = 82.1%**。**这是本套件的安装成功率参考值。**
>
> ⚠️ **反向标记（预期不应成功、却判成功）**：
> - 真·假成功 3 个：`INNO-06-假成功`（预期 `install_unverified`）、`A29-07-反证据-装后回滚`（预期 `install_partial`）、`INNO-10-联网下载组件等待`（预期 `killed_on_timeout`）；
> - 另有 6 个非安装器样本（`11-原生导出表(7z).dll`、`实际是PE的docx.docx` / `实际是PE的jpg.jpg` / `实际是PE的txt.txt`、`09-未知扩展名但MZ头.qwerty`、`无扩展名文件`）凭「执行 / 落盘」证据被判 `install_completed`，属判定口径偏松，**不计入安装器成功率**。

---

## 三、哪些支持、哪些不支持（按分组逐一看）

| 分组 | 样本数 | 预期效果 | 结论 | 说明 |
|---|---|---|---|---|
| 01-Inno Setup（真实） | 5 | 5 个安装器均 `install_completed`/high | ✅ 支持 | 本轮 2/5：WinMerge / Git 成功；ShareX 部分（N2）；audacity / Notepad3 交互超时 |
| 02-NSIS（真实） | 5 | 5 个安装器均 `install_completed`/high | ✅ 支持 | 本轮 5/5：npp / Everything / Defraggler / Recuva / Firefox（UPX + 中文向导）全部 high |
| 03-MSI | 6 | 6 个 MSI 均 `install_completed`/high | ✅ 支持 | 本轮 5/6：7z / KeePassXC / node / putty / TortoiseGit 成功；MobaXterm 1603（已存 MSI 详细日志） |
| 04-WiX Burn | 3 | 3 个 bootstrapper 均 `install_completed` | ✅ 支持 | 本轮 3/3：python / VC_redist / windowsdesktop-runtime 全部成功 |
| 05-其它厂商安装器 | 3 | 3 个安装器均 `install_completed` | ⚠️ 部分 | 本轮 1/3：Zoom 成功；TeraCopy（N6）/ VeraCrypt 部分 |
| 06-压缩包 | 7 | 解压并触发内层；便携包按落盘判成功 | ✅ 支持 | 6 个容器正常展开 + 内层触发；7z2600-x64-32bit.exe 成功 |
| 07-脚本与快捷方式 | 15 | 脚本按类型触发；指向安装器的 .lnk 应 `install_completed` | ✅ 支持 | bat/cmd/ps1/wsf/com/scr/lnk 正常；VBS/JS 判 `no_activity` |
| 08-文档类 | 8 | 有宿主→打开并 `triggered`；无宿主→`skipped: no_host_app` | ✅ 符合预期 | 有宿主打开；无宿主跳过；无宿主扩展名 `.atdoc` 判 failed（ISSUE-35） |
| 09-类型识别与伪装 | 13 | 按真实内容识别：伪装 PE 执行、ELF/Mach-O 跳过、非法 MSI failed | ✅ 支持 | 伪装成 docx/jpg/txt 的 PE 被执行；ELF/Mach-O 跳过；OLE 伪 msi 判 partial（ISSUE-09） |
| 10-入口分层与黑名单 | 6 | 命中 P0/P1 入口并安装；黑名单全程不执行 | ✅ 支持 | 选中正确入口；A25-01 复跑 VIOLATION = 0 |
| 11-安装成功判定 | 13 | A29-03/04/05/09/10/11b 应 `install_completed`；反证据样本应 partial/failed | ⚠️ 部分 | 本轮 3/6 应安装样本完成；其余多判 `install_unverified`（受快照不完整影响） |
| 12-超时与活动感知 | 9 | A30-01/04 应 `install_completed`；A30-02 应 `failed: no_activity`；其余 timeout | ⚠️ 部分 | A30-01/04 完成；6 个超时；A30-02 未判 `no_activity`（ISSUE-27） |
| 13-光盘映像 ISO | 10 | 介质分类正确 + OS/影音盘安全跳过；安装介质触发内层 | ✅ 支持 | OS 安装盘/影音光盘安全跳过；两处介质分类相反（ISSUE-32） |
| 14-跳过与兜底 | 12 | 空文件 `skipped`；损坏/加密/炸弹结构化失败且不落盘 | ✅ 符合预期 | 空文件跳过；损坏/加密/炸弹安全失败且不落盘 |
| 15-批量与嵌套 | 2 | 三层嵌套触达最内层；50 文件 `total=50` | ✅ 支持 | 三层嵌套与 50 文件均展开处理；total 仍含子项（ISSUE-31） |
| 16-自绘界面-OCR专项 | 2 | 自绘向导靠模板/OCR 走完并 `install_completed` | ✅ 支持 | 浅色走 template + OCR 完成；深色超时（已取到 A2） |
| 17-合成安装器(Inno) | 11 | 8 个应 `install_completed`；INNO-06 应 unverified、INNO-07 应 partial、INNO-10 应 timeout | ✅ 支持 | 本轮 8/8 应安装样本完成；但 INNO-06/10 判成功（假成功，见第二节标记） |
| 18-合成安装器(NSIS) | 7 | 6 个应 `install_completed`；NSIS-05 应 partial | ✅ 支持 | 本轮 6/6；NSIS-05 部分（识别到回滚 N4） |
| 19-合成安装器(MSI-WiX) | 9 | 6 个应 `install_completed`；MSI-02 应 partial；MSI-07/08 应 failed | ✅ 支持 | 本轮 6/6；MSI-02 部分（1603 + MSI 详细日志）；无效/损坏 MSI 正确失败 |
| 20-静默参数探测 | 3 | 2 个命中静默参数即成功；记录桩应 failed | ✅ 支持 | 按顺序探测，成功后立即停止 |

> 上表「预期效果」列即第二节「应安装样本」口径；期望 `install_completed` 的非容器安装器样本共 **56** 个，本轮实际完成 **46** 个（**82.1%**）。

### 三句话总结

1. **支持**：静默/标准安装器（Inno / NSIS / MSI / Burn）、需要点击向导的中英文安装器、压缩包、脚本与快捷方式、文档、伪装文件、黑名单、ISO、自绘界面（模板 + OCR）。
2. **部分支持**：安装成功判定受「文件系统快照不完整」影响（A29 组多为 `install_unverified`）；超时与活动感知个别样本判错；ISO 介质分类两处与清单相反。
3. **本轮已修复**：非 MSI 返回 3010、黑名单误杀、升级误判回滚、完成页卡住、自绘 OCR/模板回退、证据路径归因、包内 readme 挂起——详见 [reports/issues/README.md](reports/issues/README.md)。

---

## 四、样本构成

| 类别 | 分组 | 数量 | 随仓库分发 |
|---|---|---|---|
| 真实软件（厂商签名已核验） | 01–06 | 约 692 MB | ❌ 仅登记官方地址 + SHA-256 |
| 自制合成安装器 | 17–20 | 27 个 | ✅ |
| 自制行为样本 | 07–16 | 120 个 | ✅ |

- 自制样本清单：[manifests/samples.selfmade.json](manifests/samples.selfmade.json)
- 第三方清单：[manifests/samples.thirdparty.json](manifests/samples.thirdparty.json)
- 逐样本结果：[reports/per-sample.csv](reports/per-sample.csv)
- 可编译源码：[sources/BUILD.md](sources/BUILD.md)

---

## 五、快速开始

### 5.1 校验样本完整性

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-SampleManifest.ps1
# 期望输出: 结果: 一致 146 / 不一致 0 / 缺失 1
```

### 5.2 快速冒烟（推荐先跑，秒级）

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-SmokeTest.ps1 -AutoTrigger C:\path\to\AutoTrigger.exe
```

> 运行前请把 `AutoTrigger.exe` 加入杀软排除，否则可能中途被隔离（详见 [docs/environment.md](docs/environment.md) 第八节）。

### 5.3 逐样本批量测试（全部 20 组）

```powershell
# 建议在「管理员身份启动的 PowerShell」里运行，并保持桌面可交互、不锁屏、不休眠
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-SampleTest.ps1 -AutoTrigger C:\path\to\AutoTrigger.exe -TimeoutSec 240
```
结果按时间戳归档到 `runs\<时间戳>\`，每个样本产出结果 JSON、日志、控制台输出三件套。

### 5.4 跑完清理

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command 'Start-Process powershell -Verb RunAs -ArgumentList ''-NoProfile'',''-ExecutionPolicy'',''Bypass'',''-File'',''.\scripts\Cleanup-SyntheticSamples.ps1'''
```

只清理 `ATSynthetic*` / `ATSynth*` / `ATPackage*` / `ATArch*` / `ATF13*` / `ATOwnerDraw` 前缀对象与
`HK[LM|CU]\Software\AT-TestSuite`、`C:\Users\Public\AT-SENTINEL`，不动其它软件。

---

## 六、已知问题

共 **36 条**问题文档：[reports/issues/](reports/issues/)。
按本轮（当前桌面构建 / 管理员 / 交互桌面）逐条核对关闭判据后的结论：
**已关闭 8 条、疑似已修复或部分 6 条、仍存在 19 条、未复测 3 条。**
汇总（含每条问题的**关闭判据**与当前结论）见 **[reports/issues/README.md](reports/issues/README.md)**。

每次重跑后，只需按该表逐条核对判据，并把状态更新进去即可。

---

## 七、目录结构

```text
AutoTrigger-TestSuite\
├─ README.md                 本文件（套件是什么 + 工具效果）
├─ samples\                  分类样本（20 组）
├─ sources\                  自制样本源码 + BUILD.md
├─ scripts\                  冒烟 / 批量测试 / 结果合并 / 清单校验 / 第三方获取 / 清理
├─ manifests\                自制与第三方样本清单、工具链、SHA-256
├─ reports\                  汇总报告、逐样本 CSV、36 份问题文档 + 追踪表
├─ evidence\                 脱敏后的结果 JSON / 日志
└─ docs\                      测试方法、环境要求、结果判读、FAQ
```

关键入口：[reports/summary.md](reports/summary.md) · [reports/per-sample.csv](reports/per-sample.csv) ·
[reports/issues/README.md](reports/issues/README.md) · [docs/interpreting-results.md](docs/interpreting-results.md) ·
[docs/environment.md](docs/environment.md)

> 每次测试后，更新第二节的数字与第三节的结论；新问题追加到 `reports/issues/` 并在追踪表中登记。


