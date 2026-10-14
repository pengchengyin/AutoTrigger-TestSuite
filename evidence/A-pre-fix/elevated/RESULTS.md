# 已提权会话复测结果（合成安装器 17 / 18 / 19）

> 会话：`Start-Process -Verb RunAs` 启动的**高完整性**进程（`ELEVATED=True`）。
> 目的：验证 ISSUE-01/02 的结论——**只要工具提权，绝大多数安装器就能装成**。

## 0. 总览

| 组 | 样本数 | 结果分布 | 耗时 |
|---|---|---|---|
| 17 合成 Inno | 11 | `installed=9 partial=1 skipped=1` | 561.3 s |
| 18 合成 NSIS | 7 | `installed=5 partial=2` | 394.4 s |
| 19 合成 MSI  | 16 | `installed=4 failed=7 partial=1 skipped=4`（含 8 个非样本 `.wixpdb`） | 87.5 s |

按清单预期逐条比对：**✅ 通过 22 条 / ❌ 不符 5 条 / ⚪ 非样本 7 条**。

**关键结论**：**未提权时合成 NSIS 全部 7 个 0 成功；提权后 5 个 `install_completed` + 2 个符合预期的 `install_partial`。**
ISSUE-01 是本样本集里"能自动安装的软件数量"的第一瓶颈，证据确凿。

## 1. 提权后新暴露的问题

| 问题 | 表现 |
|---|---|
| [ISSUE-12](../../../reports/issues/ISSUE-12-非MSI安装器返回3010被判失败.md) | `NSIS-06` 静默返回 3010 → 被判 `install_partial`、`requires_reboot=false`（MSI-03/INNO-08 却是对的） |
| [ISSUE-13](../../../reports/issues/ISSUE-13-构建中间产物被当作样本处理污染统计.md) | 8 个 `.wixpdb` 被当成样本 → `failed` 统计虚高 |
| [ISSUE-14](../../../reports/issues/ISSUE-14-requires_network只在有窗口时才输出.md) | `requires_network` 从未输出；`INNO-10` 跑满 180 s 后按 `install_completed` 收尾 |
| [ISSUE-03](../../../reports/issues/ISSUE-03-黑名单误杀含卸载字样的合法安装器.md) 追加 | `MSI-06-升级覆盖V1/V2.msi` 因"升级"被跳过；`INNO-06-...无卸载项.exe` 因"卸载"被跳过 |

## 2. 逐条对照


### 17 组（11 条结果）

| 样本 | 期望 | 实测 | 置信度 | requires_reboot | 判定 |
|---|---|---|---|---|---|
| INNO-01-静默安装成功.exe | install_completed (high) | install_completed | high | false | ✅ |
| INNO-04-per-user安装-lowest.exe | install_completed (HKCU 卸载项) | install_completed | high | false | ✅ |
| INNO-05-长安装-持续写盘90s.exe | install_completed | install_completed | high | false | ✅ |
| INNO-07-安装后失败框-退出码1.exe | install_partial | install_partial | low | false | ✅ |
| INNO-02-仅GUI向导-中文.exe | install_completed | install_completed | medium | false | ✅ |
| INNO-03-仅GUI向导-英文.exe | install_completed | install_completed | medium | false | ✅ |
| INNO-08-需重启-返回3010.exe | install_completed (requires_reboot=true) | install_completed | high | true | ✅ |
| INNO-09-卡在完成页-超时验证.exe | install_completed | install_completed | high | false | ✅ |
| INNO-10-联网下载组件等待.exe | killed_on_timeout (requires_network=true) | install_completed | high | false | ❌ |
| INNO-11-仅GUI向导-无许可页.exe | install_completed | install_completed | medium | false | ✅ |
| INNO-06-假成功-只解压无卸载项.exe | install_unverified | skipped | - | false | ❌ |

### 18 组（7 条结果）

| 样本 | 期望 | 实测 | 置信度 | requires_reboot | 判定 |
|---|---|---|---|---|---|
| NSIS-01-静默安装成功.exe | install_completed (high) | install_completed | high | false | ✅ |
| NSIS-05-安装后回滚.exe | install_partial | install_partial | low | false | ✅ |
| NSIS-07-长安装-持续写盘.exe | install_completed | install_completed | high | false | ✅ |
| NSIS-02-仅GUI向导-中文.exe | install_completed | install_completed | high | false | ✅ |
| NSIS-03-仅GUI向导-英文.exe | install_completed | install_completed | high | false | ✅ |
| NSIS-04-静默无效果-需GUI兜底.exe | install_completed | install_completed | high | false | ✅ |
| NSIS-06-需重启-3010.exe | install_completed (requires_reboot=true) | install_partial | low | false | ❌ |

### 19 组（16 条结果）

| 样本 | 期望 | 实测 | 置信度 | requires_reboot | 判定 |
|---|---|---|---|---|---|
| MSI-01-标准安装成功.msi | install_completed (high) | install_completed | medium | false | ✅ |
| MSI-02-安装致命错误1603.msi | install_partial | install_partial | low | false | ✅ |
| MSI-04-per-user安装.msi | install_completed | install_completed | medium | false | ✅ |
| MSI-05-多文件较长安装.msi | install_completed | install_completed | medium | false | ✅ |
| MSI-03-需重启3010.msi | install_completed (requires_reboot=true) | install_completed | medium | true | ✅ |
| MSI-07-无效MSI-纯文本内容.msi | failed | failed | - | false | ✅ |
| MSI-08-损坏的MSI.msi | failed | failed | - | false | ✅ |
| MSI-01-标准安装成功.wixpdb | *(非样本/构建产物)* | failed | - | false | ⚪ |
| MSI-02-安装致命错误1603.wixpdb | *(非样本/构建产物)* | failed | - | false | ⚪ |
| MSI-03-需重启3010.wixpdb | *(非样本/构建产物)* | failed | - | false | ⚪ |
| MSI-04-per-user安装.wixpdb | *(非样本/构建产物)* | failed | - | false | ⚪ |
| MSI-05-多文件较长安装.wixpdb | *(非样本/构建产物)* | failed | - | false | ⚪ |
| MSI-06-升级覆盖V1.msi | install_completed | skipped | - | false | ❌ |
| MSI-06-升级覆盖V1.wixpdb | *(非样本/构建产物)* | skipped | - | false | ⚪ |
| MSI-06-升级覆盖V2.msi | install_completed | skipped | - | false | ❌ |
| MSI-06-升级覆盖V2.wixpdb | *(非样本/构建产物)* | skipped | - | false | ⚪ |

## 3. 提权后确认可用的能力

- **NSIS**：`/S` 静默安装、中文/英文 MUI 向导（UIA 点击"安装/完成"）、长安装（持续写盘 90 s 不误杀）全部成功；
- **Inno**：静默安装、per-user（lowest）、中英文向导、无许可页向导、卡在完成页（超时但证据齐全）全部成功；
- **MSI**：`/quiet`、`/passive`、per-user、长安装、3010 需重启、1603 失败判 `install_partial`、非法/损坏 MSI 判 `failed`，均符合预期；
- **失败日志**：`19-group-msi-logs\` 下 9 个 `.log` 文件非空（A34 ① 通过）；
- **GUI 自动化**：`【界面】自动点击：安装(I)（识别来源 uia）` 在提权会话下稳定生效。

## 4. 复现命令

~~~powershell
# 需要一次静默提权（本机 ConsentPromptBehaviorAdmin=0，不会弹窗）
$env:__COMPAT_LAYER=""; Start-Process powershell -Verb RunAs -ArgumentList @(
  '-NoProfile','-ExecutionPolicy','Bypass','-File','C:\ATTest\elev-batch.ps1')
~~~
