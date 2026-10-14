# ISSUE-21｜落盘证据（S2/N5）无法归因，且同一次判定里自相矛盾（高）

- **严重级别**：高（S2 是 S 级证据、N5 是 N 级反证据，两者都被污染时安装判定不可信）
- **状态**：待修复
- **关联验收项**：F15.1 / F15.2 / F15.3（S2 / N4 / N5）
- **发现环境**：已提权，样本 `06-压缩包\nssm-2.24.zip`

## 一、问题现象

内层 `nssm.exe` 的第 9 次尝试（`no_param_run`）一次性给出**方向相反**的两条磁盘证据：

```text
[9] no_param_run  "<TEMP>\AT-1907365336\nssm-2.24\win64\nssm.exe"
    exit=1   artifact=ok
    install_evidence =
      S2|新增 39 个文件或目录实体
      N5|移除 39 个文件或目录实体
      N1|1
final_status = install_partial   install_confidence = low
```

日志同一时刻：

```text
2026-10-11 12:03:45 [警告] 【判定】证据冲突（N5）：监控目录实体数量减少（疑似回滚）：移除 39 个文件或目录实体
2026-10-11 12:03:45 [结果】...\AT-1907365336\nssm-2.24\win64\nssm.exe → 部分完成
```

**"+39 个新增" 与 "-39 个移除" 同时成立**，而 `nssm.exe` 本身只打印 Usage 就退出（exit=1，无任何安装行为）。

## 二、我做了验证：最初的猜想**被证伪**

**猜想**：这个 39 是不是工具自己解压出来的临时树被算进了快照？
（依据：日志显示 `【解压】开始解压到临时目录：<DESKTOP>\<USER>\AppData\Local\Temp\AT-1907365336`，
而 `watch_exclude` 里明明有 `%TEMP%`；`snapshot_depth=2` 时 `Local\Temp\AT-xxx` 正好落在深度 2。）

**验证**：构造一个**只含 7 个文件**的压缩包（1 个 exe + 6 个 txt），用同样方式跑一遍：

```text
自定义样本 C:\ATTest\selfnoise\probe.zip（7 个条目）
-> 解压到 <DESKTOP>\<USER>\AppData\Local\Temp\AT-2251533686
-> 结果：where.exe = failed，evidence 只有 N1|2 / N1|1
-> 没有出现 S2，也没有出现 N5
```

**结论：S2/N5 未能复现，"工具把自己的解压树当证据"这一猜想不成立（至少不是唯一原因）。**
因此本问题**不是**"自解压污染"，而是更基础的**证据不可归因**问题。

### 2.1 但"S2 与 N5 同现"本身是**系统性**的（5+ 个样本都能看到）

跑 06 组各条目时，这种"+N 又 -N"的组合反复出现：

| 样本 | 结果 | 证据 |
|---|---|---|
| `nssm-2.24.zip` → `nssm.exe` | `install_partial / low` | `N1+A3+S2+N5` |
| `7z2501-extra.7z` → `7za.exe` | `install_partial / low` | `S2+N5+N1+A1` |
| `7z2501-extra.7z` → `7za.exe`（另一份） | `install_partial / low` | `N1+S2+N5+A1` |
| `7z2501-extra.7z` → `7zxa.dll` | `install_partial / low` | `S2+N5+N1` |
| `7z2501-extra.7z` → `7za.dll` | `install_partial / low` | `A1+S2+N5` |
| **`7z2600-x64-32bit.exe`** | `install_partial / low` | `A3+N1+A1+S2+N5` |

**注意最后一行**：`7z2600-x64-32bit.exe` 是一个**直接执行的安装器**（不是压缩包、不解压到临时目录），
却同样出现 `S2+N5`。**这直接排除了"一定是解压目录造成的"**，说明这是磁盘 diff 机制更普遍的问题。

所以本条的结论是：**现象稳定复现，但根因无法从现有证据判断——因为证据里没有路径。**

## 三、真正的问题：证据只有"数量"，没有"路径"

无论那 39 个实体来自哪里，当前的证据结构都让**任何人无法判断**：

- 证据 detail 只有一句 `"新增 39 个文件或目录实体"` / `"移除 39 个..."`，**没有任何路径**；
- 与此同时机器上还有**无关进程在写盘**（复现时 Zoom 正在运行、AutoTrigger GUI 也开着），
  任何应用的缓存/日志/更新都可能落在 `watch_dirs`（`%LOCALAPPDATA%`、`%APPDATA%`、`%ProgramData%`）；
- 于是 `+39 / -39` 既可能是本样本、也可能是**无关的并发活动**，而工具的判定直接采信。

同类现象在真实软件测试里也出现过：`Notepad3` 那一轮的 `S1` 里混进了**与本样本无关的 `Opera Stable` 卸载项**
（见 [ISSUE-16](ISSUE-16-走完GUI向导仍被硬超时判partial.md) 第四节）。

**这两个案例指向同一个根因：磁盘/注册表 diff 只做"有没有变化"，不做"变化是否可归因于本次样本"。**

## 四、期望行为

1. **证据要带路径（至少带路径前缀/直方图）**：`S2 / N4 / N5` 的 detail 建议给出
   变化实体的**路径样例（前 N 条）+ 顶层目录分布**，例如
   `"新增 39：%LOCALAPPDATA%\Zoom\logs\* (31)，C:\Program Files\NewApp\* (8)"`。
   没有这一步，S2/N5 无法被复核，也无法被修复验证。
2. **加自排除断言**：把本任务的 `archive.temp_root` 绝对路径强制排除，并在任务结束时断言
   "临时根从未贡献任何 diff 条目"（成本极低，顺手把 ISSUE-08 的预算问题一起兜住）。
3. **并发噪音要剔除或降级**：对 diff 实体做**进程树归因**——只采信"由安装器进程树创建"的路径；
   无法归因的条目单独放（如 `unattributed_changes`）且**不得作为 S 级证据**。
4. **同一 attempt 内方向相反的 S/N 证据要拦截**：`S2(+39)` 与 `N5(-39)` 同时出现时，
   应标记证据不可信并要求人工复核，而不是直接合成一个 `install_partial`。

## 五、同一批实验的第二发现：便携压缩包里的 CLI 工具被套用"安装参数表"（这条是确凿的）

`nssm.exe` 是**命令行工具**，但工具给它依次套了 8 种静默安装参数、再跑一次无参，共 9 次：

```text
[1] /VERYSILENT /NORESTART /SUPPRESSMSGBOXES   exit=1
[2] /S                                          exit=1
[3] /s "/v/qn"                                  exit=1
[4] /quiet /norestart                           exit=1
[5] /silent                                     exit=1
[6] --silent                                    exit=1
[7] --quiet                                     exit=1
[8] -s                                          exit=1
[9] （无参）                                     exit=1
```

每次 stderr 都是同一段：

```text
NSSM: The non-sucking service manager
Version 2.24 64-bit, 2014-08-31
Usage: nssm <option> [<args> ...]
```

即：**仅凭"这是个 exe"就套用 Inno/NSIS/InstallShield/WiX 全套静默参数**，既白跑 8 次，
也把"便携工具集"错当"安装器"。而清单对 `nssm-2.24.zip` 的预期只是
"解压后触发内层 nssm.exe（P4 主程序）"，`triggered` 级别即可。

建议：
- 解压产生的条目先做**安装器家族识别**（PE 节表 + 字符串指纹，F17 P2），识别不出就**不要套参数表**，
  直接无参运行并按 `triggered` 记账；
- "退出码 1 + 耗时≈0 + stderr 含 `Usage:`" 是很强的"非安装器"信号，可用于提前收敛。

## 六、证据文件

| 证据 | 位置 |
|---|---|
| S2(+39)/N5(-39) 同现 | `elevated-arch/01-nssm-2.24.json` |
| 判定日志（12:03:45） | `elevated-arch/01-nssm-2.24.log` 第 83–97 行 |
| **证伪实验**（未复现） | `C:\ATTest\selfnoise\probe.json` / `probe.log` |
| 配置 | `--dump-config` 的 `install_verify.watch_dirs / watch_exclude / snapshot_depth` |

## 七、影响面

`S2` 能把结果抬成 `install_completed`，`N4/N5` 能把它压成 `install_partial`——
**这两条证据一旦不可归因，安装判定在"有并发写盘"的真实机器上就不可靠**。
它还会连带影响 `A29-01/02/05/07/11/12` 一系列以"有没有副作用"为核心的验收项。
