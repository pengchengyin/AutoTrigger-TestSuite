# AutoTrigger-TestSuite

面向 [AutoTrigger](https://github.com/pengchengyin/AutoTrigger)（Windows 任意文件自动安装/触发工具）的**可复现测试套件**：
样本、源码、脚本、样本清单、逐样本结果、真实测试报告与已知问题。

> 本仓库的目的不是"证明工具很好"，而是**让任何人能在自己的机器上快速核对 AutoTrigger 的真实效果与边界**。
> 结论只按实际跑出来的结果写，缺失的信息一律标注「未提供」。

---

## 一、这是什么

| 项 | 说明 |
|---|---|
| 被测工具 | **AutoTrigger**（Windows 安装包自动处理工具） |
| 主机程序链接 | [pengchengyin/AutoTrigger](https://github.com/pengchengyin/AutoTrigger) — 本仓库仅链接，未修改主项目仓库 |
| 工具版本 | `0.1.0`（`tool_version`），结果 JSON schema `2.8`，resource pack `0.1.0` |
| 本套件内容 | 自制样本 240 个文件（14 组）+ 第三方样本登记 23 条（6 组，不随仓库分发） |
| 样本源码 | ✅ 全部自制样本源码在 `sources\`，Inno/NSIS/WiX 均已实测可重新编译 |
| 证据 | ✅ 逐样本结果 CSV、脱敏原始 JSON/日志、冒烟验证实录 |

---

## 二、最新测试结论摘要

◆ **请先读这句话：本套件从未在"同一工具版本 + 同一次运行"下跑完全部样本，因此不存在一个统一的成功率。**
下面按 **(工具构建, 权限)** 分段给出，各段**不可相加、不可互相比较**。

| 段 | 工具构建 | 权限 | 覆盖输入样本 | 状态分布 | 安装成功/分母 |
|---|---|---|---|---|---|
| A-修复前提权 | 10,038,272 B（2026-10-11） | 管理员 | 207 | 成功 72 / 部分 20 / 跳过 35 / 失败 32 / 已触发 36 / 超时 8 / 未验证 4 | **72/172 = 41.9%** |
| A-修复前未提权 | 同上 | 普通用户 | 32 | 部分 5 / 成功 3 / 跳过 3 / 失败 9 / 已触发 12 | **3/29 = 10.3%** |
| B-修复后定向复测 | 10,235,904 B（2026-10-12） | 管理员 | 8 | 成功 6 / 未验证 1 / 部分 1 | **6/8 = 75.0%** |
| D-当前分发版自制备样 | 7,758,848 B（2026-10-14） | 管理员 | 120 | 成功 34 / 失败 20 / 容器展开 16 / 跳过 12 / 未验证 10 / 超时 10 / 部分 9 / 已触发 9 | **34/92 = 37.0%**（合成安装器专项 21/27 = **77.8%**） |

**口径**：分母 = 覆盖的输入样本数 − `skipped`。
`install_unverified` / `install_partial` / `triggered` / `killed_on_timeout` / `failed` **都不计入**"安装成功"。
容器展开出的子项（3403 条）**已全部排除**，避免重复统计。

> - **A-修复前未提权**那段只覆盖 07/09 两组，作用是**证明"未提权时装不上需要管理员的软件"**，
>   **不代表**工具在未提权下的整体能力。
> - **B-修复后**只跑了 6 项修复对应的 8 个定向样本，属**验证子集**，**不能当全套件成功率**。
> - **D-当前分发版**用逐样本方式跑完 **自制备样 07–20 全部 120 个**（第三方仅抽测 4 个），
>   合成安装器专项 **21/27 = 77.8%**、黑名单 VIOLATION = 0，完整偏差见 [reports/run-2026-10-14.md](reports/run-2026-10-14.md)。
> - 详细口径与证据索引见 **[reports/README.md](reports/README.md)** 与 **[reports/summary.md](reports/summary.md)**。

### 状态口径（务必区分）

| 状态 | 含义 | 计入"安装成功"？ |
|---|---|---|
| `install_completed` | 取得安装证据（卸载项/落盘/MSI 11707 等） | ✅ |
| `install_unverified` | 仅有退出码 0 之类的弱证据 | ❌ |
| `install_partial` | 同时存在成功与失败反证据 | ❌ |
| `already_installed` | 装前已存在 | ❌ |
| `triggered` | 只被触发，未确认安装 | ❌ |
| `killed_on_timeout` / `failed` | 超时 / 失败 | ❌ |
| `skipped` | 未执行（空文件/无宿主/命中黑名单） | ❌（且排除出分母） |

◆ **退出码为 0、安装器窗口关闭、流程正常结束，都不等于安装成功。**

---

## 三、测试环境（如实记录）

| 项 | 值 |
|---|---|
| 测试日期 | 2026-10-11 ～ 2026-10-14 |
| 操作系统 | Windows 11 专业版 10.0.26300（build 26300） |
| 屏幕 / DPI | 1718x1038 / **96 DPI（100%）** |
| PowerShell | 5.1.26100.9444 |
| 权限 | 两段：**管理员会话** 与 **普通用户会话**（见上表） |
| 7-Zip | ✅ 可用（`archive_backend_status=ok`） |
| OCR | PaddleOCR-json，**状态不稳定**：多次运行中 `ocr_engine_status` 在 `ok` 与 `startup_failed` 间摆动 |
| GUI 自动化 | `gui_automation=true` |
| 内置模板 | `builtin_templates=false`；**模板索引内容未提供**（本机未找到可发布内容） |
| 提交/commit | **未提供** — 测试基于分发的二进制，未记录源码提交号 |
| 截图 | **未提供** — 证据中截图数量为 0 |

> ⚠️ **此测试会在被跑机器上真实安装软件**：写注册表卸载项、写 Program Files、起进程、动鼠标键盘。
> 请务必用**一次性虚拟机或可回滚快照**，**不要在日常办公电脑跑全套件**。

---

## 四、样本构成

| 类别 | 数量 | 随仓库分发 | 说明 |
|---|---|---|---|
| 自制合成样本（组 07–20） | 240 个文件 / 14 组 | ✅ | 含 Inno/NSIS/MSI 合成安装器、脚本、伪装、ISO、黑名单陷阱等 |
| 真实第三方安装包（组 01–06） | 23 个 | ❌ | 仅登记官方地址 + SHA-256；**6 组共 692 MB 不代发** |

- 自制样本清单：**[manifests/samples.selfmade.json](manifests/samples.selfmade.json)**（147 条索引，146 条在盘，SHA-256 全部已核对）
- 第三方清单：**[manifests/samples.thirdparty.json](manifests/samples.thirdparty.json)**（23 条，**8 条官方下载地址未提供**）
- 逐样本结果：**[reports/per-sample.csv](reports/per-sample.csv)**
- 可编译源码：**[sources/BUILD.md](sources/BUILD.md)**

---

## 五、主要已知问题与未验证场景

### 5.1 已确认修复并复测（2026-10-12 构建）

| 项 | 结论 |
|---|---|
| 回调耗尽崩溃（`too many callback functions`） | ✅ 通过 — 6-压缩包整组 1621 条结果、38 分钟正常收尾 |
| 黑名单误杀（卸载项/升级覆盖被跳过） | ✅ 通过（含负向对照：真实 `unins000.exe` / `update.exe` 仍被拦截） |
| 回滚证据被清空 | ✅ 通过 — 后续正常退出不再清除已有反证据 |
| 截断快照误判（A29 组） | ✅ 通过 — 快照不完整时不再产生文件差异证据 |
| 截断快照误判（A30 组） | ⚠️ 部分 — 仍残留无路径的 `A3` 证据 |
| 升级误判回滚（VC_redist） | ⚠️ 部分验证 — 本机旧版本已被消耗，无法复现真正的替换升级 |
| 证据路径诊断 | ✅ 通过 — `S2/N5/N6` 带实际目录与增减数量 |

### 5.2 仍存在（未复测修复）

**35 份问题文档**位于 **[reports/issues/](reports/issues/)**。
第一轮（修复前）严重度分布：**致命 3、高 16、中 11、低 4、说明 1**。
除上表 7 项外，其余问题的状态均为 **「仍存在（未复测修复）」**。

### 5.3 未验证场景

| 场景 | 状态 |
|---|---|
| 全部 20 组在同一版本下完整跑完 | ❌ 从未做过 |
| `already_installed` 幂等判定 | ❌ 未复测 |
| OCR 专项（16-自绘界面） | ⚠️ 受 OCR 启动不稳定影响 |
| 远程/SSH 环境下运行 | ⚠️ GUI 向导类样本在 SSH 下 `gui_actions=0`，**不可用**；静默类可用 |
| 组 01–06 中 8 个样本 | ❌ 官方来源未提供，未纳入可复现范围 |

---

## 六、快速开始

### 6.1 准备

> 📦 若你是从 **GitHub Release** 下载的打包版（`AutoTrigger-TestSuite-v*.zip`）：
> **组 01–06 的第三方样本已随包提供**（共 30 个文件 / 约 692 MB），解压后可直接跳到 [6.2](#62-校验样本完整性)，**无需**下面的 clone 与下载步骤。

```powershell
git clone https://github.com/pengchengyin/AutoTrigger-TestSuite.git AutoTrigger-TestSuite
cd AutoTrigger-TestSuite
```

必需：Windows 10/11、PowerShell 5.1、**7-Zip**、AutoTrigger.exe。
可选：PaddleOCR-json（自绘界面样本）。

第三方样本不在 Git 仓库内，如需完整覆盖请先获取：

```powershell
# 只下载清单中登记了官方直链的条目；未登记来源的会明确列出
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-ThirdPartySamples.ps1
```

### 6.2 校验样本完整性

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-SampleManifest.ps1
# 期望输出: 结果: 一致 146 / 不一致 0 / 缺失 1（缺的是索引中的历史条目）
```

### 6.3 快速冒烟验证（推荐先跑这个）

```powershell
# 默认 quick：3 个自制样本，秒级，无副作用
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-SmokeTest.ps1 -AutoTrigger C:\path\to\AutoTrigger.exe
```

脚本会：检查工具/7-Zip/OCR/权限/交互式桌面/样本完整性 → 列出样本与副作用 → **等你确认** →
逐样本输出到 `runs\<时间戳>\`（不覆盖历史）→ 生成本轮 `summary.md` 并列出**预期 vs 实际**差异。

| Profile | 内容 | 需要管理员 |
|---|---|---|
| `quick`（默认） | 3 个跳过/失败判定样本，秒级 | 否 |
| `standard` | 追加 ZIP 伪装、Inno/NSIS 合成安装器 | 部分需要 |
| `blacklist` | A25-01 黑名单陷阱包（验证 11 个陷阱**未被执行**） | 否 |

> 需要无人值守时用 `-Unattended`，**不会**默认跳过安全确认。

### 6.4 样本级批量测试（自制备样 120 个）

推荐用逐样本方式跑全套件（结果按时间戳目录归档，不覆盖历史）：

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-SampleTest.ps1 -AutoTrigger C:\path\to\AutoTrigger.exe -TimeoutSec 120
# 中途退出后可多次续跑，再用合并脚本汇总
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Summarize-Run.ps1 -RunDir .\runs\<时间戳1>,.\runs\<时间戳2> -OutDir .\runs\_merged
~~~

2026-10-14 实测（当前分发版 **7,758,848 B**，管理员会话，逐样本，超时 120 s）：
**自制备样 120/120 全部覆盖**，合成安装器专项 **21/27 = 77.8%**，黑名单 **VIOLATION = 0**。
完整结论与偏差见 **[reports/run-2026-10-14.md](reports/run-2026-10-14.md)**。

### 6.5 本次冒烟验证的实际结果（2026-10-14）

| 样本 | 预期 | 实际 | 耗时 |
|---|---|---|---|
| 14-跳过与兜底/01-空文件.exe | skipped | ✅ skipped | 4.8 s |
| 14-跳过与兜底/02-空文件.dat | skipped | ✅ skipped | 7.5 s |
| 14-跳过与兜底/03-单字节文件.bin | failed | ✅ failed | 3.8 s |

退出码 0，全部符合预期。原始结果见 **[evidence/smoke-2026-10-14/](evidence/smoke-2026-10-14/)**。

### 6.6 跑完后清理

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','.\scripts\Cleanup-SyntheticSamples.ps1'"
```

只清理 `ATSynthetic*` / `ATSynth*` / `ATPackage*` / `ATArch*` / `ATF13*` / `ATOwnerDraw` 前缀对象与 `HK[LM|CU]\Software\AT-TestSuite`、`C:\Users\Public\AT-SENTINEL`，**不动其它软件**。

---

## 七、目录结构

```text
AutoTrigger-TestSuite\
├─ README.md                  ← 本文件
├─ LICENSE                    MIT（仅覆盖本仓库自制内容）
├─ THIRD_PARTY_NOTICES.md     第三方软件/工具链许可与获取方式
├─ samples\                   自制样本（14 组 / 240 文件）
├─ sources\                   自制样本源码 + BUILD.md（含实测构建命令）
├─ scripts\                   冒烟验证 / 样本级批量测试 / 结果合并 / 清单校验 / 第三方获取 / 结果对比 / 清理
├─ manifests\                 自制与第三方样本清单、工具链、SHA-256、索引
├─ reports\                   汇总报告、逐样本 CSV、35 份问题文档、历史报告
├─ evidence\                  脱敏后的 JSON / 日志 + 脱敏映射表
└─ docs\                      测试方法、环境要求、结果判读、FAQ、整理清单
```

关键入口：
[reports/summary.md](reports/summary.md) ·
[reports/run-2026-10-14.md](reports/run-2026-10-14.md) ·
[reports/per-sample.csv](reports/per-sample.csv) ·
[reports/issues/](reports/issues/) ·
[reports/coverage.md](reports/coverage.md) ·
[docs/interpreting-results.md](docs/interpreting-results.md) ·
[docs/environment.md](docs/environment.md) ·
[manifests/samples.thirdparty.json](manifests/samples.thirdparty.json)

---

## 八、许可与隐私

- 本仓库**自制内容**（样本、源码、脚本、文档）采用 MIT，见 [LICENSE](LICENSE)。
- **第三方安装包不随仓库分发**（体积 + 再分发许可逐项不同），仅登记官方地址与 SHA-256，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
- 编译器（Inno/NSIS/WiX）同样不随仓库分发。
- 所有证据副本已**脱敏**（用户名、机器名、邮箱、Windows SID、绝对路径），规则与逐文件记录见 [evidence/SANITIZATION.csv](evidence/SANITIZATION.csv)。

## 九、如何引用/反馈

- 发现样本或结论有误：请带上 `runs\<时间戳>\` 下的结果 JSON 与日志提 issue。
- 需要引用本套件结论：请**同时说明工具构建、权限、分母口径**，不要摘取单一百分比。

> 本仓库由测试者整理；**未包含**对 AutoTrigger 主项目的任何修改。
