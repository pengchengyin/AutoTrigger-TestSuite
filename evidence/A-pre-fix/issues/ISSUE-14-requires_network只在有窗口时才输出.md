# ISSUE-14｜`requires_network` 只在"抓得到窗口"时才有：静默路径下永远拿不到（中）

- **严重级别**：中（A15 离线合规字段在静默安装场景缺失；联网等待样本状态也不符预期）
- **状态**：待修复
- **关联验收项**：A15 / F14.4 / INNO-10
- **更正记录**：本条最初写的是"`requires_network` 从未出现"。跑完 `12-超时与活动感知` 后**该结论被推翻**——
  `A30-08` 确实输出了 `requires_network: true`。现按最新证据改写。

## 一、现状（修正后）

| 样本 | 形态 | `requires_network` | 最终状态 |
|---|---|---|---|
| `A30-08-GUI窗口-正在下载组件.exe` | **有窗口**（标题含"正在下载组件"） | ✅ `true` | `killed_on_timeout`（符合预期） |
| `17-...\INNO-10-联网下载组件等待.exe` | **静默运行**（`/VERYSILENT` 无窗口） | ❌ 缺失 | `install_completed`（预期 `killed_on_timeout`） |

- **有窗口**：`platform_meta = {"requires_network": true}` ✅ 实现是对的；
- **静默路径**：拿不到窗口文本，于是这个字段**永远不会被设置**；
- 早先我在 `elevated/*` 与 `evidence/*` 上做过全量检索"0 命中"，
  但那批数据里**没有任何一个样本真正命中过联网窗口**，所以那个"0 命中"是**采样偏差**，不能作为"未实现"的证据。

## 二、`INNO-10` 的问题（仍然成立）

```text
elevated-real/17-group.json
  INNO-10-联网下载组件等待.exe
    final_status = install_completed   conf = high
    platform_meta = {}                       <-- 应含 requires_network: true
    notes = "terminated on timeout; installation evidence still collected"
    attempt[1] silent_install  exit=null  result=killed_on_timeout  dur=180.1s
               err=deadline_or_interrupt  ev=[S1+S2]
    gui = []                                 <-- 没有任何窗口被识别到
```

两个偏差：

1. **`requires_network` 缺失**：静默路径没有窗口可抓，字段就丢了；
2. **最终状态不符**：清单对 `INNO-10` 的预期是 `killed_on_timeout`，实际因"已取得 S1+S2 落盘证据"被判 `install_completed`。

## 三、期望行为

1. **静默路径也要能判联网等待**：除了窗口文本，还应看
   - 进程的输出（stdout/stderr 里的"下载/连接/超时"字样，本例有 `stdout_summary` 可用）；
   - 网络活动（连接建立/等待计数）；
   - 或至少：**长时间停在同一阶段且无落盘增长**时，把 `requires_network` 置为"疑似"而不是丢弃。
2. **字段语义统一**：`A30-08` 走的是 `platform_meta.requires_network`，请确认 INNO-10 也应写在同一位置（当前是彻底缺失，不是写了别的值）。
3. **`INNO-10` 的状态对齐**：如果确实"装了文件但一直等网络"，至少要像 `A30-04` 那样在 notes 里写明"超时终结但已取得安装证据"，
   并在 `requires_network` 上体现差异；否则与"正常装完"无法区分。

## 四、证据文件

| 证据 | 位置 |
|---|---|
| ✅ 有窗口时字段正常 | `elevated-a30/07-A30-08-GUI窗口-正在下载组件.json`（`platform_meta={"requires_network":true}`） |
| ❌ 静默路径字段缺失 | `elevated-real/17-group.json`（INNO-10，`platform_meta={}`） |
| 关键词规则（已备好但只用了一半） | `--dump-resources` 的 `keywords\buttons.zh-CN.json` 中 `{"id":"zh_network","pattern":"正在下载|下载组件|连接服务器|需要联网","action":"network"}` |
