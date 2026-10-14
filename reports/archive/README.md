# AutoTrigger 功能测试报告（安装效果专项）

> 用 `<SUITE_ROOT>` 样本集对 `AutoTrigger.exe` 做功能测试，目标是**尽可能多地自动安装各类软件**。
> 每个问题一份独立 md（问题描述 + 证据日志），便于逐个修复。

## 0. 一页速览

| 项 | 值 |
|---|---|
| 被测工具 | `<DESKTOP>\AutoTrigger.exe`（tool v0.1.0 / schema 2.8 / resource pack 0.1.0） |
| 样本集 | `<SUITE_ROOT>\samples`（20 组 / ~300 文件 / ~740 MB） |
| 环境 | Windows 10.0.26300 x64；账户 `<HOST>\<USER>` |
| 测试日期 | 2026-10-11 |
| 未提权证据 | `evidence\` |
| **已提权证据** | **`elevated\`（含 `RESULTS.md` 逐条比对）** |

**一句话结论**：**工具自身不提权是当前最大瓶颈**。未提权时所有需要管理员的安装器（合成 NSIS 全部 7 个、真实 Inno/NSIS/Burn）**一个都装不上**；而本机 UAC 策略是"静默提权"（`ConsentPromptBehaviorAdmin=0`，实测 `runas` 不弹窗即可拿到 `ELEVATED=True`），工具只要改用 `ShellExecuteEx(runas)` 就能无声解决——**提权后合成 NSIS 立刻从 0/7 变成 5 装成 + 2 符合预期的部分成功**。

## 1. 运行环境的关键事实

| 事实 | 取值 | 影响 |
|---|---|---|
| 进程完整性级别 | `Medium`（S-1-16-8192） | 无法创建高完整性子进程，`CreateProcess` 直接报 `requires elevation` |
| `BUILTIN\Administrators` | `Group used for deny only` | 账户是管理员，但令牌被过滤 |
| `EnableLUA` / `ConsentPromptBehaviorAdmin` | `1` / **`0`** | **提权不弹窗**，`runas` 可静默成功 |
| `AutoTrigger.exe` 清单 | 无 `requestedExecutionLevel` | 默认 `asInvoker`，双击不会提权 |
| 内置图像模板 | **`entries: []`（0 张）** | 模板匹配这条腿完全缺失 |
| OCR 引擎 | 时好时坏（`startup_failed` ↔ `ok`；`ocr_startup_ms` 观测到 0 / 1672 / 4454） | 同一环境自检结果不稳定 |
| 7-Zip | `third_party\7zip\7-Zip\7z.exe` v26.03，状态 `ok` | 正常 |

## 2. 问题总表

| # | 级别 | 标题 | 关键证据 |
|---|---|---|---|
| [ISSUE-01](../issues/ISSUE-01-未提权导致管理员安装器无法启动.md) | 🔴 致命 | 未提权 → `requireAdministrator` 安装器 9/9 次无法启动 | `evidence/18-NSIS-01.json` |
| [ISSUE-02](../issues/ISSUE-02-目标完整性级别更高时UIPI拦截点击且不快速失败.md) | 🔴 致命 | 目标窗口 IL 更高 → UIPI 拦截点击，却不快速失败，空耗 306 s | `evidence/01-Notepad3.log` |
| [ISSUE-03](../issues/ISSUE-03-黑名单误杀含卸载字样的合法安装器.md) | 🟠 高 | 黑名单子串匹配误杀 3 个合法安装器（"卸载项/无卸载项/升级覆盖"） | `evidence/07-group.log`、`elevated/17,19-group.json` |
| [ISSUE-04](../issues/ISSUE-04-内置图像模板为空导致GUI兜底缺失.md) | 🟠 高 | 内置图像模板为空（0 张），GUI 兜底缺失 | `--capabilities`、`--dump-resources` |
| [ISSUE-05](../issues/ISSUE-05-OCR引擎启动自检不稳定.md) | 🟠 高 | OCR 自检时好时坏，冷启动 18.9 s ≫ 10 s 超时 | `--capabilities` |
| [ISSUE-12](../issues/ISSUE-12-非MSI安装器返回3010被判失败.md) | 🟠 高 | 非 MSI 安装器静默返回 3010（成功+需重启）被判失败 | `elevated/18-group.json`、`elevated/18-group.log` |
| [ISSUE-06](../issues/ISSUE-06-MSI首次quiet返回1603且成功却只判medium.md) | 🟡 中 | MSI 首试 `/quiet` 必返 1603，靠 `/passive` 才装成 | `evidence/19-MSI-01.json` |
| [ISSUE-07](../issues/ISSUE-07-summary.by_status键名与final_status枚举不一致.md) | 🟡 中 | `summary.by_status` 键名与 `final_status` 枚举不一致 | `--capabilities` |
| [ISSUE-08](../issues/ISSUE-08-文件系统快照预算上限导致负向证据被禁用.md) | 🟡 中 | 快照触达预算上限 → 负向文件证据被静默禁用 | `evidence/07-group.log` |
| [ISSUE-09](../issues/ISSUE-09-非法MSI被判install_partial而非failed.md) | 🟡 中 | 非法/损坏 MSI 被判 `install_partial` 而非 `failed` | `evidence/09-group.json` |
| [ISSUE-10](../issues/ISSUE-10-document_host直接执行非可执行文档本体.md) | 🟡 中 | `document_host` 把文档本体当程序执行 | `evidence/09-group.json` |
| [ISSUE-11](../issues/ISSUE-11-合成载荷app.exe非有效PE致artifact_check失败.md) | 🟡 中 | 合成载荷 `app.exe` 非有效 PE → 置信度跌破清单预期 | `evidence/19-MSI-01.json` |
| [ISSUE-14](../issues/ISSUE-14-requires_network只在有窗口时才输出.md) | 🟡 中 | `requires_network` 只在抓到窗口时才输出；静默路径缺失 | `elevated/17-group.json` |
| [ISSUE-15](../issues/ISSUE-15-安装后拉起的应用窗口被持续自动化至硬超时.md) | 🟠 高 | 装完自动启动的应用窗口被当向导，持续自动化到硬超时（ShareX 305 s） | `elevated-real/01-group.log` |
| [ISSUE-16](../issues/ISSUE-16-走完GUI向导仍被硬超时判partial.md) | 🟠 高 | 已走完 GUI 向导并取得 S1+S2，却被硬超时判 `install_partial`（Notepad3） | `elevated-real/01-group.log` |
| [ISSUE-20](../issues/ISSUE-20-Go回调表耗尽导致致命崩溃.md) | 🔴 致命 | Go 回调表耗尽（too many callback functions）→ 06 组崩溃，1613 条结果全丢 | `elevated-real/06-group.console.txt` |
| [ISSUE-17](../issues/ISSUE-17-升级式安装被误判为回滚N4.md) | 🟠 高 | VC_redist 正常升级被误判为回滚（N4），成功后仍重试至 partial | `elevated-real/04-group.json` |
| [ISSUE-19](../issues/ISSUE-19-重复点击同一控件触顶后空转到超时.md) | 🟠 高 | 10 次点击全打在同一个 `确定`，触顶后空转到超时（VeraCrypt） | `elevated-real/05-group.log` |
| [ISSUE-18](../issues/ISSUE-18-样本不完整MobaXterm缺dat且错误未提炼.md) | 🟡 中 | MobaXterm MSI 缺 `.dat`（Error 1308）必然失败；错误未提炼进结果 | `elevated-real/03-group-msi-logs/` |
| [ISSUE-21](../issues/ISSUE-21-落盘证据无法归因且自相矛盾.md) | 🟠 高 | 落盘证据 S2/N5 无路径、可归因性缺失，且同次判定里 +N/−N 自相矛盾 | `elevated-arch/01-nssm-2.24.json` |
| [ISSUE-22](../issues/ISSUE-22-便携压缩包被当作安装器处理.md) | 🟡 中 | 便携压缩包被当安装器：CLI 工具套 9 种参数、常驻工具跑到超时 | `elevated-arch/06-putty-0.85-w64.json` |
| [ISSUE-23](../issues/ISSUE-23-阶段2暴力兜底未生效.md) | 🟠 高 | 阶段2暴力兜底（`fallback_to_brute`）未生效，深层 P5 入口未被枚举（A25-06） | `elevated-a25/04-A25-06-阶段2兜底.json` |
| [ISSUE-24](../issues/ISSUE-24-包内readme被document_host打开并挂到超时.md) | 🟡 中 | 包内 readme（.txt）被记事本打开并挂到 idle 超时（A25-02） | `elevated-a25/02-A25-02-readme指向不存在文件.json` |
| [ISSUE-26](../issues/ISSUE-26-二次调用未识别already_installed.md) | 🟠 高 | 二次调用未识别 `already_installed`，`pre_installed` 恒为 false（A29-10） | `elevated-a29/p2-A29-10-已安装检测-幂等.json` |
| [ISSUE-25](../issues/ISSUE-25-反证据N6被正向证据覆盖.md) | 🟠 高 | 反证据 N6（装后回滚）被忽略仍判 `install_completed`；纯 1603 判 partial | `elevated-a29/p1-07-A29-07-反证据-装后回滚.json` |
| [ISSUE-27](../issues/ISSUE-27-启动后无动作从未判定no_activity.md) | 🟠 高 | 「启动后无动作」从未判 `no_activity`，一路耗到硬超时（A30-02） | `elevated-a30/02b-A30-02-clean.json` |
| [ISSUE-29](../issues/ISSUE-29-活动感知超时状态系统性偏差.md) | 🟠 高 | 静止/等待/子进程脱离的终态系统性偏错；静止样本竟判 `install_completed` | `elevated-a30/03-A30-03-运行中静止.json` |
| [ISSUE-30](../issues/ISSUE-30-完成页卡住却判partial未取到安装证据.md) | 🟠 高 | 「完成页卡住」取不到 S1/S2 → 判 partial（与 INNO-09 矛盾） | `elevated-a30/04-A30-04-完成安装后卡在完成页.json` |
| [ISSUE-28](../issues/ISSUE-28-系统休眠期间计时照算.md) | ⚪ 低 | 系统休眠 7 小时被计入耗时（26118 s） | `elevated-a30/02-A30-02-启动后无动作.json` |
| [ISSUE-31](../issues/ISSUE-31-summary.total包含解压子项导致计数不符.md) | 🟡 中 | `summary.total` 混入解压子项：批量 50 文件得 `total=55` | `elevated-batch/15-batch50.json` |
| [ISSUE-32](../issues/ISSUE-32-ISO介质分类与清单不符.md) | 🟡 中 | ISO `media_kind` 2/10 与清单不符（A26-05 / A26-07） | `elevated-batch/13-05.json`、`13-07.json` |
| [ISSUE-33](../issues/ISSUE-33-自绘窗口OCR模板回退从未触发.md) | 🟠 高 | 自绘窗口 OCR/模板回退**从未触发**，`gui_actions=0`（16 组全失败） | `elevated-misc/16-01.json` |
| [ISSUE-34](../issues/ISSUE-34-解压失败缺少结构化错误码.md) | ⚪ 低 | 解压失败无结构化错误码（`extract_failed` 0 命中），与 zip 炸弹不一致 | `elevated-misc/14-04.json` |
| [ISSUE-35](../issues/ISSUE-35-无宿主扩展名被判failed而非skipped.md) | ⚪ 低 | 无宿主扩展名被判 `failed` 而非 `skipped: no_host_app`（.atdoc） | `elevated-doc/08-08.json` |
| [ISSUE-13](../issues/ISSUE-13-构建中间产物被当作样本处理污染统计.md) | ⚪ 低 | `.wixpdb` 构建产物被当样本，污染 failed 统计 | `elevated/19-group.json` |

> 级别定义：🔴 致命＝导致"装不上"或"大量空耗"；🟠 高＝显著降低可安装软件范围；🟡 中＝判定/契约/可诊断性偏差；⚪ 低＝统计与整洁性。

## 3. 已确认可用的能力（回归时不要碰坏）

- **MSI 链路**：`MSI-01/03/04/05` 均 `install_completed`，`MSI-03` 正确置 `requires_reboot=true`；`MSI-07/08`（非法/损坏）正确 `failed`；
- **MSI 失败日志**：`elevated\19-group-msi-logs\` 下 9 个 `.log` 非空，1603 有中文释义（A34 ① 通过）；
- **NSIS（提权后）**：`/S` 静默、中英文 MUI 向导、长安装不误杀，全部 `install_completed`；
- **Inno（提权后）**：静默、per-user(lowest)、中英文向导、无许可页向导、卡完成页（超时但证据齐全）；
- **GUI 自动化（提权后）**：`【界面】自动点击：安装(I)（识别来源 uia）` 稳定生效；
- **脚本触发**：`.bat/.cmd/.ps1/.vbs/.js/.wsf` 全部 `triggered`，哨兵 `SCRIPT-*` 齐全；
- **快捷方式解析**：`.lnk` → 真实目标解析与后续动作正常（除被黑名单误杀那条）。
- **静默参数探测（F13）** ✅：`elevated-f13/` 实测 9 次尝试顺序与 F13 参数表**逐条吻合**
  （Inno → NSIS → InstallShield → WiX → `/silent` → `--silent` → `--quiet` → `-s` → 无参数），
  且"任一尝试取得证据即提前结束"生效（`见VERYSILENT即成功` 只调用 1 次、`只认NSIS的S` 恰好 2 次）。
  详见 `elevated-f13/01..03-*-f13argv.log`。

## 4. 已提权复测结果（关键验证）

`Start-Process -Verb RunAs` 拉起高完整性会话，复测合成安装器 17/18/19 三组：

| 组 | 样本数 | 结果 | 说明 |
|---|---|---|---|
| 17 合成 Inno | 11 | 9 装成 / 1 部分 / 1 跳过 | 含中英文 GUI 向导、per-user、无许可页 |
| 18 合成 NSIS | 7 | 5 装成 / 2 部分 | **未提权时这 7 个是 0 成功** |
| 19 合成 MSI | 16 | 4 装成 / 7 失败 / 1 部分 / 4 跳过 | failed 里 5 个、skipped 里 4 个是"非样本/被误杀" |

**✅ 通过 22 条 / ❌ 不符 5 条 / ⚪ 非样本 7 条**，明细见 [elevated/RESULTS.md](elevated/RESULTS.md)。

## 4.5 真实软件安装效果（已提权，01–06 组）

同样在**高完整性会话**下跑真实软件样本，直接测量"能装多少"：

| 组 | 结果 | 通过率 |
|---|---|---|
| 01 真实 Inno Setup | 4 装成 / 1 部分成功（Notepad3） | 4/5 |
| 02 真实 NSIS | **5/5 全部 `install_completed`** | 5/5 |
| 03 真实 MSI | 5 装成 / 1 失败（MobaXterm，样本缺文件） | 5/6 |
| 04 WiX Burn | 2 装成 / 1 部分成功（VC_redist 升级误判） | 2/3 |
| 05 其它厂商安装器 | 2 装成 / 1 部分成功（VeraCrypt GUI 触顶） | 2/3 |
| 06 压缩包 | **进程崩溃，结果全丢**（ISSUE-20） | 崩溃 |

**真实安装器合计 18 / 22 判为 `install_completed`（约 82%）**，NSIS 类 100% 通过（含刻意保留的难点样本 `Firefox-Setup-zh-CN.exe`）。
明细与副作用清单见 [elevated-real/RESULTS.md](elevated-real/RESULTS.md)。

### 压缩包（06 组）逐包单跑

06 组整体跑因 ISSUE-20 崩溃，改为**每个压缩包单独一个进程**重跑：

| 结果 | 说明 |
|---|---|
| **8/8 正常结束、0 崩溃** | 反证 ISSUE-20 是累积性崩溃，而非某个压缩包有毒 |
| 嵌套递归 ✅ | `01-一层嵌套.7z` / `02-两层嵌套.zip` 都走到最内层并 `install_completed` |
| 包内安装器 ✅ | `MobaXterm_Installer.zip` 里的 MSI 装成（`high`），并证实 ISSUE-18 是样本缺 `.dat` |
| 便携工具集 ❌ | CLI 工具被套 9 种静默参数、常驻托盘工具跑到超时（ISSUE-22） |

明细见 [elevated-arch/RESULTS.md](elevated-arch/RESULTS.md)。

### A25 入口分层与黑名单（10 组逐个子样本）

| 子样本 | 结果 |
|---|---|
| A25-01 / A25-04 黑名单 | ✅ **`VIOLATION-*.txt = 0`**，`excluded=11`，铁证通过 |
| A25-03 架构优先 | ✅ 顺序为 `setup_x64 → install.bat → setup_x86`（x86 未抢先）；但装成后仍执行 x86 |
| A25-04 压缩包 | ✅ 解压前即产出 `entries=51 / excluded=11`（F17.1） |
| A25-06 阶段2兜底 | ❌ 未兜底，P5 唯一有效 PE 被完全漏掉（ISSUE-23） |
| A25-02 readme | ❌ `.txt` 被记事本打开、挂到 67.3 s 超时（ISSUE-24） |

明细见 [elevated-a25/RESULTS.md](elevated-a25/RESULTS.md)。

### 静默参数探测（20 组 / F13）✅

`elevated-f13/` 实测三次探测桩，**顺序与提前结束都完全正确**：
`记录全部尝试` 恰好 9 次且顺序为 Inno→NSIS→InstallShield→WiX→`/silent`→`--silent`→`--quiet`→`-s`→无参数；
`见VERYSILENT即成功` 只调用 1 次；`只认NSIS的S` 恰好 2 次。原始证据见 `elevated-f13/*-f13argv.log`。

### A29 安装成功判定（11 组逐个样本 + 幂等二次运行）

**13 个样本里只有 3 个完全符合清单预期**：

| 偏差类型 | 数量 | 代表 |
|---|---|---|
| ❌ 被**黑名单**直接跳过 | **4** | `A29-03` / `A29-04` / `A29-09` / `A29-11`（ISSUE-03） |
| ❌ 被 `artifact_check` 压低 | 1 | `A29-05`（ISSUE-11） |
| ❌ 反证据 / 噪音导致方向错误 | 4 | `A29-01` / `A29-07` / `A29-08` / `A29-12`（ISSUE-25 / ISSUE-21） |
| ❌ 幂等检测缺失 | 1 | `A29-10` 第 2 次未判 `already_installed`（ISSUE-26） |

> **结论**：A29 的偏差主要不来自判定算法，而来自**输入证据被污染**（ISSUE-21）与**候选样本被黑名单吃掉**（ISSUE-03）。
> 修这两个的性价比远高于调权重。

明细见 [elevated-a29/RESULTS.md](elevated-a29/RESULTS.md)。

### A30 超时与活动感知（12 组逐个样本）

**7 个样本只有 2 个符合预期**，但两个关键能力是好的：

| 结论 | 说明 |
|---|---|
| ✅ 慢安装器不误杀 | ~A30-01~ 总时长 92 s > idle 60 s，仍判 ~install_completed / high~ |
| ✅ 进程树清理生效 | ~A30-06~ 任务结束后 ~RESIDUAL_cmd_ping = 0~，终止走了 ~graceful→terminated→killed_tree~ |
| ✅ ~requires_network~ 可用 | ~A30-08~ 输出 ~{"requires_network":true}~ + ~killed_on_timeout~ |
| ❌ ~no_activity~ 从未判定 | ~A30-02~ 干净复现 206.4 s（应为 30 s 级）→ ISSUE-27 |
| ❌ 终态系统性偏错 | ~A30-03~ 静止却判 ~install_completed/high~；~05/06~ 被判 ~install_partial~ → ISSUE-29 |
| ❌ 完成页样本取不到证据 | ~A30-04~ 判 ~install_partial~（与 ~INNO-09~ 矛盾）→ ISSUE-30 |

明细见 [elevated-a30/RESULTS.md](elevated-a30/RESULTS.md)。

> ⚠️ 本轮机器真实休眠过一次（~Kernel-Power~ 事件 42），导致 ~A30-02~ 首次运行耗时 26118 s；
> 相关结论均已用**干净复现**替换（见 ISSUE-28）。

### 批量（15 组）与光盘映像（13 组）

| 项 | 结果 |
|---|---|
| 批量 ~A6-批量50文件~ | ~sum(by_status)==total~ ✅；但 **~total=55~ ≠ 50 输入** ❌（ISSUE-31）；耗时 433 s |
| 三层嵌套 ~01-三层嵌套.7z~ | ✅ ~level4-installer.exe -> install_completed/high~（F6 深度 3 递归正确） |
| ISO 安全断言 | ✅ ~A26-03-os_install_media~ / ~A26-04-media_disc~ **零执行** |
| ISO 入口选择 | ✅ 01~08 全部符合（含 ~.lnk~ 最高优先、乱码名、8 层深目录、autorun 失效回落） |
| ISO 双轨 | ✅ ~A27-09~ 走 ~extract~；~A27-10~ 两轨失败且**不阻塞** |
| ISO 介质分类 | ❌ ~A26-05~ / ~A26-07~ 的 ~media_kind~ 与清单不符（ISSUE-32） |

明细见 [elevated-batch/RESULTS.md](elevated-batch/RESULTS.md)。
> 本轮加了防休眠守卫（~SetThreadExecutionState~），避免上一轮的睡眠冻结问题。

### 自绘 OCR（16 组）与 跳过/兜底（14 组）

| 项 | 结果 |
|---|---|
| 16 自绘向导（浅色/深色） | ❌ 两个都是 `install_partial/low` + **`gui_actions=0`**；OCR 一次没调用 → ISSUE-33 |
| 14 空文件/单字节 | ✅ `skipped: empty_file` / `failed: untriggerable` |
| 14 损坏/截断/加密压缩包 | ✅ 均失败且**不阻塞后续**；但错误码不结构化 → ISSUE-34 |
| 14 未知扩展名 MZ 头 | ✅ 按 PE 执行 → `install_completed` |
| **14 zip 炸弹（2.15 GB）** | ✅✅ **`extract_size_exceeded`，磁盘只变化 0.1 MB、1.1 s 拦下** |

明细见 [elevated-misc/RESULTS.md](elevated-misc/RESULTS.md)。

### 文档类（08 组）与长样本（A30-07/09）

| 项 | 结果 |
|---|---|
| 08 PDF（有宿主） | ✅ `triggered`，`platform_meta.host_program = msedge.exe` |
| 08 Office 类（无宿主） | ✅ `skipped: no_host_app`（本机确无 Office 关联，属环境正确） |
| 08 `.atdoc`（无宿主，未知扩展名） | ❌ 判 `failed` 而非 `skipped: no_host_app` → ISSUE-35 |
| **A30-07（700 s 长安装）** | ✅✅ 在 **599.5 s**（墙钟 604.9 s）终止，`term=graceful`，`install_completed` + notes 正确 |
| A30-09（只在 TEMP 写盘） | ❌ 应 `killed_on_timeout`，因误报 `S2` 被抬成 `install_partial` → ISSUE-29/21 |

明细见 [elevated-doc/RESULTS.md](elevated-doc/RESULTS.md)。

## 5. 目录结构

~~~
AutoTrigger测试报告\
├─ README.md                本文件（总索引）
├─ issues\                  35 份问题文档（问题 + 复现 + 证据 + 修复建议）
├─ evidence\                未提权会话的原始证据（JSON / debug 日志 / 控制台）
├─ elevated\                          合成安装器 17/18/19（提权）+ RESULTS.md
├─ elevated-real\                   真实软件 01–06（提权）+ RESULTS.md
├─ elevated-arch\                   压缩包 06 组逐包单跑 + RESULTS.md
├─ elevated-a25\                    A25 入口分层与黑名单逐子样本 + RESULTS.md
├─ elevated-f13\                    F13 静默参数探测 + 原始 argv 日志
├─ elevated-a29\                    A29 安装成功判定逐样本 + RESULTS.md
├─ elevated-a30\                    A30 超时与活动感知逐样本 + RESULTS.md
├─ elevated-batch\                  批量 50 + 三层嵌套 + 10 个 ISO + RESULTS.md
├─ elevated-misc\                   自绘 OCR + 跳过/兜底（含 zip 炸弹）+ RESULTS.md
├─ elevated-doc\                    文档类 08 + 长样本 A30-07/09 + RESULTS.md
~~~

## 6. 复现方式

~~~powershell
$Exe = "<DESKTOP>\AutoTrigger.exe"
$S   = "<SUITE_ROOT>\samples"

& $Exe --input "$S\18-合成安装器(NSIS)" --output ".\18.json" --log-level debug
& $Exe --check-prereq --json
& $Exe --capabilities
& $Exe --dump-resources .\atres      # 导出内置规则/模板用于核对
~~~

## 7. 建议的修复优先级

1. **ISSUE-01 + ISSUE-02（提权）**——改动最小、收益最大；把 `CreateProcess` 换成 `ShellExecuteEx(runas)`，本机不会弹窗。
2. **ISSUE-03（黑名单）**——把子串匹配改成带边界的强特征，立刻多救回 3 个样本（含 `MSI-06` 升级链、`INNO-06` 假成功专项）。
3. **ISSUE-12（3010）**——把 3010/1641 提为全局成功码，避免静默安装的"需重启"软件被误判。
4. **ISSUE-04 + ISSUE-05（GUI 兜底）**——补齐模板 + OCR 就绪判据改"banner + 预热"。
5. 其余（ISSUE-06~11、13、14）为判定与契约层面的打磨。
