# F13 静默参数探测（20 组）· 已提权

> 三个探测桩逐个单跑；每个桩运行前后会清空/抓取 `C:\Users\Public\AT-SENTINEL\f13-argv.log`，
> 因此下面每份 argv 都是**该次运行真实收到的完整命令行序列**。

## 0. 结论：F13 的核心断言**全部通过** ✅

| 样本 | 清单预期 | 实测 | 判定 |
|---|---|---|---|
| `F13-参数探测桩-记录全部尝试.exe` | 按 F13 参数表顺序出现 9 条，最后一条是无参数 | **9 条，顺序完全吻合** | ✅ |
| `F13-参数探测桩-见VERYSILENT即成功.exe` | 只应出现 **1 行** | **恰好 1 行** | ✅ |
| `F13-参数探测桩-只认NSIS的S.exe` | 先试 Inno（未命中）→ 再试 `/S`（命中）→ 停止 | **恰好 2 行** | ✅ |

## 1. 原始 argv 证据（逐字复制）

### 1.1 `记录全部尝试` —— 9 次，顺序与 F13 表一致

```text
12:21:06.624  [静默参数]  /VERYSILENT /NORESTART /SUPPRESSMSGBOXES     <- ① Inno
12:21:12.003  [静默参数]  /S                                            <- ② NSIS
12:21:17.261  [静默参数]  /s /v/qn                                      <- ③ InstallShield
12:21:22.427  [静默参数]  /quiet /norestart                             <- ④ WiX / MSI
12:21:27.560  [静默参数]  /silent                                       <- ⑤ 通用
12:21:32.945  [静默参数]  --silent
12:21:38.251  [静默参数]  --quiet
12:21:43.741  [静默参数]  -s
12:21:49.082  [无参数/GUI]                                              <- ⑥ 无参数运行
```

与 `--dump-resources` 导出的 `params\silent_params.windows.json` 完全一致：

```json
[{"id":"inno","args":["/VERYSILENT","/NORESTART","/SUPPRESSMSGBOXES"]},
 {"id":"nsis","args":["/S"]},
 {"id":"installshield","args":["/s","/v/qn"]},
 {"id":"wixburn","args":["/quiet","/norestart"]},
 {"id":"generic_silent","args":["/silent"]},
 {"id":"generic_long_silent","args":["--silent"]},
 {"id":"generic_quiet","args":["--quiet"]},
 {"id":"generic_short_silent","args":["-s"]}]
```

### 1.2 `见VERYSILENT即成功` —— 提前结束生效（F13 ⑤）

```text
12:22:04.303  [命中 /VERYSILENT]  /VERYSILENT /NORESTART /SUPPRESSMSGBOXES
```

**只有 1 行**——第一次尝试就拿到成功证据，后面 8 种参数一个都没试。

### 1.3 `只认NSIS的S` —— 顺序正确，不是"只试一种"

```text
12:22:14.059  [未命中]  /VERYSILENT /NORESTART /SUPPRESSMSGBOXES
12:22:19.215  [命中 /S] /S
```

**恰好 2 行**：先按顺序试 Inno 参数（未命中）→ 再试 `/S`（命中）→ 立即停止。

## 2. 最终状态对照

| 样本 | 清单预期 | 实测 | 备注 |
|---|---|---|---|
| `记录全部尝试` | `failed` / `triggered` | `install_partial / low` | ⚠️ 小偏差，见下 |
| `见VERYSILENT即成功` | `install_completed` | `install_completed / medium` | ✅ |
| `只认NSIS的S` | `install_completed` | `install_completed / medium` | ✅ |

### 关于"记录全部尝试"的 `install_partial`

该桩 9 次尝试全部 `exit=1`（它本来就是"全部失败"的桩），最终证据为 `[S2+N1]`：

```text
[1..8] silent_install exit=1
[9]    no_param_run  exit=1
evidence = S2|新增 … 个文件或目录实体 + N1
final_status = install_partial / low
```

按清单它应为 `failed` / `triggered`。这里被一条 `S2`（"新增文件"）抬成了 `install_partial`——
**又是 ISSUE-21 的同一形态**（探测桩本身只写哨兵日志，`S2` 的来源无法归因）。
不影响 F13 的参数顺序结论，但再次说明 **`S2` 的可归因性**是关键。

## 3. 证据文件

| 证据 | 位置 |
|---|---|
| 三次运行的 argv 全量 | `elevated-f13/01-…-f13argv.log`、`02-…`、`03-…` |
| 结果 JSON | `elevated-f13/01-….json` … `03-….json` |
| 参数表定义 | `--dump-resources` → `params\silent_params.windows.json` |
