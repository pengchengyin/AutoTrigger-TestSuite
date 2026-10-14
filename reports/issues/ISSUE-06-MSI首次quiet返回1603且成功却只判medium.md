# ISSUE-06｜MSI 首次 `/quiet` 返回 1603，靠 `/passive` 才装成（中）

- **严重级别**：中（首次尝试必然白跑，且给证据集塞进一条 N1）
- **状态**：待修复
- **关联验收项**：A2 / A13 / A29 ②

## 一、问题现象

两个"标准 MSI 安装成功"样本在**未提权**会话下都出现同一模式：

1. 第 1 次尝试 `msiexec /i <pkg> /quiet /norestart /L*v ...` → **退出码 1603**（致命错误）；
2. 第 2 次尝试 `msiexec /i <pkg> /passive /norestart /L*v ...` → **退出码 0**，且拿到 `S1+S2+S3+S4` 全部证据；
3. 最终 `final_status = install_completed`，但**置信度不一致**：

| 样本 | 第 2 次 `artifact_check` | 最终置信度 | 清单预期 |
|---|---|---|---|
| `19-合成安装器(MSI-WiX)\MSI-01-标准安装成功.msi` | `failed` | **medium** | high |
| `03-MSI\putty-64bit-0.85-installer.msi` | `ok` | **high** | high |

## 二、证据（`evidence\19-MSI-01.json`、`evidence\03-putty.json`）

### MSI-01

```text
[1] method=msi cmd="C:\WINDOWS\System32\msiexec.exe" "/i" "...\MSI-01-标准安装成功.msi"
              "/quiet" "/norestart" "/L*v" "%TEMP%\AT-3818527424\MSI-0.log"
    exit=1603  result=exited dur=2.41s  artifact=unknown
    evidence=["N1|1603","B1|安装成功"]
[2] method=msi cmd="C:\WINDOWS\System32\msiexec.exe" "/i" "...\MSI-01-标准安装成功.msi"
              "/passive" "/norestart" "/L*v" "%TEMP%\AT-3818527424\MSI-1.log"
    exit=0     result=exited dur=4.81s  artifact=failed
    evidence=["S1|AT Synthetic MSI 01 1.0.0.0","S2|新增 5 个文件或目录实体","S3|0",
              "S4|11707 [Product: AT Synthetic MSI 01 -- Installation completed successfully. ...]",
              "B1|安装成功"]
final_status=install_completed   install_confidence=medium
```

### putty（同样先 1603 再成功）

```text
[1] "/quiet"   "/norestart"  exit=1603 dur=0.66s  evidence=["N1|1603"]
[2] "/passive" "/norestart"  exit=0    dur=4.35s  artifact=ok
    evidence=["S1|PuTTY release 0.85 (64-bit) 0.85.0.0","S2|新增 11 个文件或目录实体",
              "S3|0","S4|11707 ...","B1|installation completed successfully"]
final_status=install_completed   install_confidence=high
```

### 对照样本的 MSI 定义（`_build\wix\MSI-01-标准安装成功.wxs`）

```xml
<Package Id="*" InstallerVersion="500" Compressed="yes"
         InstallScope="perMachine" InstallPrivileges="elevated" ... />
```

`perMachine + InstallPrivileges="elevated"` 的 MSI 在**未提权**进程里用 `/quiet` 装必然失败（这正是 1603 的来源）；而 `/passive` 会走 Windows Installer 的提权路径——本机 `ConsentPromptBehaviorAdmin=0`，于是**静默提权成功**（见 ISSUE-01 §3.5）。

## 三、期望行为

1. **不要在"已知会失败"的路径上浪费第一次尝试**：既然工具能识别 MSI 的 `perMachine/elevated`（从 MSI 数据库的 `ALLUSERS` / `InstallPrivileges` 属性即可读出），而自身又未提权，就应**先提权**（`runas`）或**直接优先 `/passive`**，而不是先打一发注定 1603 的 `/quiet`。
2. **失败尝试不应污染最终证据**：`N1|1603` 来自一次"参数不对"的尝试，不应与最终判定混在同一证据链里（当前它进了 `install_evidence`，还可能拉低置信度）。建议在证据里区分 `attempt` 作用域。
3. **`artifact_check` 的降级口径要写清楚**：MSI-01 的 medium 完全来自 `artifact_check=failed`（见 ISSUE-11），需要在文档中明确"什么条件下降级"。

## 四、备注

本问题是 ISSUE-01 的连带现象。**工具一旦以管理员身份运行，`/quiet` 首试大概率直接成功**，本条随之消失（已用提权会话复测，见 `测试报告\elevated`）。
