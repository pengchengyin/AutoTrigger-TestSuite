# ISSUE-09｜非法/损坏 MSI 被判 `install_partial`，而清单预期是 `failed`（中）

- **严重级别**：中（判定偏差，会污染统计与置信度）
- **状态**：待修复
- **关联验收项**：A34 ⑥ / F15.3 / N1

## 一、问题现象

`samples\09-类型识别与伪装\OLE头伪msi.msi`（扩展名 `.msi`，实际是 OLE 头，**不是合法 MSI**）实测：

```text
final_status      = install_partial
install_confidence= low
```

而样本清单对该样本的预期是：

> `OLE头伪msi.msi` | OLE 头 | 尝试 msiexec → 非零码 → **`failed`（N1）**

## 二、证据

### 2.1 三次尝试全部返回 1620

```text
msi cmd="C:\\WINDOWS\\System32\\msiexec.exe" "/i" "...\\OLE头伪msi.msi" "/quiet"    "/norestart" "/L*v" "%TEMP%\\AT-...\\MSI-0.log"  exit=1620
msi cmd="C:\\WINDOWS\\System32\\msiexec.exe" "/i" "...\\OLE头伪msi.msi" "/passive"  "/norestart" "/L*v" "%TEMP%\\AT-...\\MSI-1.log"  exit=1620
msi cmd="C:\\WINDOWS\\System32\\msiexec.exe" "/i" "...\\OLE头伪msi.msi"              "/norestart" "/L*v" "%TEMP%\\AT-...\\MSI-2.log"  exit=1620
```

### 2.2 判定证据（`evidence\09-group.json`）

```json
"install_evidence":[
  {"id":"A3","level":"A","type":"filesystem_changed","detail":"监控文件或目录发生变化"},
  {"id":"N1","level":"N","type":"failure_exit_code","detail":"1620"},
  {"id":"A3",...},{"id":"N1","detail":"1620"},
  {"id":"A3",...},{"id":"N1","detail":"1620"}],
"final_status":"install_partial"
```

即：**三条 N1（1620）** 是明确的失败反证据，但被 `A3 "监控文件或目录发生变化"` 抬成了 `install_partial`。

### 2.3 `A3` 从哪来

`A3` 是"监控目录发生变化"，由 `msiexec` 自身的日志/缓存写入触发（`/L*v` 写到 `%TEMP%`，但 msiexec 在 `C:\Windows\Installer`、`ProgramData` 等 `watch_dirs` 内也会留下痕迹）。**这类"工具自己/系统自身的写入"不应算作安装副作用。**

## 三、期望行为

1. **退出码为 1620/1619/1639 等"包本身不可用"类错误**时，不应因 `A3` 升格为 `install_partial`；应判 `failed`（N1），并在 notes 给出中文释义（A34 ⑥ 要求）。
2. **区分"安装器产生的副作用"与"运行环境噪音"**：可对 `msiexec` 自身日志、`C:\Windows\Installer` 缓存、WER/CrashDumps 做定向排除；或把 `A3` 降级为弱证据，仅在"新增实体 ≥ min_new_files 且路径可归因于安装器"时才作为 A 级。
3. 同类样本 `samples\19-合成安装器(MSI-WiX)\MSI-07-无效MSI-纯文本内容.msi`（期望 `failed`，1620）与 `MSI-08-损坏的MSI.msi`（期望 `failed`，1619/1620）**必须一起回归**。

## 四、备注

同一轮里还有更细的问题值得一起看：`11-原生导出表(7z).dll` 经 `rundll32` 探测被访问违例（`3221225477` = `0xC0000005`）杀死，产生的崩溃转储同样落入 `watch_dirs`，把该 DLL 抬成了 `install_partial / low`。
