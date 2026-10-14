# 环境要求

## 一、必需

| 项 | 要求 | 说明 |
|---|---|---|
| 操作系统 | Windows 10/11 x64 | 本次实测 Windows 11 专业版 build 26300 |
| PowerShell | 5.1+ | 脚本以 UTF-8 **with BOM** 保存，否则中文会乱码 |
| **7-Zip** | 已安装 | 压缩包/ISO 样本必需，缺失时工具退出码 4 |
| AutoTrigger.exe | 由工具作者提供 | 本仓库不含二进制 |
| 管理员权限 | 强烈建议 | 未提权时装不了任何需要管理员的软件 |

## 二、可选

| 项 | 用途 |
|---|---|
| PaddleOCR-json | 16-自绘界面 组；缺失时自绘向导类样本无法自动化 |
| .NET Framework 4 | 仅当你要重新编译 `sources\csharp\` 时 |
| Inno / NSIS / WiX | 仅当你要重新编译合成安装器时（见 sources/BUILD.md） |

## 三、⚠️ 系统变更与风险

跑本套件会**真实修改你的系统**：

| 变更 | 说明 |
|---|---|
| 文件 | 写入 `C:\Program Files\*`、`%LOCALAPPDATA%*`、`C:\ProgramData\*`、`%TEMP%*`、`C:\Users\Public\AT-SENTINEL\*` |
| 注册表 | 写入 `HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\*` 与 `HKCU\...\` 下的 `AT*` 项 |
| 进程 | 启动真实安装器（含 GUI） |
| 输入 | **GUI 自动化会移动鼠标、发送按键**——测试期间不要操作同一桌面 |
| 网络 | 部分样本（Firefox/Zoom/联网等待类）会访问外网 |

## 四、强烈建议

1. 使用**一次性虚拟机**或**可回滚快照**，每次开跑前快照。
2. **不要在日常办公电脑跑全套件。**
3. 跑完后执行清理脚本，或直接回滚快照。
4. GUI 样本运行期间**不要移动鼠标**，否则会干扰自动化。

## 五、UAC / 提权

| 设置 | 本次测试环境 |
|---|---|
| `EnableLUA` | 1 |
| `ConsentPromptBehaviorAdmin` | 0（静默提权，不弹窗） |
| `PromptOnSecureDesktop` | 0 |
| 账户 | 属 Administrators 组 |

> 若你的机器 UAC 会弹窗，请以**管理员身份启动 PowerShell** 再运行脚本，
> 否则需要管理员的样本会失败（脚本会检测并明确提示）。

## 六、交互式桌面

GUI 自动化需要**可交互桌面**：

- 本机/远程桌面登录状态下可用；
- **SSH 会话下不可用**：实测 GUI 向导类样本 `gui_actions=0`，最终 `killed_on_timeout`。
  静默安装、MSI、脚本、压缩包类在 SSH 下**仍可用**。

## 七、建议磁盘空间

| 项 | 空间 |
|---|---|
| 自制样本 | `48 MB |
| 第三方样本（自行下载） | `692 MB |
| 每轮运行产物 | 数 MB（压缩包压力组可达数十 MB） |
| 预留 | **≥ 3 GB** |
