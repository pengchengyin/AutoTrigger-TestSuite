# ISSUE-01｜非管理员会话下，请求管理员的安装器全部无法启动（致命）

- **严重级别**：致命（阻断绝大多数真实安装器的自动安装）
- **状态**：待修复
- **关联验收项**：A1 / A11 / F1

## 一、问题现象

在**未提权**的会话中，凡是清单里声明 `requireAdministrator` 的安装器，AutoTrigger 的每一次尝试都在进程创建阶段直接失败，工具把 9 次尝试全部记为「失败」，最终 `final_status = failed`、`install_confidence = null`，且**结果 JSON 里没有任何「需要提权」的可操作结论**。

实测样本：`samples\18-合成安装器(NSIS)\NSIS-01-静默安装成功.exe`（预期 `install_completed / high`）。

## 二、复现步骤

```powershell
cd <DESKTOP>
.\AutoTrigger.exe --input ".\安装包测试\samples\18-合成安装器(NSIS)\NSIS-01-静默安装成功.exe" `
  --output ".\AutoTrigger测试报告\evidence\18-NSIS-01.json" `
  --log-file ".\AutoTrigger测试报告\evidence\18-NSIS-01.log" `
  --timeout 300 --log-level debug
```

## 三、证据

### 3.1 运行日志（每次尝试都是同一个错误）

```text
【执行】第 1/9 次尝试：方法=silent_install，命令="...\NSIS-01-静默安装成功.exe" "/S"
[警告] 【执行】无法启动安装进程（方法=silent_install）：
        fork/exec ...\NSIS-01-静默安装成功.exe: The requested operation requires elevation.
【判定】第 1/9 次尝试判定：失败（置信度 未知）
...
【执行】第 9/9 次尝试：方法=no_param_run，命令="...\NSIS-01-静默安装成功.exe"
[警告] 【执行】无法启动安装进程（方法=no_param_run）：
        fork/exec ...\NSIS-01-静默安装成功.exe: The requested operation requires elevation.
【结果】...\NSIS-01-静默安装成功.exe → 失败
【结果】总体结论：安装失败
```

### 3.2 结果 JSON 片段（`evidence\18-NSIS-01.json`）

```json
"platform_meta":{"administrator":false,"architecture":"amd64",...},
"results":[{
  "final_status":"failed",
  "install_confidence":null,
  "attempts":[
    {"method":"silent_install","exit_code":null,"result":"failed",
     "error":"fork/exec ...\NSIS-01-静默安装成功.exe: The requested operation requires elevation."},
    "... 共 9 条，error 完全相同 ..."
  ]
}]
```

### 3.3 会话权限实测

```text
User: <HOST>\<USER>
IsAdmin(role): False
Mandatory Label\Medium Mandatory Level   S-1-16-8192
BUILTIN\Administrators   Alias   Group used for deny only   S-1-32-544
```

账户在 Administrators 组内，但令牌被 UAC 过滤（"Group used for deny only"），进程处于 Medium IL。

### 3.4 工具自身没有声明提权

对 `AutoTrigger.exe` 二进制检索清单关键字（ASCII 与 UTF-16 两种编码都试过），**完全不存在**：

```text
requestedExecutionLevel : -1
asInvoker               : -1
requireAdministrator    : -1
highestAvailable        : -1
```

`--capabilities` 自检也明确给出告警：

```text
[警告] 【任务】环境提示：建议以管理员身份运行：当前进程未提权，即使账户属于 Administrators
也可能是标准权限。系统级安装与 HKLM 采证可能不完整；……
```

### 3.5 ★ 本机可以**静默提权**——修复成本极低

本机 UAC 策略（`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System`）：

```text
EnableLUA                  : 1
ConsentPromptBehaviorAdmin : 0      <-- "Elevate without prompting"（不弹 UAC 直接提权）
PromptOnSecureDesktop      : 0
```

且 `<USER>` 属于本机 Administrators 组。实测用 `Start-Process -Verb RunAs` **完全无声地**拿到了提权进程：

```text
launching elevated...
launcher exit=0
--- result ---
ELEVATED=True USER=<HOST>\<USER>
```

也就是说：**本机根本不需要用户点任何东西**，只要工具改用 `ShellExecuteEx(verb="runas")`，`ERROR_ELEVATION_REQUIRED` 就能被静默化解。

## 四、期望行为

1. **子进程按需提权**（最小改动、收益最大）：捕获 `ERROR_ELEVATION_REQUIRED` 后，改用 `ShellExecuteEx` + `runas` 启动，而不是 `CreateProcess`。
2. **启动自举提权**：清单改为 `requestedExecutionLevel level="requireAdministrator"`，或启动时检测到需要提权即用 `runas` 重新拉起自身（保留 `--no-elevate` 开关）。
3. **失败要能自我解释**：即使不自动提权，也应在结果里给出专属状态与中文提示（例如 `failed: requires_elevation`），而不是把 9 次尝试记成同样的「失败」让使用者自己猜。

## 五、影响面

`samples` 中合成 NSIS 全部 7 个、以及所有声明 `requireAdministrator` 的真实安装器在未提权会话下**一个都装不上**。这是当前"能自动安装的软件数量"的首要瓶颈。
