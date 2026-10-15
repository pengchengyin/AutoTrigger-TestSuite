# AutoTrigger-TestSuite

面向 [AutoTrigger](https://github.com/pengchengyin/AutoTrigger)（Windows 任意文件自动安装/触发工具）的**可复现测试套件**。

一句话：这里有一套**现成的分类样本 + 源码 + 脚本 + 实测结果**，用来回答一个问题——
**AutoTrigger 对各种各样的文件，到底支持到什么程度、哪些支持、哪些不支持。**

> 本套件只记录实际跑出来的结果；缺失信息一律标注「未提供」，不猜测、不补造。

---

## 一、被测工具与测试环境

| 项 | 值 |
|---|---|
| 工具 | AutoTrigger.exe |
| 构建 | 7,758,848 B / SHA-256 `691373269CA840248939482479632C66933B830376C46DDF2BA2DA46206CB7FF` |
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
- ✅ **压缩包、脚本、文档、伪装文件、ISO、黑名单**：按设计正确处理。
- ⚠️ **需要点击向导的安装器**：本轮测试机的桌面不可交互（锁屏/前台窗口为空），**未能验证**，
  不能算作「不支持」，需在真正的交互桌面单独验证。
- ⚠️ **超时与活动感知**：部分支持，个别样本状态判定仍有偏差。

| 状态 | 数量 |
|---|---|
| ✅ 安装成功 `install_completed` | 43 |
| 🔶 部分 `install_partial` | 18 |
| ❌ 失败 `failed` | 20 |
| ⏱ 超时 `killed_on_timeout` | 17 |
| ❔ 未验证 `install_unverified` | 8 |
| ▶ 已触发 `triggered` | 9 |
| ⏭ 跳过 `skipped` | 12 |
| 📦 容器展开（目录/压缩包输入） | 22 |

> 口径：**只有拿到安装证据（卸载项 / 落盘 / MSI 11707 / 安装器日志等）才算「安装成功」**；
> 退出码为 0、窗口关闭、流程结束，都**不算**。
> 分母去掉「跳过」与「容器展开」后为 115，安装成功 **43/115 = 37.4%**；
> 但分母里包含大量**本来就不该安装**的样本（损坏包、伪装文件、文档、黑名单陷阱），所以这个百分比不代表安装器成功率。

---

## 三、哪些支持、哪些不支持（按分组逐一看）

| 分组 | 样本数 | 结论 | 说明 |
|---|---|---|---|
| 01-Inno Setup（真实） | 5 | ✅ 支持 | Git、WinMerge 安装成功；audacity / Notepad3 / ShareX 本轮桌面非交互，未验证 |
| 02-NSIS（真实） | 5 | ✅ 支持 | npp / Everything / Defraggler / Recuva / Firefox（UPX + 中文向导）全部成功 |
| 03-MSI | 6 | ✅ 支持 | 7z / KeePassXC / MobaXterm / node / putty / TortoiseGit 全部成功 |
| 04-WiX Burn | 3 | ✅ 支持 | python / VC_redist / windowsdesktop-runtime 全部成功 |
| 05-其它厂商安装器 | 3 | ⚠️ 未验证 | TeraCopy / VeraCrypt / Zoom 需要向导交互 |
| 06-压缩包 | 7 | ✅ 支持 | zip / 7z 解压并触发内层，含 1330+ 文件的 MobaXterm 包与嵌套包 |
| 07-脚本与快捷方式 | 15 | ✅ 支持 | bat / cmd / ps1 / wsf / com / scr / lnk 正常触发；VBS / JS 本轮未验证 |
| 08-文档类 | 8 | ✅ 符合预期 | 有宿主则打开并记录触发，无宿主则跳过 |
| 09-类型识别与伪装 | 13 | ✅ 支持 | 按**真实内容**识别：伪装成 docx/jpg/txt 的 PE 能被执行，ELF/Mach-O 被跳过 |
| 10-入口分层与黑名单 | 6 | ✅ 支持 | 选中正确入口；卸载/更新类陷阱**全程不执行**（VIOLATION = 0） |
| 11-安装成功判定 | 13 | ✅ 支持 | 分级判定（S1 卸载项 / S2 落盘 / S3 MSI 0 / A1 退出码）并识别反证据 |
| 12-超时与活动感知 | 9 | ⚠️ 部分 | 6 个按预期超时；「启动后无动作」未判 no_activity，个别状态有偏差 |
| 13-光盘映像 ISO | 10 | ✅ 支持 | OS 安装盘 / 影音光盘安全跳过；安装介质正常处理 |
| 14-跳过与兜底 | 12 | ✅ 符合预期 | 空文件跳过；损坏 / 加密 / 压缩炸弹安全失败且不落盘 |
| 15-批量与嵌套 | 2 | ✅ 支持 | 三层嵌套、50 文件批量 |
| 16-自绘界面-OCR专项 | 2 | ⚠️ 未验证 | 需要交互桌面 + OCR 引擎 |
| 17-合成安装器(Inno) | 11 | ✅ 静默 / ⚠️ GUI 未验证 | 静默安装成功；仅 GUI 向导类未验证 |
| 18-合成安装器(NSIS) | 7 | ✅ 静默 / ⚠️ GUI 未验证 | 静默安装成功；仅 GUI 向导类未验证 |
| 19-合成安装器(MSI-WiX) | 9 | ✅ 支持 | 标准 / per-user / 升级覆盖成功；无效、损坏 MSI 正确失败 |
| 20-静默参数探测 | 3 | ✅ 支持 | 按顺序探测静默参数，成功后立即停止后续尝试 |

### 三句话总结

1. **支持**：静默/标准安装器（Inno / NSIS / MSI / Burn）、压缩包、脚本与快捷方式、文档、伪装文件、黑名单、ISO。
2. **未验证**：需要「点向导」的安装器与自绘界面样本——本轮测试机桌面不可交互，需要在真实交互桌面复跑。
3. **部分支持**：超时与活动感知，个别样本的状态判定与预期不符（见问题文档）。

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
