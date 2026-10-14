# ISSUE-16｜已走完 GUI 向导并取得 S1+S2，却因硬超时被判 `install_partial`（高）

- **严重级别**：高（把"确实装好了"的软件报成"部分成功"，且失败尝试污染证据链）
- **状态**：待修复
- **关联验收项**：A13 / A29 / F15 / A12
- **发现环境**：已提权，真实软件样本 `01-Inno Setup\Notepad3-Setup.exe`（清单预期 `install_completed / high`）

## 一、问题现象

`Notepad3-Setup.exe` 实测 `install_partial / low`。但证据显示**它其实是被 GUI 自动化完整走完并安装成功的**：

```text
attempt[2] 方法=silent_install
  gui_actions = 确定(uia) -> 下一步(N)(uia) -> Accept(uia) -> 下一步(N)(uia)
                -> 我同意此协议(A)(uia) -> 下一步(N)(uia) x4
                -> 安装(I)(uia) -> 完成(&F)(win32)
  install_evidence = S1|Notepad3 (x64) 6.24.1221.1
                     S2|新增 47 个文件或目录实体
                     A2|完成(&F)
  result = killed_on_timeout  dur=288.8s  term=killed_tree  err=deadline_or_interrupt
```

**关键点**：`完成(&F)` 已经点掉了、卸载项和 47 个文件都出现了，**安装已经完成**；
但因为进程树在硬超时前没有全部退出，工具把整轮记为 `killed_on_timeout`，
最终按"有落盘但被终止"降到 `install_partial / low`。

## 二、第二个问题：首次"秒失败"尝试污染证据

```text
attempt[1] silent_install "/VERYSILENT" "/NORESTART" "/SUPPRESSMSGBOXES"
           exit=1   result=exited   dur=2.4s
           evidence = ["N1|1"]
...
evidence_conflicts = [{"id":"N1","detail":"1"}]
```

第 1 次尝试 **2.4 秒就返回退出码 1**（Inno 的 `/VERYSILENT` 在这个安装器上直接失败），
这条 `N1` 一直挂在最终结果里成为 `evidence_conflicts`，与后面"向导全部走完"的强证据打对台。

## 三、期望行为

1. **"安装已完成"的判据应优先于"进程被超时终止"**：
   已经出现 `S1（卸载项）+ S2（落盘）` 且点掉了向导的 `安装` / `完成`，就应判
   `install_completed`（若需重启则 `requires_reboot=true`），并在 notes 注明"超时终结但已取得安装证据"。
   **这个口径 `INNO-09` 已经做到了**（`install_completed` + `terminated on timeout; installation evidence still collected`），
   说明规则存在，只是**在真实 Inno 安装器上没走到**。
2. **失败尝试的 `N1` 不应跨尝试累积**：`/VERYSILENT` 失败属于"这个参数不合适"，
   与"安装是否成功"是两个层次。建议每条 attempt 自带结论，最终判定只看**成功尝试**（或按权重合成），
   避免一条 2.4 s 的秒退把 `290 s` 的完整安装拉低。
3. **"秒失败"要区别对待**：退出码 1 且耗时 < 3 s 更可能是参数不被接受；
   本例后续 GUI 路径其实是有效的，说明策略对，只是证据没合并好。

## 四、附带观察：`S1` 证据疑似被"无关软件"污染

`Notepad3` 这一轮的 `S1` 里出现了**两个**卸载项：

```text
S1|Notepad3 (x64) 6.24.1221.1 6.24.1221.1
S1|Opera Stable 137.0.6036.39 137.0.6036.39     <-- 与本次安装无关
```

`Opera Stable` 显然是机器上别的软件（很可能是后台自动更新重建了卸载项）在**同一时间窗口**发生的注册表变化。
当前 `S1` 采用"三处 Uninstall 根的 diff"，会把**任何同期的无关变化**算作本次安装的证据。建议：

- 至少在 `S1` 里带上**可归因性判断**（例如 `DisplayName` / `Publisher` / `InstallLocation` 与样本元信息的相关度）；
- 或把可疑条目单独放（如 `unattributed_arp_changes`），不要混进 S 级证据。

## 五、影响面

真实 Inno 安装器（Notepad3、以及带许可页/完成页的软件）普遍是这个形态：
`/VERYSILENT` 不被支持 → GUI 兜底走完 → 装完自动启动或停在完成页 → 被硬超时截断。
如果"超时终结但已取得安装证据"的口径不能稳定生效，**大量真实软件都会被报成 `install_partial`**。
