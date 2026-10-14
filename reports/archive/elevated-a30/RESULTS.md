# A30 超时与活动感知（已提权，12 组逐个样本）

> `--timeout 200`，每个样本单独一个进程。`A30-07` / `A30-09`（各 700 s）本轮未跑。

## 0. 结论：7 个样本只有 2 个符合清单预期

| 样本 | 清单预期 | 实测 | 判定 |
|---|---|---|---|
| `A30-01-慢安装器-持续写盘90s` | `install_completed`（不得误杀） | `install_completed / high`，92 s，`term=natural` | ✅ |
| `A30-02-启动后无动作` | `failed: no_activity`（30 s±20 %） | `killed_on_timeout`（干净复现 206 s） | ❌ ISSUE-27 |
| `A30-03-运行中静止` | `killed_on_timeout`（idle 60 s±20 %） | **`install_completed / high`**，172 s | ❌ ISSUE-29 |
| `A30-04-完成安装后卡在完成页` | `install_completed`（+notes） | `install_partial / low`，`ev=[A3]` | ❌ ISSUE-30 |
| `A30-05-联网下载组件等待` | `killed_on_timeout` | `install_partial / low`，200 s | ❌ ISSUE-29 |
| `A30-06-子进程脱离-进程树清理` | `triggered`（且无残留进程） | `install_partial / low`，`term=killed_tree` | ❌ 状态错（**清理对**） |
| `A30-08-GUI窗口-正在下载组件` | `requires_network:true` + 超时 | `killed_on_timeout` + **`requires_network:true`** | ✅ |

## 1. 两个"做对了"的点（回归时保护）

1. **慢安装器不误杀** ✅ —— `A30-01` 总时长 92 s > `idle_timeout_sec=60`，
   但因为"每 3 s 有进展"，被判 `install_completed / high`，`term=natural`（A30 ① 通过）。
2. **进程树清理生效** ✅ —— `A30-06` 任务结束后残留检查为 0：

   ```text
   RESIDUAL_cmd_ping = 0
   A30-06 自带的 residual.txt 内容为空
   ```

   终止动作也确实走了 `graceful → terminated → killed_tree`（`term=killed_tree`），符合 F9.3。

## 2. 本轮新开的条目

- **[ISSUE-27](../../issues/ISSUE-27-启动后无动作从未判定no_activity.md)**（高）：`startup_timeout_sec` 形同虚设，
  `no_activity` 从未判定；本机干净复现 206.4 s。
- **[ISSUE-29](../../issues/ISSUE-29-活动感知超时状态系统性偏差.md)**（高）：静止/等待/子进程脱离的 `final_status` 系统性偏错，
  `A30-03` 甚至被判成 `install_completed / high`。
- **[ISSUE-30](../../issues/ISSUE-30-完成页卡住却判partial未取到安装证据.md)**（高）：`A30-04` 取不到 S1/S2，
  与 `INNO-09` 的正确行为形成矛盾对照。
- **[ISSUE-28](../../issues/ISSUE-28-系统休眠期间计时照算.md)**（低）：机器休眠 7 小时被计入耗时（26118 s）。

## 3. 顺带推翻了 ISSUE-14 的一个结论

`A30-08` 输出了 `platform_meta = {"requires_network": true}` ——
说明 **`requires_network` 是实现了的**，只是**只在能抓到窗口时才设置**。
ISSUE-14 已按新证据改写（"从未输出"→"静默路径拿不到"）。

## 4. ⚠️ 测试环境提醒：本轮有一次真实休眠

`A30-02` 第一次运行期间，机器在 **12:44:12 进入睡眠**（`Kernel-Power` 事件 42），
约 7 小时后唤醒，工具把睡眠时间计入耗时（`26118 s`）。
因此该次的时长数据不可用于断言；本节所有结论均基于**干净复现**（`02b-A30-02-clean`）。
后续做时长类验收时，请确保机器不进入睡眠。

## 5. 复现命令

```powershell
$Exe = "<DESKTOP>\AutoTrigger.exe"
$D   = "<SUITE_ROOT>\samples\12-超时与活动感知"
Get-ChildItem $D -File | Where-Object { $_.Name -notmatch 'A30-(07|09)' } | ForEach-Object {
  & $Exe --input $_.FullName --output ".\$($_.BaseName).json" --timeout 200 --log-level debug --no-lock
}
# 逐样本后检查残留
Get-Process cmd,PING -ErrorAction SilentlyContinue   # 必须为空
```
