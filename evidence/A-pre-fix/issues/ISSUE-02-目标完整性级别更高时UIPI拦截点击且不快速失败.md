# ISSUE-02｜目标窗口完整性级别高于工具时点击被 UIPI 拦截，但工具不快速失败、空耗 306 秒（致命）

- **严重级别**：致命（既装不上，又极大浪费单文件时间预算）
- **状态**：待修复
- **关联验收项**：A12 / A32 / F14 / F9

## 一、问题现象

对 `samples\01-Inno Setup\Notepad3-Setup.exe`（预期 `install_completed / high`）实测：

- 第 1 次尝试 `/VERYSILENT /NORESTART /SUPPRESSMSGBOXES` 返回**退出码 1**（8.5 s）；
- 之后工具发现了一个 **High 完整性级别（0x3000）** 的安装窗口「选择安装语言」，而工具自身是 **Medium（0x2000）**，所有 `win32` 点击被 Windows UIPI 拦截；
- 工具**明知原因**，却仍继续第 2–5 次尝试，每次都等到静默期超时被强杀；
- 最终耗时 **306.4 秒**，结论为 `install_partial / low`。

## 二、复现步骤

```powershell
.\AutoTrigger.exe --input ".\安装包测试\samples\01-Inno Setup\Notepad3-Setup.exe" `
  --output ".\AutoTrigger测试报告\evidence\01-Notepad3.json" `
  --log-file ".\AutoTrigger测试报告\evidence\01-Notepad3.log" `
  --timeout 300 --log-level debug
```

## 三、证据

### 3.1 日志中反复出现的根因（`evidence\01-Notepad3.log`）

```text
[调试] 【界面】界面识别/点击未产生动作：窗口 "选择安装语言" 的按钮 "确定"（win32）点击失败：
       窗口 "选择安装语言" 的权限高于本工具（目标 0x3000，本工具 0x2000），
       输入可能被 Windows UIPI 拦截；请以管理员身份运行本工具后重试
```

该行在整轮运行中**重复数十次**（10:26:04–10:26:15 期间每秒 1–2 次），说明工具能识别到窗口与按钮，却无法跨越完整性级别。

### 3.2 时间与尝试序列（`evidence\01-Notepad3.json`）

```text
[1] method=silent_install cmd="...\Notepad3-Setup.exe" "/VERYSILENT" "/NORESTART" "/SUPPRESSMSGBOXES"
    exit=1     result=exited            dur=8.5s   term=natural
[2] method=silent_install cmd="...\Notepad3-Setup.exe" "/S"
    exit=null  result=killed_on_timeout dur=101.0s term=killed_tree  err=idle_timeout
[3] method=silent_install cmd="...\Notepad3-Setup.exe" "/s" "/v/qn"
    exit=null  result=killed_on_timeout dur=98.8s  term=killed_tree  err=idle_timeout
[4] method=silent_install cmd="...\Notepad3-Setup.exe" "/quiet" "/norestart"
    exit=null  result=killed_on_timeout dur=68.8s  term=killed_tree  err=idle_timeout
[5] method=silent_install cmd="...\Notepad3-Setup.exe" "/silent"
    exit=null  result=killed_on_timeout dur=2.0s   term=graceful     err=deadline_or_interrupt

final_status=install_partial  install_confidence=low
evidence_conflicts=[{"id":"N1","detail":"1"}]
```

### 3.3 日志尾部

```text
[信息] 【执行】本轮尝试结束：超时被强制终止，耗时 68.8 秒
[信息] 【判定】第 4/9 次尝试判定：部分完成（置信度 low）
[警告] 【判定】证据冲突（N1）：安装进程返回失败退出码 1
...
[信息] 【结果】本次运行结束：总耗时 306.4 秒，退出码 0 —— 处理完成
[信息] 【结果】总体结论：部分成功
```

## 四、期望行为

1. **识别到 `目标 IL > 本工具 IL` 即快速失败**（或先自动提权重试一次），而不是把 9 次尝试全跑完。建议新增专属状态 `failed: target_elevated_uipi`（或 `needs_elevation`）并在 notes 里给出「请以管理员身份运行」。
2. **父进程退出码不可作为唯一判据**：本例中父进程 exit=1，但真正的安装在**它重新拉起的提权子进程**里进行。工具应以子进程树 / 窗口归属为准判定，而不是立刻记 N1「证据冲突」。
3. **失败即清理**：本轮结束后应确保被强杀的安装进程及其子进程、遗留窗口全部回收（见 `11-原生导出表(7z).dll` 一轮后仍遗留 `msiexec.exe` PID 8712 的同类现象）。

## 五、备注

Issue-01 与 Issue-02 是同一根因（工具自身未提权）的两种表现：

- Issue-01：目标清单为 `requireAdministrator` → Windows 直接拒绝 `CreateProcess`；
- Issue-02：目标先以 Medium 启动、再自我提权 → 工具被 UIPI 挡在窗口外。

**只要工具自身以管理员身份运行，两者大概率同时消失。**
