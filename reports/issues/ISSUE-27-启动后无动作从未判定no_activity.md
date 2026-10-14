# ISSUE-27｜`A30-02`「启动后无动作」从未被判 `no_activity`，一路耗到硬超时（高）

- **严重级别**：高（"卡死的安装器"无法尽早识别，直接吃掉单文件硬超时，拖垮批量吞吐）
- **状态**：待修复
- **关联验收项**：A30 ② / F9 / `startup_timeout_sec`
- **发现环境**：**干净复现**（机器处于唤醒状态，无休眠干扰）

## 一、问题现象

清单要求：

> `A30-02-启动后无动作.exe` → **`failed: no_activity`**，在 `startup_timeout_sec` 30 s（±20 %）内判定

实测（`--timeout 200`，单跑，总耗时 **206.4 s**）：

```text
final_status = install_partial   install_confidence = low

attempt[1]  exit=null  result=killed_on_timeout  dur=123.1s  err=idle_timeout  ev=[A3]
attempt[2]  exit=null  result=killed_on_timeout  dur= 64.7s  err=idle_timeout  ev=[A3]
attempt[3]  exit=null  result=...  dur=  1.5s   err=deadline_or_interrupt  ev=[A3]
```

**没有出现 `no_activity`，也没有在 30 s 级别收敛**；第 1 次尝试甚至跑了 **123.1 s**。

## 二、两个具体缺陷

### 2.1 `startup_timeout_sec` 形同虚设

日志里 30 秒粒度的探针（来自受污染的第一次运行，形态相同）：

```text
[信息] 【执行】执行等待中：已用时 31 秒，无进展 5 秒，最近信号=filesystem_registry，监控PID=[5496]
[信息] 【执行】执行等待中：已用时 61 秒，无进展 35 秒，最近信号=filesystem_registry，监控PID=[5496]
[信息] 【执行】执行等待中：已用时 91 秒，无进展 23 秒，最近信号=filesystem_registry，监控PID=[5496]
```

- 31 s 时"无进展"只有 5 s——因为被 `filesystem_registry` 信号不断重置；
- 该样本按设计**什么都不做**，这些 I/O 信号几乎必然来自**无关进程**（与 ISSUE-21 同源）；
- 于是 `startup_timeout_sec = 30` 永远等不到，只能靠更晚的 idle/hard 超时兜。

### 2.2 `idle_timeout_sec = 60` 也被超出

第 1 次尝试 `dur = 123.1 s`，约为配置值（60 s）的 **2 倍**。
若按 A30-03 的口径"应在 `idle_timeout_sec` 60 s（±20 %，即 48–72 s）内进入终止流程"，
**123.1 s 明显越界**——说明静默期判定后面还挂了一段更长的收尾/稳定期逻辑，没有被文档覆盖。

### 2.3 顺带：又出现了无来源的 `A3`

三条 attempt 的证据都是 `A3|监控文件或目录发生变化`，
而这个样本按设计**不写任何文件**。这条 `A3` 又把结果从 `failed` 抬成了 `install_partial`（ISSUE-25 的同一形态）。

## 三、期望行为

1. **`startup_timeout_sec` 要真的生效**：进程启动后若在 `startup_timeout_sec` 内**没有可归因于该进程的**活动，
   直接判 `failed: no_activity`，不要等到 idle/hard 超时。
2. **活动信号必须可归因**：`filesystem_registry` 这类系统级信号不应重置静默计时——
   至少要能区分"该进程树自己的 I/O"与"全局系统 I/O"（这与 ISSUE-21、ISSUE-08 是同一个根因）。
3. **`idle_timeout` 的语义要写清**：静默期 + 稳定期（`settle_sec` / `quiet_polls` / `settle_max_sec`）到底合计多少，
   文档与实现要对齐；若确实是 60 s，就不该出现 123 s。
4. **`no_activity` 要有专属 final_status**（清单用的是 `failed: no_activity`），便于区分"启动即死"和"跑着超时"。

## 四、证据文件

| 证据 | 位置 |
|---|---|
| **干净复现**（206.4 s） | `elevated-a30/02b-A30-02-clean.json` / `02b-A30-02-clean.log` |
| 受污染运行（含休眠） | `elevated-a30/02-A30-02-启动后无动作.json` |
| 配置 | `--dump-config` 的 `startup_timeout_sec=30`、`idle_timeout_sec=60`、`settle_sec/quiet_polls/settle_max_sec` |
