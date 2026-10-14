# ISSUE-12｜非 MSI 安装器返回 3010（成功但需重启）被判为失败（高）

- **严重级别**：高（把"已经装好、只差重启"的软件误判为失败，并触发 9 次重复安装）
- **状态**：待修复
- **关联验收项**：F15.6 / A2 / A13
- **发现环境**：**已提权**会话（`elevated`），与 ISSUE-01 无关——这条是纯粹的状态码判定缺陷

## 一、问题现象

`samples\18-合成安装器(NSIS)\NSIS-06-需重启-3010.exe`（清单预期：**`install_completed` + `requires_reboot: true`**）实测：

```text
final_status       = install_partial
install_confidence = low
requires_reboot    = false        <-- 应为 true
```

**同一组、同一台机器、同一次运行**里，另外两个"需重启"样本却是对的：

| 样本 | 退出码 / 信号 | 结果 | requires_reboot |
|---|---|---|---|
| `MSI-03-需重启3010.msi` | 3010（被正确识别） | `install_completed` | ✅ true |
| `INNO-08-需重启-返回3010.exe` | exit=null，靠**GUI 关键字**识别 | `install_completed` | ✅ true |
| `NSIS-06-需重启-3010.exe` | **3010（静默路径）** | ❌ `install_partial` | ❌ false |

差异在于**判定路径**：

- MSI 走的是 `msiexec` 专属分支，有 `3010：安装成功，需要重启才能生效` 的映射；
- INNO-08 之所以对，是因为它**没有静默参数**，弹出了含"需要重启"的窗口，被 `buttons.zh-CN.json` 的 `zh_reboot`（`需要重启|需要重新启动`）关键字抓到，于是置了 `requires_reboot`；
- **NSIS-06 用 `/S` 静默运行，没有窗口可抓，只剩退出码 3010 —— 而通用 PE 的静默路径没有把它当成功。**

结论：**"靠窗口关键字"能兜住，但"靠退出码"这条线漏了 3010。**
对真实安装器来说，静默参数命中后本来就没有窗口，所以这条线才是主路径。

## 二、证据

### 2.1 NSIS-06：9 次尝试全部 3010，且每次都拿到 S1+S2

```text
[1] silent_install "/S"                                  exit=3010 artifact=ok
    evidence=["S1|AT Synthetic NSIS 06 Reboot 1.0.0","S2|新增 6 个文件或目录实体","N1|3010"]
[2] silent_install "/VERYSILENT" "/NORESTART" "/SUPPRESSMSGBOXES"  exit=3010
    evidence=["S1|...","S2|新增 6 个文件或目录实体","N1|3010","A2|完成(F)"]
...
[9] no_param_run                                          exit=3010
    evidence=["S1|...","S2|新增 6 个文件或目录实体","N1|3010","A2|完成(F)"]

final: install_partial  low  requires_reboot=false
```

### 2.2 工具其实"认识"3010 —— 但把它记成了 N1

`elevated\18-group.log`：

```text
[信息] 【执行】本轮尝试结束：安装进程已自行退出，退出码=3010，耗时 1.6 秒
[警告] 【判定】证据冲突（N1）：安装进程返回失败退出码 3010：安装成功，需要重启才能生效
```

注意后半句 —— **工具自己写了"3010：安装成功，需要重启才能生效"**，却仍然把它归入 `N1 = failure_exit_code`。日志文案与判定逻辑自相矛盾。

### 2.3 MSI 分支的正确做法（对照组）

`elevated\19-group.log`：

```text
[信息] 【执行】本轮尝试结束：安装进程已自行退出，退出码=3010，耗时 1.1 秒
[信息] 【执行】Windows Installer 退出状态：3010：安装成功，需要重启才能生效
[信息] 【结果】...\MSI-03-需重启3010.msi → 安装成功
```

结果 JSON：``"final_status":"install_completed","requires_reboot":true``。

## 三、期望行为

1. **把 3010 / 1641 提升为全局成功码**（不只 MSI）：`3010 = ERROR_SUCCESS_REBOOT_REQUIRED`、`1641 = ERROR_SUCCESS_REBOOT_INITIATED`。命中时应：
   - 不产生 `N1`；
   - 记 `requires_reboot = true`；
   - **立即停止后续尝试**（当前白跑了 9 次，每次都真的重新安装一遍）。
2. **同理检查其他"非零但成功"的码**：`VERR_...`、Inno 的 `exit code 0/3010/1641`；建议把"成功码集合"做成配置而非硬编码分支。
3. 日志文案与判定必须一致：既然写的是"安装成功"，就不该同时进 N1。

## 四、影响面

所有返回 3010 的 **NSIS / Inno / 厂商安装器**都会被误判为 `install_partial`。

- 现象上：用户看到"部分成功"而不是"安装成功（需重启）"；
- 代价上：每次多跑 8 次重复安装（本例 9 次 × 约 2.5 s + 稳定期）；
- 语义上：`requires_reboot` 漏报会影响后续"重启后继续"的流程。
