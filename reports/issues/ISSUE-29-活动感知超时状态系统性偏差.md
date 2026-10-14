# ISSUE-29｜活动感知超时的 `final_status` 系统性偏差：静止/等待/子进程脱离都被抬成 `install_partial` 或 `install_completed`（高）

- **严重级别**：高（把"没装成/在等待"报成"装成/部分成功"，直接影响安装结果可信度）
- **状态**：待修复
- **关联验收项**：A30 ②③⑤ / F9
- **发现环境**：已提权，`12-超时与活动感知` 逐个样本跑（`--timeout 200`）

## 一、总览：7 个样本只有 2 个符合预期

| 样本 | 清单预期 | 实测 | 结论 |
|---|---|---|---|
| `A30-01-慢安装器-持续写盘90s` | `install_completed`（不得误杀） | `install_completed / high`，92 s，`term=natural` | ✅ |
| `A30-02-启动后无动作` | `failed: no_activity`（30 s ±20 %） | `killed_on_timeout`（干净复现 206 s） | ❌ ISSUE-27 |
| `A30-03-运行中静止` | `killed_on_timeout`（idle 60 s ±20 %） | **`install_completed / high`**，172 s | ❌ 本条 |
| `A30-04-完成安装后卡在完成页` | `install_completed`（+notes） | `install_partial / low`，`ev=[A3]` | ❌ ISSUE-30 |
| `A30-05-联网下载组件等待` | `killed_on_timeout` | `install_partial / low`，200 s | ❌ 本条 |
| `A30-06-子进程脱离-进程树清理` | `triggered`（且无残留进程） | `install_partial / low`，`term=killed_tree` | ❌ 本条（**清理本身是对的**） |
| `A30-08-GUI窗口-正在下载组件` | `requires_network:true` + 超时 | `killed_on_timeout` + `requires_network:true` | ✅ |

## 二、三条偏差的共同点：无关的 `A3` 把状态"抬"上去

```text
A30-03  install_completed / high    ev=[S2]        172s   （预期 killed_on_timeout）
A30-05  install_partial   / low     ev=[A3]        200s   （预期 killed_on_timeout）
A30-06  install_partial   / low     ev=[A3]        200s   （预期 triggered）
```

- `A30-03`「运行中静止」按设计**只写 `%TEMP%`**（清单原文），却出现 `S2|新增文件`，
  于是被判成 `install_completed / high`——**这是最危险的一条：一个静止的进程被报成"安装成功"**；
- `A30-05` / `A30-06` 都只有一条无来源的 `A3|监控文件或目录发生变化`，
  不足以证明安装，却把 `failed/killed` 抬成 `install_partial`。

这是 [ISSUE-21](ISSUE-21-落盘证据无法归因且自相矛盾.md)（证据不可归因）在 **A30 判定上的直接后果**：
`S2/A3` 的取值决定了最终状态，而它们的来源无人能证。

## 三、`A30-03` 的第二个问题：终止耗时 172 s，远超配置

清单要求"在 `idle_timeout_sec` 60 s（±20 %，即 48–72 s）内进入终止流程"。
实测三次尝试合计 **172 s**（`term=graceful`），单次最长超过 72 s 上限。
与 ISSUE-27 §2.2 里 `A30-02` 的 123 s 是同一现象：**静默期之后还挂着一大段未被文档覆盖的收尾逻辑**。

## 四、`A30-06` 的"一半是对的"要明确记下来

`A30-06` 的**进程树清理是达标的**：

```text
任务结束后的残留检查：RESIDUAL_cmd_ping = 0
（A30-06 自带 residual.txt 内容为空）
```

也就是说 F9.3 的 `graceful → terminated → killed_tree` 这串终止动作**起作用了**（`term=killed_tree`）。
问题只在**状态判定**：父进程按设计 8 s 就退出了，工具仍在等那个"脱离的子进程"，
最后记成 `killed_on_timeout / install_partial`，而清单只要求 `triggered`。

> 这属于 [ISSUE-15](ISSUE-15-安装后拉起的应用窗口被持续自动化至硬超时.md) 同族：
> **该结束的时候不结束**（等一个本就不该等的进程）。

## 五、期望行为

1. **无关证据不得抬高状态**：`A3` 单独存在时不应把 `killed_on_timeout` 变成 `install_partial`；
   `S2` 必须先证明"可归因于本次安装进程树"（ISSUE-21）；
2. **"静止/等待"要有专属终态**：`A30-03` 应 `killed_on_timeout`、`A30-05` 应 `killed_on_timeout`、
   `A30-06` 应 `triggered`（父进程退出即视为完成，子进程清理另行记录）；
3. **`idle_timeout` 的收尾时长要可解释**：把 `settle_sec / quiet_polls / settle_max_sec` 的真实合计写进文档，
   或把总时长纳入 `idle_timeout` 预算。

## 五之二、长样本补测：`A30-07` 通过 ✅，`A30-09` 又被 `S2` 抬错 ❌

用 `--timeout 600` 单独跑两个 700 s 长样本：

| 样本 | 清单预期 | 实测 | 判定 |
|---|---|---|---|
| `A30-07-超长安装-持续700s` | 600 s 硬上限终止；已落盘可并判 `install_completed`；`termination_mode` 有值 | `install_completed / high`，`dur=599.5s`（墙钟 604.9 s），`term=graceful`，notes 正确 | ✅ |
| `A30-09-超长安装-只在TEMP写盘700s` | **`killed_on_timeout`** | **`install_partial / low`**，`dur=599.8s`，`ev=[S2|新增 5 个文件]` | ❌ |

**`A30-07` 做得很好**：正好在 600 s 处终止，`termination_mode` 有值，notes 明确写"超时终结但已取得安装证据"。

**`A30-09` 又栽在同一条上**：attempt 级结果确实是 `killed_on_timeout`（正确），
但最终 `final_status` 因为一条 **`S2|新增 5 个文件或目录实体`** 被抬成 `install_partial`。
而该样本按设计**只写 `%TEMP%`**——`%TEMP%` 本应在 `watch_exclude` 里。
这正是 ISSUE-21（证据不可归因）与本节 §二 完全相同的形态；
清单安排 `A30-07/09` 成对存在，本意就是要证明"有落盘/无落盘走不同判定"，而 `S2` 的误报把这个对照毁掉了。

> 注：`A30-07` 的 `S2=842 个文件` 是**真实落盘**（它就该装到 `Program Files`），
> `A30-09` 的 `S2=5 个文件` 则是 `%TEMP%` 里的东西。**两者都是 `S2`，但真伪完全不同**——
> 这就是"证据必须带路径"的最直接例证。

## 六、证据文件

| 样本 | 位置 |
|---|---|
| A30-03 | `elevated-a30/03-A30-03-运行中静止.json` |
| A30-05 | `elevated-a30/05-A30-05-联网下载组件等待.json` |
| A30-06（含 residual） | `elevated-a30/06-A30-06-子进程脱离-进程树清理.json` / `-residual.txt` |
| A30-08（通过） | `elevated-a30/07-A30-08-GUI窗口-正在下载组件.json` |
