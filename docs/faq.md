# FAQ

**Q1. 为什么没有"总成功率"？**
A. 因为测试跨 3 个工具构建、2 种权限上下文，从没在同版本下跑完全部样本。
混合统计会得出无意义的数字。请按 [reports/summary.md](../reports/summary.md) 的分段引用。

**Q2. `install_unverified` 到底是成功还是失败？**
A. 都**不是**。它表示"流程正常但**没拿到安装证据**"。本项目不把它算成功。

**Q3. 退出码 0 为什么不算安装成功？**
A. 大量安装器的"假成功"就是退出码 0 但什么都没装（样本 A29-01/A29-02 专门测这个）。

**Q4. 为什么 `skipped` 不算进分母？**
A. `skipped` 是"未执行"（空文件、无宿主、命中黑名单），不构成安装能力的证据。
把它放进分母会人为压低成功率，放在分子里更是错的。

**Q5. 为什么第三方安装包不放进仓库？**
A. 两个原因：体积（692 MB）与**再分发许可**。其中 Zoom/MobaXterm/TeraCopy/VeraCrypt 等是专有 EULA。
详见 [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)。

**Q6. 那 8 个没有下载地址的样本怎么办？**
A. 原始下载脚本没登记来源，我们在清单里**如实标注"未提供"**，不猜 URL。
你可以从厂商官网取对应版本，再用 SHA-256 核对。

**Q7. 我能直接在办公电脑上跑吗？**
A. **不建议。** 套件会真实安装软件、写注册表、动鼠标键盘。请用一次性虚拟机或可回滚快照。

**Q8. 一定要管理员权限吗？**
A. 建议要。未提权时结果 JSON 里 `platform_meta.administrator=false`，
需要管理员的安装器会失败，得到的结果**不代表工具能力**。

**Q9. 跑失败了怎么排查？**
A. 看 `runs\<时间戳>\` 下的三件套：结果 JSON（状态与证据）、`*.log`（工具决策过程）、
`*.console.txt`（原始输出）。再用 [scripts/Compare-Results.ps1](../scripts/Compare-Results.ps1) 与已知基线对比。

**Q10. 结果和预期不符，是工具的问题还是套件的问题？**
A. 先确认三件事：权限是否一致、清理脚本是否跑过、样本 SHA-256 是否匹配。
状态残留（没清理）是**最常见**的假失败原因。

**Q11. OCR 显示 `startup_failed` 影响大吗？**
A. 只影响 16-自绘界面 组。其他组不依赖 OCR。报告里遇到这种轮次会把该组结论标为不可靠。

**Q12. 能通过 SSH 远程跑吗？**
A. 静默安装 / MSI / 脚本 / 压缩包类**可以**；**GUI 向导类不行**（实测 `gui_actions=0`）。
另外 SSH 管理员会话本身就是提权的。

**Q13. 样本文件名看起来像病毒（`uninstall.exe`、`卸载.exe`）？**
A. 那是**黑名单测试桩**，3–4 KB 的惰性程序，源码在 `sources\csharp\`。
作用正是验证工具的黑名单有没有生效。可能触发杀软误报，属已知特性。

**Q14. 我怎么复现你的结论？**
A. 三步：① [scripts/Get-SampleManifest.ps1](../scripts/Get-SampleManifest.ps1) 校验样本；
② [scripts/Invoke-SmokeTest.ps1](../scripts/Invoke-SmokeTest.ps1) 跑冒烟；
③ 需要完整覆盖时先 [scripts/Get-ThirdPartySamples.ps1](../scripts/Get-ThirdPartySamples.ps1) 取第三方样本。

**Q15. 跑着跑着大量样本「秒失败 / 无结果」，怎么排查？**
A. 先确认**被测工具是否还在**：安全软件（尤其 Windows Defender）可能在运行中把
`AutoTrigger.exe` 隔离，之后每个样本的 `cmd.exe` 都会直接报「系统无法执行指定的程序」。
用 `Get-MpThreatDetection` 确认、`MpCmdRun.exe -Restore` 还原，并把 `AutoTrigger.exe`
加入排除；批量运行前也应先加排除。详见
[reports/issues/ISSUE-36](issues/ISSUE-36-Defender隔离AutoTrigger致整轮中断.md)。

