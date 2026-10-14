# ISSUE-03｜黑名单正则用「卸载」做子串匹配，误杀文件/目标名含"卸载项"的合法安装器（高）

- **严重级别**：高（合法安装器被直接跳过，零执行）
- **状态**：待修复
- **关联验收项**：A25 ① / F17 黑名单

## 一、问题现象

`samples\07-脚本与快捷方式\09-快捷方式-指向安装器.lnk` 指向一个**合法安装器**，但工具把该 `.lnk` 判为黑名单直接跳过，状态 `skipped`、`selection_reason = excluded_blacklist`，**没有产生任何执行动作**（哨兵日志里也没有预期的 `A29-03` 记录）。

## 二、复现步骤

```powershell
:: 快捷方式真实指向（WScript.Shell 解析结果）
09-快捷方式-指向安装器.lnk  ->  ...\samples\11-安装成功判定\A29-03-标准安装-落盘+卸载项.exe
```

```powershell
.\AutoTrigger.exe --input ".\安装包测试\samples\07-脚本与快捷方式" `
  --output ".\AutoTrigger测试报告\evidence\07-group.json" `
  --log-file ".\AutoTrigger测试报告\evidence\07-group.log" `
  --timeout 180 --log-level debug
```

## 三、证据

### 3.1 运行日志（`evidence\07-group.log`）

```text
[信息] 【入口】选用入口：...\09-快捷方式-指向安装器.lnk（优先级 P0，判定依据 entry_p0_lure）
[信息] 【识别】识别结果：...\09-快捷方式-指向安装器.lnk → shortcut（1.0 KB）
[信息] 【结果】...\09-快捷方式-指向安装器.lnk → 跳过
        （excluded_blacklist: uninstall|unins0|卸载|反安装|remove）
```

### 3.2 命中的内置规则（`--dump-resources` 导出，逐字复制）

```json
[{"id":"uninstall","pattern":"uninstall|unins0|卸载|反安装|remove"},
 {"id":"repair","pattern":"repair|修复|modify"},
 {"id":"debug","pattern":"crashpad|crashreporter|werfault|debug"},
 {"id":"update","pattern":"update|updater|checkupdate|升级"},
 {"id":"help","pattern":"\\.(chm|hlp|pdf)$"}]
```

解析后的目标名 `A29-03-标准安装-落盘+卸载项.exe` 命中子串 `卸载`（`卸载项` = "uninstall **entry**"，即注册表卸载项，**不是卸载程序**），于是被当作"卸载器"拦掉。

### 3.3 结果 JSON（`evidence\07-group.json`）

```json
{"file_path":"...\\09-快捷方式-指向安装器.lnk",
 "detected_type":"shortcut",
 "selection_reason":"excluded_blacklist",
 "final_status":"skipped",
 "attempts":[]}
```

### 3.4 哨兵日志（`C:\Users\Public\AT-SENTINEL\ran.log`）—— 目标确实没被执行

```text
2026-10-11 10:13:56  COM
2026-10-11 10:13:58  SCR
SCRIPT-bat / SCRIPT-cmd / SCRIPT-ps1 / SCRIPT-vbs / SCRIPT-wsf / SCRIPT-utf16
2026-10-11 10:15:58  DISGUISE-text-as-exe
2026-10-11 10:16:15  ENTRY-install
...
```

**没有** `A29-03`（样本清单要求的断言点），即合法安装器从未运行。

## 四、期望行为

黑名单应当匹配**"可执行体的用途"**，而不是文件名里的任意子串。建议：

1. 收窄为强特征，例如 `^(unins\d{3}|uninstall|uninst|卸载|反安装|remove)\.(exe|com)$`，并要求**词首/词尾边界**，避免 `卸载项` 这类复合词被命中；
2. 或改成"词表 + 边界"匹配（`\b(卸载|反安装)\b` 在中文场景需自定义边界：`卸载` 后不得紧跟 `项|信息|说明|文件`）；
3. 对 **P0/P1 优先入口** 做二次确认：若入口是 readme/快捷方式明确指向的目标，即使命中黑名单也应记录为 `skipped_p0_blacklist` 并在结果里给出目标全路径，便于人工复核（当前只给了一个正则字符串）。

## 五、第二个实锤：`升级` 同样误杀升级类 MSI（已提权会话复测）

在**已提权**的 `19` 组里，`MSI-06-升级覆盖V1.msi` / `V2.msi` 因为文件名带 **`升级`**，命中 `update|updater|checkupdate|升级`，被整条跳过：

```text
MSI-06-升级覆盖V1.msi  -> skipped  notes=excluded_blacklist: update|updater|checkupdate|升级
MSI-06-升级覆盖V2.msi  -> skipped  notes=excluded_blacklist: update|updater|checkupdate|升级
```

而清单对 `MSI-06` 的要求是 **`V1 → V2 连续跑两次`** 验证 `A3 / F15.5`（MajorUpgrade 覆盖安装），
现在**这一步完全跑不了**——不是判定错，而是**样本根本没被执行**。

证据：`elevated\19-group.json`（`MSI-06\*.msi` 均为 `skipped`）、`elevated\19-group.log`。

## 六、第三个实锤：Inno 组的 `INNO-06-假成功-只解压无卸载项.exe` 也被跳过

`elevated\17-group.json` 中：

\\\text
INNO-06-假成功-只解压无卸载项.exe  -> skipped
notes = excluded_blacklist: uninstall|unins0|卸载|反安装|remove
\\\

清单预期是 `install_unverified`（验证 A29 ① "假成功只解压无卸载项"），现在**连执行都没执行**，专项验收等于没跑。

### 三次误杀的共同点

| 样本 | 命中词 | 命中的是…… |
|---|---|---|
| `09-快捷方式-指向安装器.lnk` | `卸载` | 目标名 `...落盘+卸载项.exe` 里的"**卸载项**" |
| `MSI-06-升级覆盖V1/V2.msi` | `升级` | "升级**覆盖**安装"这个动作名 |
| `INNO-06-假成功-只解压无卸载项.exe` | `卸载` | "**无**卸载项"——明明是**没有**卸载项 |

三例都不是卸载器，全是**描述性用词**。可见当前是纯粹的"子串包含"，没有任何语义/边界判断。

## 六之二、★ 最严重的后果：整组 A29「安装成功判定」被砍掉 4/13

在 **已提权**会话下逐个跑 `11-安装成功判定` 的 13 个样本，结果有 **4 个直接被黑名单跳过**：

| 样本 | 命中词 | notes |
|---|---|---|
| `A29-03-标准安装-落盘+卸载项.exe` | `卸载`（"卸载项"） | `excluded_blacklist: uninstall|unins0|卸载|反安装|remove` |
| `A29-04-per-user安装-HKCU卸载项.exe` | `卸载`（"卸载项"） | 同上 |
| `A29-09-覆盖升级-字段变化.exe` | `升级` | `excluded_blacklist: update|updater|checkupdate|升级` |
| `A29-11-口径对照-仅非卸载项注册表副作用.exe` | `卸载`（"**非**卸载项"） | 同上 |

这 4 个恰好是 A29 里最核心的几条：

- `A29-03` 是"标准安装 → 应判 install_completed/high"的基线；
- `A29-04` 是"只写 HKCU 也要认"的验证；
- `A29-09` 是覆盖升级（A3/F15.5）；
- `A29-11` 是那处**PRD 口径歧义**的对照样本。

**它们全都没跑**，所以整个 A29 专项等于**有 4 条验收无法执行**。

## 六之三、已确认的受害者清单（累计 7 例）

| # | 样本 | 命中词 | 预期结果 |
|---|---|---|---|
| 1 | `07-脚本与快捷方式\09-快捷方式-指向安装器.lnk` | `卸载`（目标名"卸载项"） | `install_completed` |
| 2 | `19-...\MSI-06-升级覆盖V1.msi` | `升级` | `install_completed` |
| 3 | `19-...\MSI-06-升级覆盖V2.msi` | `升级` | `already_installed / install_completed` |
| 4 | `17-...\INNO-06-假成功-只解压无卸载项.exe` | `卸载`（"无卸载项"） | `install_unverified` |
| 5 | `11-...\A29-03-标准安装-落盘+卸载项.exe` | `卸载` | `install_completed / high` |
| 6 | `11-...\A29-04-per-user安装-HKCU卸载项.exe` | `卸载` | `install_completed / high` |
| 7 | `11-...\A29-09-覆盖升级-字段变化.exe` | `升级` | `install_completed` |
| 8 | `11-...\A29-11-口径对照-仅非卸载项注册表副作用.exe` | `卸载` | 口径对照 |

（8 例；其中"卸载项"这一类占了 5 例——**全是样本名在描述"卸载项/没有卸载项"这种元信息**。）

## 七、影响面

任何文件名/目标名包含 `卸载`、`update`、`edition`、`升级`、`repair`、`修复`、`remove` 的**正常**安装包都会被静默跳过，例如：

- `XX安装卸载.exe`（含"卸载"）
- `XX升级包.exe`、`XX-升级覆盖.msi`（含"升级"）
- `XX_Updater.exe`、`XXCheckUpdate.exe`（含 update）
- 而 `卸载项`、`升级说明`、`remove_tool_说明书.txt` 这类**描述性**用词都会被误伤。

**这不是边缘情况**：`升级/卸载` 是中英文安装包命名里最高频的词之一。
