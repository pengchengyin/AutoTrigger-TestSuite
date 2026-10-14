# ISSUE-20｜Go 回调表耗尽导致进程致命崩溃，整组结果全部丢失（致命）

- **严重级别**：致命（进程直接 abort，**该组所有结果丢失**，且批量跑越大越必现）
- **状态**：待修复
- **关联验收项**：A6 批量处理 / A7 结果输出 / A31 ⑦
- **发现环境**：已提权，样本组 `06-压缩包`（6 个压缩包）

## 一、问题现象

处理 `06-压缩包` 时，AutoTrigger **运行约 15 分钟（11:45:15 → 12:00:28）后直接崩溃**：

```text
退出码 = 2（工具自己的"参数或路径非法"码，实际是 Go 的 runtime.throw）

fatal error: too many callback functions

goroutine 1 [running]:
runtime.throw(...)
syscall.compileCallback(...)        syscall_windows.go:338
syscall.NewCallback(...)            syscall_windows.go:181
autotrigger/internal/platform/windows.win32Controls(...)   gui_windows.go:240
autotrigger/internal/platform/windows.GUI.Controls(...)    gui_windows.go:122
autotrigger/internal/gui.(*Automator).Step(...)            gui.go:145
autotrigger/internal/core.(*Engine).attempt(...)           attempt.go:103
```

崩溃后：

```json
// elevated-real/06-group.json
{"finished_at": null, "error": null,
 "summary": {"total":0, "by_status":{ ... 全 0 ... }}}
```

**该组的全部结果都没写出来**，只有过程日志 `06-group.json.journal.ndjson` 里留下 **1613 条**逐文件记录。
同时 `06-group.log` 在被打断的那一行**戛然而止**（没有任何优雅收尾/错误落盘）。

## 二、根因分析

Go 的 `syscall.NewCallback` 会在进程内维护一张**回调函数表**，且**条目不会回收**；
创建到一定数量（实现上限约 2000）后，`compileCallback` 就会 `runtime.throw("too many callback functions")`，
这是 **fatal error，recover 不住**。

从调用栈看，这个耗尽点出现在 **GUI 控件枚举的热路径**上：

```text
Engine.attempt  ->  Automator.Step  ->  GUI.Controls  ->  win32Controls  ->  syscall.NewCallback
```

也就是说：**每枚举一次窗口控件就新建一批回调**，而 `gui_automation.poll_interval_ms = 500`（每秒 2 次），
在长时间/多文件的运行里必然堆到上限。

## 三、为什么在 06 组爆掉（放大因素）

06 组是压缩包，工具会**递归解压**并**逐个处理解出来的每个文件**。过程日志显示：

- `putty-0.85-w64.zip` 解出数百个 Cygwin 工具（`cyg*.dll`、`git-*.exe`、`*.h` …）；
- `npp.8.8.1.portable.x64.zip` 解出 Notepad++ 的整个便携目录（各语言/主题 xml）；
- `MobaXterm_Installer.zip` 解出 MobaXterm 全套。

最终产生 **1613 条结果记录**。每条记录都会做基线快照与判定，其中不少还会进入 GUI 枚举——
回调创建次数随之线性增长，于是在这一组触顶崩溃。

## 四、期望行为

### 4.1 修复崩溃（必须）

1. **不要在热路径里反复 `NewCallback`**：把 WndProc / EnumWindows / EnumChildWindows 等回调
   **在包初始化时创建一次并复用**，而不是每次枚举都新建；
2. 若确实需要动态回调，改用 **UIA（COM 接口）** 或不依赖 Go 回调的枚举方式（如 `GetWindow` 轮询）；
3. 在关键循环里加一层**回调计数自检**（或定期重启自身/重置状态），至少在接近上限时给出可诊断的日志与优雅退出。

### 4.2 崩溃不得丢结果（必须）

- 目前崩溃后 `summary.total=0`、`finished_at=null`，**已经跑完的 1613 条结果全部不可用**；
- 既然已经有 `journal.ndjson`（过程日志），应支持**从 journal 恢复/收敛出最终 JSON**，
  或在 `recover()` 之后仍写出"部分结果 + interrupted 标记"。

### 4.3 顺带收敛规模

- 压缩包递归不应把 **数百个无关文件**逐个当样本处理（本例 1613 条里绝大多数是 `skipped`）；
  应在 `7z l` 阶段就按 `install_entries.json` 选出少量入口（这正是 F17 / A25 的设计意图），
  而不是"全解压 + 全遍历"。

## 五、证据文件

| 证据 | 位置 |
|---|---|
| 崩溃栈 | `elevated-real/06-group.console.txt`（第 6800 行附近，UTF-16） |
| 过程日志 | `elevated-real/06-group.json.journal.ndjson`（1613 条） |
| 空结果 | `elevated-real/06-group.json`（`total:0`、`finished_at:null`） |
| 截断的 debug 日志 | `elevated-real/06-group.log`（未收尾） |

## 五之二、附带后果：异常终止会**漏掉解压临时目录的清理**

崩溃/被强杀之后，工具**不会回收**已经解压出来的临时树。实测 `%TEMP%` 下残留：

```text
count = 29 个 AT-* 目录，其中 5 个非空，合计 7.8 MB

%TEMP%\AT-646820435\   (6.81 MB)  <- putty-0.85-w64.zip 的完整解压结果
    PAGEANT.EXE / PLINK.EXE / PSCP.EXE / PSFTP.EXE / PUTTY.CHM / PUTTY.EXE / PUTTYGEN.EXE …

%TEMP%\AT-1665838479\  (0.82 MB)  <- A25 规范包（含 checkupdate.exe / crashpad_handler.exe / sub\ / runtime\）
```

对应时间戳正好是**崩溃点与被强杀点**（11:58 / 10:31）；正常结束的那次（`AT-1907365336`）已被清理。
也就是说：**只有异常终止这条路漏清理**。

**为什么要一起修**：批量跑 300 个样本时，只要中途崩一次，就会把当时解压出来的整棵树留在磁盘上；
本例 `putty` 只有 6.8 MB，但 06 组里 `MobaXterm_Installer.zip` 解出的树要大得多，累积起来不可忽略。
建议在 `defer` / `recover()` 里补一条"无论成功失败都清理本次任务的 `archive.temp_root`"。

## 六、影响面

这条**单独就能判"批量模式不可用"**：

- `_run_tests.ps1` 是"按组批量跑"，任何一组跑到崩溃，那一组的结果就没了；
- 崩溃点出现在 **GUI 枚举**路径，凡是有 GUI 交互的样本都会持续累积回调；
- 说白了：**跑得越久、文件越多，越必然崩**，与"尽可能多装软件"的目标直接冲突。
