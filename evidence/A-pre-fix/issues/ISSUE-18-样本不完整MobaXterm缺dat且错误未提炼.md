# ISSUE-18｜样本不完整（MobaXterm MSI 缺 `.dat`）导致必然失败；且工具未把 MSI 日志里的关键错误提炼出来（中）

- **严重级别**：中（一半是**样本集缺陷**，一半是**失败可诊断性**不足）
- **状态**：待处理
- **关联验收项**：A34 ⑥（失败可诊断性）
- **发现环境**：已提权，样本 `03-MSI\MobaXterm_installer_26.5.msi`

## 一、问题现象

`MobaXterm_installer_26.5.msi` 三次尝试全部失败，最终 `install_partial / low`（清单预期 `install_completed`）：

```text
[1] msi "/quiet"   "/norestart"                exit=1603  dur=12.2s
    ev=["N1|1603"]
[2] msi "/passive" "/norestart"                exit=1603  dur=5.7s   artifact=failed
    ev=["A3|监控文件或目录发生变化","N1|1603"]
[3] msi "/norestart"  （无静默参数，走完整 UI）  exit=null  result=killed_on_timeout  dur=252.3s
    ev=["N6|新增目录在稳定期消失，疑似回滚" ×2, "A3|..."]
final_status = install_partial   install_confidence = low
```

## 二、根因（来自工具自己保存的 MSI 详细日志）

`elevated-real\03-group-msi-logs\MobaXterm_installer_26.5-1-msi.log`：

```text
MSI (s) (34:98) [11:14:11:970]: Product: MobaXterm --
  Error 1308. Source file not found:
  <SUITE_ROOT>\samples\03-MSI\MobaXterm_installer.dat.
  Verify that the file exists and that you can access it.
Action ended 11:14:11: InstallFinalize. Return value 3.
MSI (s) (34:98) [11:14:12:089]: Product: MobaXterm -- Installation failed.
MSI (c) (B8:9C) [11:14:14:405]: MainEngineThread is returning 1603
```

**`Error 1308：源文件缺失`** —— 这个 MSI 用了**外部数据文件** `MobaXterm_installer.dat`，
但样本目录 `samples\03-MSI\` 里**只有 .msi，没有 .dat**（见下方目录清单）。

也就是说：**无论工具怎么努力，这个样本都不可能装成功**。清单里给它写的"预期 `install_completed`"是错的。

## 二之二、★ 交叉验证：打包版能装成，证实是样本缺文件

同一个软件的**压缩包版本** `MobaXterm_Installer.zip` 里**同时包含** `MobaXterm_installer_26.5.msi`
**和** `MobaXterm_installer.dat`。把它单独跑一遍：

```text
elevated-arch/08-MobaXterm_Installer.json
  MobaXterm_installer_26.5.msi  -> install_completed / high      <-- 装成了
  MobaXterm_installer.dat       -> triggered
  MobaXterm_Installer.zip       -> install_completed
```

**同一个 MSI：单独跑（缺 .dat）报 Error 1308 失败；从压缩包里跑（有 .dat）就装成功。**

这就把"`03-MSI` 目录里的样本不完整"这件事**钉死**了——不是工具或 MSI 的问题，
而是 `samples\03-MSI\` 少放了一个文件。

## 三、两件事要分开处理

### 3.1 样本侧（主要）

- 补齐 `MobaXterm_installer.dat`（与 .msi 同级），或换用 MobaXterm 官方**完整安装器**；
- 顺带说明：`.msi` 依赖的外部文件不是个例，建议在样本清单里给这类"多文件 MSI/安装器"加一个"必须同目录存在"的备注。

### 3.2 工具侧（失败可诊断性，A34 ⑥）

工具的 `install_evidence` 只留下 `N1|1603`，而**真正的根因（Error 1308、缺失的文件名）就在它自己保存的 MSI 日志里**。
建议：

1. 从 `MSI-n.log` 中提炼关键行（`Error 1\d{3}`、`Return value 3`、`Action ended ... InstallFinalize`）放进结果
   （例如 `attempts[].msi_log_summary` 或 `failure_reason`），而不要只给一个 1603；
2. 对 1603 做二级归因（"缺少源文件 1308" / "权限不足 1925" / "自定义动作失败"），
   这样使用者不必翻 `%TEMP%` 日志就能定位；
3. 已有 `<结果名>-msi-logs\` 目录是很好的基础设施（9 个非空日志已确认），把**摘要**回填进 JSON 即可。

## 四、证据文件

- `elevated-real\03-group.json`
- `elevated-real\03-group-msi-logs\MobaXterm_installer_26.5-1-msi.log`（Error 1308）
- `<SUITE_ROOT>\samples\03-MSI\` 目录清单（无 .dat）

## 五、同组顺带发现

同组的 `7z2600-x64.msi` 拿到 `S1+S3+S4`（msiexec 报成功、ARP 有条目）却 **没有 S2（无落盘）**，
`artifact_check=failed`，置信度只有 `medium`。查证：`C:\Program Files\7-Zip` **不存在**，
全盘也没找到新装的 `7z.exe`；而机器上已有一个"7-Zip 26.03"注册在 `third_party\7zip\7-Zip\`。
这一条**需要人工确认**是"MSI 与既有 7-Zip 冲突/被 MajorUpgrade 处理"还是"工具漏采了落盘证据"，
暂不单列问题，但与 ISSUE-11（`artifact_check` 口径）是同一类。
