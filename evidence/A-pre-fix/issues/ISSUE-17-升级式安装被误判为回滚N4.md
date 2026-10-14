# ISSUE-17｜"升级式安装"被误判为回滚（N4），且成功后仍重试，最终降级为 `install_partial`（高）

- **严重级别**：高（运行时/依赖包升级是最常见安装形态之一，会被系统性误判）
- **状态**：待修复
- **关联验收项**：A29 ⑤ / F15.3 / N4 / A3
- **发现环境**：已提权，真实软件样本 `04-Burn bootstrapper\VC_redist.x64.exe`

## 一、问题现象

`VC_redist.x64.exe` 第 1 次尝试就**完整成功**：

```text
[1] silent_install  "/quiet" "/norestart"
    exit=0   result=exited   dur=28.8s   artifact=ok
    install_evidence =
      S1|Microsoft Visual C++ 2022 X64 Additional Runtime - 14.44.35211
      S1|Microsoft Visual C++ 2022 X64 Minimum Runtime - 14.44.35211
      S1|Microsoft Visual C++ 2015-2022 Redistributable (x64) - 14.44.35211
      S4|11707 [Product: Microsoft Visual C++ 2022 X64 Minimum Runtime ... Installation completed successfully.]
      S4|11707 [Product: Microsoft Visual C++ 2022 X64 Additional Runtime ... Installation completed successfully.]
      S2|新增 5 个文件或目录实体
      A1|进程正常退出（退出码 0）
      N4|Microsoft Visual C++ 2019 X64 Minimum Runtime - 14.28.29913      <-- 被当成"回滚"
      N4|Microsoft Visual C++ 2015-2019 Redistributable (x64) - 14.28.29913
      N4|Microsoft Visual C++ 2019 X64 Additional Runtime - 14.28.29913
```

结果：

```text
第 1/9 次尝试判定：部分完成（置信度 low）      <-- 明明 S1+S2+S4 全齐
第 2/9 次尝试：/VERYSILENT ... 挂到 278 s 被强杀
final_status = install_partial   install_confidence = low
evidence_conflicts = N4 × 6
```

## 二、根因：把"旧版本被新版本替换"读成了"装完又回滚"

VC_redist（2015-2022 可再发行组件包）是**升级式安装**：
它会**移除旧的 2015-2019 (14.28.29913) 卸载项**并**写入新的 2015-2022 (14.44.35211) 卸载项**。

而 `N4` 的语义是"**已安装的注册表项被移除（疑似回滚）**"，
于是这次**正常的版本替换**被记成 3–6 条 N4，直接把一次成功安装压成 `install_partial / low`。

问题在于：`N4` 只看"ARPS 条目消失"，**没有判断它是否被同族新条目取代**。

## 三、第二个问题：成功后仍然重试

第 1 次尝试已经有 `S1 + S2 + S4`（还带 `artifact=ok`），属于教科书式的成功证据组合，
却因为判定为"部分完成 low"而继续第 2 次尝试；第 2 次挂满 278 s 被强杀，又给结果叠了一层负面。

**重试策略应该由"是否已有 S 级证据"驱动，而不是由"本轮的 N 级计数"驱动。**

## 四、证据文件

- `elevated-real\04-group.json`（VC_redist 的 attempts 与 evidence_conflicts）
- `elevated-real\04-group.log`（`第 1/9 次尝试判定：部分完成（置信度 low）`、`第 2/9 次尝试`）
- MSI 详细日志目录：`elevated-real\04-group-msi-logs\`（如有）

## 五、期望行为

1. **N4 要区分"回滚"与"升级替换"**：若被移除的 ARP 条目与**新增的 ARP 条目**属于同一产品族
   （`DisplayName` 前缀相同、`Publisher` 相同、或 `UpgradeCode` 关联），应判为**升级**而非回滚，
   不产生 N4（或降级为 B 级"版本更替"信息）。
2. **升级应映射到 A3/F15.5**：`MSI-06` 与 `A29-09` 的预期本来就是"覆盖升级 → `install_completed` / `already_installed`"，
   说明设计上认可升级，但 N4 的实现没跟上。
3. **有 S 级证据就不要重试**：第 1 次已拿到 `S1+S2+S4` 时应直接收敛，避免无谓的 278 s。
4. **`evidence_conflicts` 要能自证**：N4 的 detail 只有产品名，建议带上"被谁取代"，
   这样使用者一眼就能看出是升级而不是回滚。

## 六、影响面

这条会影响**所有"先检测旧版 → 卸载/替换旧版 → 安装新版"的安装器**，典型如：

- `VC_redist.x64.exe` / `.NET Runtime` / `DirectX` 等运行库（本样本集 04 组三项里已有两项命中同类形态）；
- 浏览器、驱动、以及任何带 `MajorUpgrade` 的 MSI；
- 用 `PrivilegesRequiredOverridesAllowed` 做就地升级的 Inno 安装器。

后果是：**明明装好了，却被报成"部分成功 low"**，且每次都要多跑一轮可能挂死的重试。
