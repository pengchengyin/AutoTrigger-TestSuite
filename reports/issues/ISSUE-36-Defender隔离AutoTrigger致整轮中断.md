# ISSUE-36｜Windows Defender 将 AutoTrigger.exe 判为 Trojan:Win32/Bearfoos.B!ml 并在运行中隔离，导致整轮测试中断（致命·环境）

- **严重级别**：致命（对测试流程/结果有效性；环境侧，工具无法自控）
- **状态**：本次已定位并绕过（还原 + 排除）；**未关闭**
- **发现时间**：2026-10-14 22:49（管理员权限全量运行第 5 个样本时）
- **关联**：环境要求、运行中断、逐样本 console 校验

## 一、问题现象

2026-10-14 22:41 起以管理员权限用 `scripts\Invoke-SampleTest.ps1` 逐样本运行 149 个样本。
前 4 个样本正常（audacity / Git 判 `install_completed`）。从第 5 个样本
`01-Inno Setup\WinMerge-2.16.46-x64-Setup.exe` 开始，`cmd.exe /c` 立即返回：

```text
系统无法执行指定的程序。
```

其后 144 个样本全部**秒失败**，`per-sample.csv` 的 149 行中仅 4 行有真实结果，
其余 `最终状态=(无结果)`、退出码 1，但脚本**没有报错、没有提示工具丢失**。

根因：`C:\Users\pengc\Desktop\AutoTrigger.exe` 在运行中被 **Windows Defender 隔离**。

## 二、证据

`Get-MpThreatDetection`：

```text
InitialDetectionTime : 2026/10/14 22:49:15
ThreatID             : 2147731849
Resources            : {file:_C:\Users\pengc\Desktop\AutoTrigger.exe, process:_pid:9352,...}

InitialDetectionTime : 2026/10/14 22:49:21
ThreatID             : 2147731849
Resources            : {file:_C:\Users\pengc\Desktop\AutoTrigger.exe}
```

`Get-MpThreat`：`Trojan:Win32/Bearfoos.B!ml`，SeverityID 5，IsActive False（已被处置）。
`MpCmdRun.exe -Restore` 输出：`file:...AutoTrigger.exe quarantined at 2026/10/14 14:49:38 (UTC) was restored`。

时间线：22:48:59 启动 `ShareX-17.0.0-setup.exe`（22:49:06 桌面出现 `ShareX.lnk`）→
22:49:15 进程被检测 → 22:49:21 文件被检测 → 22:49:38 隔离。

首次运行目录 `runs\20261014-224117`（已重命名为
`runs\_invalid-20261014-224117-defender-quarantine`）中，样本 5 起的 `.console.txt` 内容为
`系统无法执行指定的程序。` 或 `'"C:\...\AutoTrigger.exe"' 不是内部或外部命令`。

## 三、影响

1. **整轮测试静默失效**：不逐条核对 console 就会把这 145 条当成"工具大量失败"，得出完全错误的结论。
2. 自动化脚本没有"被测程序是否还在"的前置/中途校验，是本次静默失效的直接放大器。
3. AutoTrigger 是**未签名的 Go 单文件**，会枚举进程、注入 GUI 输入、启动任意样本，容易命中
   `!ml`（机器学习启发式）这类通用判定；该命中**极可能是误报**，但真实存在。

## 四、本次处置（绕过，非关闭）

管理员会话执行：

```powershell
& "$env:ProgramFiles\Windows Defender\MpCmdRun.exe" -Restore -Name 'Trojan:Win32/Bearfoos.B!ml' -All
Add-MpPreference -ExclusionPath 'C:\Users\pengc\Desktop\AutoTrigger.exe'
Add-MpPreference -ExclusionProcess 'AutoTrigger.exe'
```

还原后校验：`size=7,758,848 B`，`SHA-256=691373269CA840248939482479632C66933B830376C46DDF2BA2DA46206CB7FF`
（与 reports/run-2026-10-14.md 记录的当前分发版一致）。

## 五、期望行为 / 建议

1. **套件侧（必做）**：`docs/environment.md` 与 `docs/faq.md` 增加"运行前把 `AutoTrigger.exe`
   加入杀软排除"的强制步骤；`scripts\Invoke-SampleTest.ps1` 在每轮开始与每个样本前校验
   `Test-Path $AutoTrigger` 且（可选）SHA-256 一致，一旦丢失**立即中止并报错**。
2. **工具侧（建议）**：对二进制做代码签名，或提供官方 SHA-256 供用户加白名单/提交误报。
3. **复测侧**：任何"某轮大量 failed / 无结果"的结论，先检查被测 exe 是否被安全软件移除。

## 六、关闭判据

满足其一即可关闭：

- 在 **开启 Defender 实时保护的干净机器**上、**未加任何排除**直接跑本套件，全程不再触发
  `Trojan:Win32/Bearfoos.B!ml`（工具侧签名/申诉成功）；**或**
- 运行脚本能在被测 exe 消失的**下一个样本前**立即中止，并输出明确的
  `failed: tool_binary_missing`（不再产出 149 行假失败）——此项要复测：
  删除 exe 后重跑，观察脚本是否立刻停止。
