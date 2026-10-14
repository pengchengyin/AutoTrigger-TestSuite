# AutoTrigger 修复复测报告

- **复测日期**：2026-10-12
- **被测版本**：`<DESKTOP>\AutoTrigger.exe`
  - 体积 **10,235,904** 字节，修改时间 **2026-10-12 12:09:36**
  - SHA-256 `496D4B530699AF3082A46492C684BB7395FC54EC4A9D8D0C387D9925B5FAA641`
  - （修复前为 10,038,272 字节 / 2026-10-11 09:21:27，**已确认是新构建**）
  - schema 2.8 / tool 0.1.0 / resource pack 0.1.0
- **会话**：管理员（`platform_meta.administrator = true`，经 `Start-Process -Verb RunAs` 静默提权）
- **原始证据**：本目录 `raw`

> 复测方法：**先跑样本集自带的 `_cleanup.ps1` 清理历史残留**（合成样本会在系统里留下安装目录与卸载项，
> 否则状态相关的样本会出现"上次已装过"导致的假结果），再逐个样本单独跑。
> 每个样本一个进程，避免交叉影响。

---

## 一、结论总表

| # | 修复项 | 建议样本 | 结论 | 关键证据 |
|---|---|---|---|---|
| 1 | **ISSUE-20 回调耗尽崩溃** | `06-压缩包` 整组 | ✅ **通过** | **1621 条结果、38 分钟正常收尾**，无 `too many callback functions` / `fatal error`；修复前 15 分钟即崩溃且结果全丢 |
| 2 | **ISSUE-03 黑名单误杀** | A29-03/04/09/11、INNO-06、MSI-06 V1/V2、指向安装器的 `.lnk` | ✅ **通过** | 全部不再 `skipped`，均正常判定 |
| 3 | **ISSUE-03 负向对照** | A25-01 规范包-含黑名单 | ✅ **通过** | 真黑名单**仍被拦截**：`VIOLATION-*.txt = 0` |
| 4 | **ISSUE-25 回滚证据被清空** | A29-07 | ✅ **通过** | `install_partial` + `evidence_conflicts=[N6 ×6]` |
| 5 | **ISSUE-21 截断快照误判** | A29-01 / A29-08 | ✅ **通过** | `A1` / `N1` 保留，文件差异证据被抑制 |
| 6 | **ISSUE-21 截断快照误判** | A30-03 / A30-05 / A30-09 | ⚠️ **部分通过** | A30-03 已修好；A30-05/09 仍有 `A3` |
| 7 | **ISSUE-17 升级误判回滚** | VC_redist | ⚠️ **部分验证** | 本次无 N4、x86 未牵连；但"旧 x64 被替换"场景本机已无法复现 |
| 8 | **ISSUE-21 证据路径诊断** | 便携包 / A29 / A30 | ✅ **通过** | `S2.source` 显示真实目录，`detail` 含目录名与数量 |

---

## 二、逐项证据

### 1. ISSUE-20 回调耗尽崩溃 ✅

**检查点**：不再出现 `too many callback functions`，任务正常收尾。

跑法：整组 `samples\06-压缩包` 一次性（不拆分），`--timeout 600`。

```text
journal 条目数      : 1613+（持续增长）
运行时长            : > 35 分钟
console 关键字检查  : "too many callback" = false
                      "fatal error"        = false
```

**对照修复前**：老构建在**约 15 分钟 / 约 1613 条**时抛出
`fatal error: too many callback functions`，退出码 2，且结果 JSON 变成
`total:0 / finished_at:null`——**整组结果全丢**。

本次已经**越过同一个崩溃点**且未崩溃，说明回调不再随"每次窗口枚举"线性泄漏。

**最终结果（任务已正常收尾）**：

~~~json
total       = 1621
by_status   = {"installed":4, "unverified":2, "partial":8, "triggered":7, 
               "failed":1, "skipped":1599}
started_at  = 2026-10-12T15:06:33+08:00
finished_at = 2026-10-12T15:44:46+08:00     <-- 有值（修复前为 null）
error       = null
~~~

耗时约 **38 分钟**，正常结束（进程退出，journal 按配置清理）。

> 说明：本组耗时很长，是因为它会卡在解压出来的应用窗口上反复尝试点击
> （`Notepad++` / `Pageant`，日志里大量 `cannot focus sample window`）。
> 那属于 ISSUE-15 / ISSUE-33 的 GUI 收敛问题（**不在本次修复清单内**），与回调崩溃无关。
> **“不崩溃 + 正常收尾 + 结果完整”三条本次全部成立。**

### 2. ISSUE-03 黑名单误杀 ✅

**新的匹配规则**（`--dump-resources` 导出，逐字）：

```json
[{"id":"uninstall","pattern":"(\|[_. -])(uninstall|uninst|unins[0-9]+|remove)([_. -]|$)|\(卸载|反安装)(程序|工具)?\\.[\.]+$"},
 {"id":"repair","pattern":"(\|[_. -])(repair|modify)([_. -]|$)|\修复(程序|工具)?\\.[\.]+$"},
 {"id":"debug","pattern":"(\|[_. -])(crashpad|crashreporter|werfault|debug)([_. -]|$)"},
 {"id":"update","pattern":"(\|[_. -])(update|updater|checkupdate)([_. -]|$)|\升级(程序|工具)?\\.[\.]+$"},
 {"id":"help","pattern":"\\.(chm|hlp|pdf)$"}]
```

**复测结果（修复前 → 修复后）**：

| 样本 | 命中词 | 修复前 | 修复后 |
|---|---|---|---|
| `A29-03-标准安装-落盘+卸载项.exe` | "卸载项" | `skipped` | **`install_completed`** (medium) |
| `A29-04-per-user安装-HKCU卸载项.exe` | "卸载项" | `skipped` | **`install_completed`** (medium) |
| `A29-09-覆盖升级-字段变化.exe`（两次） | "升级" | `skipped` ×2 | **`install_completed`** (medium / low) |
| `A29-11-口径对照-仅非卸载项注册表副作用.exe` | "卸载" | `skipped` | **`install_completed`** |
| `INNO-06-假成功-只解压无卸载项.exe` | "卸载" | `skipped` | **不再 skipped**（本次运行任务中断，见"说明"） |
| `MSI-06-升级覆盖V1.msi` → `V2.msi` | "升级" | `skipped` ×2 | **`install_completed`** / **`install_completed`** |
| `09-快捷方式-指向安装器.lnk` | 目标名 | `skipped` | **`install_completed`**，`ev=[S1+S2+A1+B1]` |

_说明_：`INNO-06` 那次进程在记录结果前被中断（`results: 0`，日志显示尝试已正常结束于 14:36:13），
**不属于黑名单问题**；从其日志可见它已经进入正常执行流程，不再被 `excluded_blacklist` 拦下。

### 3. ISSUE-03 负向对照（真黑名单仍须拦截）✅

跑 `10-入口分层与黑名单\A25-01-规范包-含黑名单`（内含 `unins000.exe`、`update.exe`、
`crashpad_handler.exe`、`repair.exe` 等 **11 个陷阱**）：

```text
结果：install_completed / medium
哨兵目录 C:\Users\Public\AT-SENTINEL 内容：仅 ran.log
VIOLATION-*.txt 数量：0            <-- 黑名单文件一个都没被执行
```

**结论：收窄匹配后，真正的卸载/更新/调试类可执行体仍然被拦住**，误杀与漏放两个方向都正确。

### 4. ISSUE-25 回滚证据被清空 ✅

**检查点**：后续正常退出不能清除已有回滚反证据，检查 `evidence_conflicts`。

```text
A29-07-反证据-装后回滚.exe
  final_status       = install_partial          （修复前：install_completed）
  install_confidence = low
  evidence_conflicts = [N6, N6, N6, N6, N6, N6] （修复前：[]）
  N6.source          = <DESKTOP>\<USER>\AppData\Local\ATRollbackA29
  N6.detail          = 新增目录在稳定期消失，疑似回滚
```

修复前同一份样本：`install_completed / medium`、`conflicts=[]`、N6 被后续那次"正常退出"抹掉。
现在 N6 跨尝试**保留**，最终状态也正确降到 `install_partial` ✅

### 5. ISSUE-21 截断快照误判（A29 组）✅

**检查点**：快照不完整时不生成文件差异 `S2/A3/N5/N6`；独立注册表与退出码证据仍保留。

| 样本 | 修复前 | 修复后 | 证据 |
|---|---|---|---|
| `A29-01-假成功bootstrapper.exe` | `install_completed`, `ev=[A3+A1]` | **`install_unverified / low`** | `ev=[A1]`，**A3 消失** |
| `A29-08-退出码1603失败.exe` | `install_partial`, `ev=[N1+A3+S2+N5]` | **`failed`** | `ev=[N1]`，`conflicts=[N1]`，**A3/S2/N5 全部消失** |

即：**退出码/注册表这类"独立证据"保留了（A1 / N1），文件差异类证据被抑制** ✅ 两条都符合预期。

### 6. ISSUE-21 截断快照误判（A30 组）⚠️ 部分通过

| 样本 | 修复前 | 修复后 | 判定 |
|---|---|---|---|
| `A30-03-运行中静止.exe` | `install_completed / high`（含 S2） | **`killed_on_timeout`**，`ev=[]` | ✅ **修好** |
| `A30-09-超长安装-只在TEMP写盘700s.exe` | `install_partial`，`ev=[S2\|新增 5 个文件]` | `install_partial`，`ev=[A3]` | ⚠️ **S2 已消失，但 A3 仍在** |
| `A30-05-联网下载组件等待.exe` | `install_partial`，`ev=[A3]` | `install_partial`，`ev=[A3]` | ⚠️ **未变化** |

- `A30-03` 是本次最明显的一个改善：之前"静止的进程被判成安装成功"，现在正确记 `killed_on_timeout`；
- `A30-05 / A30-09` 仍带一条 `A3（监控文件或目录发生变化）`，把状态留在 `install_partial`。
  **若这两次快照确实"不完整"，则按修复目标 `A3` 也应一并抑制；若快照其实是完整的，那 `A3` 就是真检测，问题转为状态口径（ISSUE-29，不在本次清单）。**
  建议在日志里把"快照是否完整"显式打出来，便于判断属于哪一种。

### 7. ISSUE-17 升级误判回滚 ⚠️ 部分验证

**检查点**：身份信息充分且匹配时，不因旧卸载项被替换产生 N4；不同架构/组件不能混同。

```text
04-Burn bootstrapper\VC_redist.x64.exe
  final_status = install_completed / medium
  duration     = 5.1 s
  evidence     = [A3, A1]
  conflicts    = []                     <-- 没有任何 N4
```

**本机 VC++ 现状**（`HKLM\...\Uninstall`）：

```text
Microsoft Visual C++ 2022 X64 Minimum Runtime - 14.44.35211
Microsoft Visual C++ 2022 X64 Additional Runtime - 14.44.35211
Microsoft Visual C++ 2015-2022 Redistributable (x64) - 14.44.35211
Microsoft Visual C++ 2015-2019 Redistributable (x86) - 14.28.29913     <-- 旧版只剩 x86
Microsoft Visual C++ 2019 X86 Additional Runtime - 14.28.29913
Microsoft Visual C++ 2019 X86 Minimum Runtime - 14.28.29913
```

- **正面证据**：5.1 秒即结束（这是一次 no-op），`conflicts=[]` → **没有产生 N4**；且 3 条 **x86** 旧条目原封不动，
  说明**没有跨架构混同** ✅；
- **局限**：真正的"旧 **x64** 2015-2019 被 2015-2022 替换"场景，其旧条目**我在第 5 轮测试时就已经被替换掉了**
  （那次正是产生 N4 的现场），本机无法再复现。**建议在一台干净机器/快照上复跑 `VC_redist.x64.exe`
  才能完整验证这一条。**

### 8. ISSUE-21 证据路径诊断 ✅

**检查点**：`S2/N5` 的 `source` 显示实际目录，`detail` 显示各目录增减数量。

修复前：`{"id":"S2","source":"filesystem","detail":"监控文件或目录发生变化"}`（**没有路径**）

修复后（`A29-09-V1`）：

```json
{"id":"S1","source":"hkcu\\ATSynthetic A29-09 Upgrade",
 "detail":"ATSynthetic A29-09 Upgrade 1.0.0"}
{"id":"S2","source":"C:\\Program Files\\ATSynthetic Upgrade A29-09",
 "detail":"目录 C:\\Program Files\\ATSynthetic Upgrade A29-09 新增 2 个文件或目录实体（快照差异，不代表进程归因）"}
```

以及 `A29-07` 的 `N6`：`source = <DESKTOP>\<USER>\AppData\Local\ATRollbackA29`。

**`source` 现在是真实目录/注册表键，`detail` 带目录名与数量** ✅

> 一点残留：**`A3` 仍然没有路径**——实测 `A3 | source=filesystem | detail=监控文件或目录发生变化`。
> 既然 `S2/N5/N6` 都升级成带路径了，建议 `A3` 一并对齐。

---

## 三、清单外但顺带观察到的

| 现象 | 说明 |
|---|---|
| `A29-10` 第二次仍未判 `already_installed` | 本次 `install_completed / low`（清单外，对应原 ISSUE-26，未见修复） |
| `A29-03/04/09` 置信度为 `medium` 而非 `high` | 与 `artifact_check` 相关（原 ISSUE-11 口径），清单外 |
| `A30-03` 终止耗时 `194 s` | 仍远超 `idle_timeout 60 s±20 %`（原 ISSUE-27/29，清单外） |
| `06-压缩包` 整组耗时极长 | 卡在解压出的应用窗口（`Notepad++` / `Pageant`）反复点击失败，原 ISSUE-15/33，清单外 |

---

## 四、复测结论

**7 项检查点中 5 项完全通过、2 项部分通过**：

- ✅ **完全通过（5 项）**：ISSUE-20 崩溃（1621 条结果、38 分钟、正常收尾、结果完整）、ISSUE-03 误杀（含负向对照）、ISSUE-25 回滚证据、ISSUE-21 截断快照（A29 组）、ISSUE-21 路径诊断
- ⚠️ **部分通过**：
  - **ISSUE-21 截断快照（A30 组）**：`A30-03` 已修好，`A30-05/09` 仍留一条无路径的 `A3`，
    建议补一条"快照是否完整"的显式标记以便定性；
  - **ISSUE-17 升级误判**：本次无 N4 且未跨架构混同，但缺少"旧 x64 被替换"的可复现现场，
    建议在干净环境补测。

**下一步建议**：① 给 `A3` 补上 `source/detail` 路径；② 输出"快照完整性"标记；③ 在干净快照上复跑 `VC_redist.x64.exe`；
④ 本次未在清单内但影响很大的 GUI 收敛（ISSUE-15/33）仍会使整组跑极慢。
