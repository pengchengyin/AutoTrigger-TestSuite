# ISSUE-08｜文件系统快照触达条目/时间预算上限，负向证据被静默禁用（中）

- **严重级别**：中（直接削弱 A29 的反证据判定与 A3 的"未安装"判定）
- **状态**：待修复
- **关联验收项**：A29 ⑤ / F15.2 / F15.8

## 一、问题现象

在一次**普通**目录快照采集时，工具输出：

```text
[警告] 【判定】基线采集告警（...\11-原生导出表(7z).dll）：
       文件系统快照达到条目数或 450ms 预算上限：负向文件计数证据已禁用
```

同时还有一批"访问被拒绝"告警：

```text
[警告] 【判定】基线采集告警（...\10-导出函数库.dll）：C:\Program Files\WindowsApps: open C:\Program Files\WindowsApps: Access is denied.
[警告] 【判定】基线采集告警（...）：C:\ProgramData\Microsoft\Diagnosis: open ...: Access is denied.
[警告] 【判定】基线采集告警（...）：C:\ProgramData\Microsoft\SmsRouter: open ...: Access is denied.
[警告] 【判定】基线采集告警（...）：C:\ProgramData\Microsoft\Windows Defender: open ...: Access is denied.
[警告] 【判定】基线采集告警（...）：C:\ProgramData\Packages: open ...: Access is denied.
```

"负向文件计数证据已禁用"意味着后续**"没有新增文件"**这类否定证据失效，进而影响：

- `N4/N6`（装后回滚、删目录销卸载项）的识别；
- `A29-01/02/05/07/12` 的判定分级；
- `A29-11`（仅非卸载项注册表副作用）这类边界样本。

## 二、证据出处

`evidence\07-group.log`（10:14:08 前后，处理 `10-导出函数库.dll` 时）。

生效配置（`--dump-config`）中的相关阈值：

```json
"install_verify":{"snapshot_depth":2,"snapshot_max_entries":20000,
                  "watch_dirs":["C:\\Program Files","C:\\Program Files (x86)",
                                "%ProgramData%","%LOCALAPPDATA%","%APPDATA%"],
                  "watch_exclude":["%TEMP%","%LOCALAPPDATA%\\Temp",...]}
```

`watch_dirs` 覆盖 `C:\Program Files`、`%ProgramData%`、`%APPDATA%` 等体量很大的目录，`snapshot_depth=2` + 20000 条目 + 450 ms 预算在**没有提权**的前提下必然触顶（大量子目录直接 `Access is denied`）。

## 三、期望行为

1. **不要把"快照不完整"只记成 debug 级告警**：它应当在结果 JSON 里体现（例如 `platform_meta.snapshot_complete=false`，或 `notes` 中声明），让 `install_confidence` 的降级有据可查；
2. **给基线采集一个可配置的更长预算**，或对已知不可读/易变目录（`WindowsApps`、`Defender`、`Packages`、`Diagnosis`）内置排除表，避免每次都在同一批目录上浪费预算；
3. **负向证据缺失时的判定口径要明确**：宁可在该场景下把 `install_completed` 降为 `install_unverified`，也不要悄悄按"没有新增"下结论。
