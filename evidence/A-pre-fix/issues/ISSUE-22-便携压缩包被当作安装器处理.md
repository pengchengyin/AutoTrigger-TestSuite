# ISSUE-22｜便携压缩包被当成安装器：CLI 工具被套 9 种静默参数，常驻 GUI 工具被跑到超时（中）

- **严重级别**：中（不破坏系统，但大量误判 + 每样本白耗 3 分钟）
- **状态**：待修复
- **关联验收项**：F6 / F17 P4-P5 / A3 / F15.8
- **发现环境**：已提权，06 组各压缩包**单独**跑（每包一个进程）

## 一、问题现象

压缩包类样本（便携工具集）里的条目**不是安装器**，但工具一律按"安装器"处理：

| 样本 | 条目 | 实际是什么 | 工具怎么做 | 结果 |
|---|---|---|---|---|
| `nssm-2.24.zip` | `nssm.exe` | 命令行服务管理器 | 套 8 种静默参数 + 无参，共 **9 次** | `install_partial / low` |
| `7z2501-extra.7z` | `7za.exe` / `7zxa.dll` | 7-Zip 命令行工具集 | 9 次 / 3 次 | `install_partial / low` |
| `putty-0.85-w64.zip` | `PAGEANT.EXE` | **常驻托盘程序**（SSH 代理） | 跑起来后一直活着 | `killed_on_timeout` |

### 1.1 CLI 工具：每次都是同一段 Usage

日志证据（`elevated-arch/01-nssm-2.24.log` 第 71–86 行；全部 9 次尝试 stderr 相同）：

```text
[1] /VERYSILENT /NORESTART /SUPPRESSMSGBOXES   exit=1
[2] /S                                          exit=1
[3] /s "/v/qn"                                  exit=1
[4] /quiet /norestart                           exit=1
[5] /silent                                     exit=1
[6] --silent                                    exit=1
[7] --quiet                                     exit=1
[8] -s                                          exit=1
[9] （无参）                                     exit=1

stderr（每次都一样）：
  NSSM: The non-sucking service manager
  Version 2.24 64-bit, 2014-08-31
  Usage: nssm <option> [<args> ...]
```

### 1.2 常驻 GUI 工具：被跑到 180 s 硬超时

```text
PAGEANT.EXE -> killed_on_timeout   attempts=3
```

Pageant 是**托盘常驻程序**，启动后会一直运行，本来就不该"等它结束"。
（在 06 组整体跑那次崩溃前的日志里，还能看到工具反复尝试点击 "Pageant" 窗口的"确定"。）

## 二、对照清单预期

样本清单对这三条的要求都只是"**触发**"级别：

> `nssm-2.24.zip` → 解压后触发内层 `nssm.exe`（P4 主程序）
> `7z2501-extra.7z` → 纯工具集（含 `7za.exe`）
> `putty-0.85-w64.zip` → 便携包，多个 exe → P4/P5 分层

也就是说：**`triggered` 就达标了**，不该走"静默安装参数表 + 安装证据判定"这一整套。

## 三、期望行为

1. **先做"是不是安装器"的家族识别**：解压/目录里的条目应先过 F17 P2 的家族指纹
   （PE 节表 + 字符串：`.itext/`.didata` → Inno，`.ndata` → NSIS，`.wixburn` → Burn …）。
   **识别不出安装器家族时，不要套用静默参数表**，直接无参运行并按 `triggered` 记账。
2. **早退信号**：`退出码≠0 + 耗时≈0 + stderr 含 Usage/usage/--help` 是强"非安装器"信号，应立即收敛，
   不要再试剩下 7 种参数。
3. **常驻程序不要等**：进程存活但**既无安装写入也无向导窗口**时，应在较短时间内判定为
   `triggered`（或 `killed_on_timeout` 但注明"常驻工具"），而不是耗满 `--timeout`。
4. **便携包整体口径**：便携压缩包更适合"分层挑出入口 + 触发 + 记 `triggered`"，
   而不是逐个条目跑判定（本例 `putty` 解出数百个文件，只挑出 `PAGEANT.EXE` 执行，却仍耗 185 s）。

## 四、已确认**正常**的部分（回归时保护）

同一批实验里，**压缩包递归是好的**：

| 样本 | 结果 |
|---|---|
| `嵌套包\01-一层嵌套.7z` | `level4-installer.exe -> install_completed / high` ✅ |
| `嵌套包\02-两层嵌套.zip` | `level4-installer.exe -> install_completed / low` ✅ |

即 F6 的多层递归（默认 3 层）**能到最内层安装器并装成功**，这部分不用动。

## 五、证据文件

| 证据 | 位置 |
|---|---|
| nssm 的 9 次 Usage 退出 | `elevated-arch/01-nssm-2.24.json` / `01-nssm-2.24.log` |
| 7z 工具集的 `install_partial` | `elevated-arch/02-7z2501-extra.json` |
| Pageant 超时 | `elevated-arch/06-putty-0.85-w64.json` |
| 嵌套递归成功 | `elevated-arch/04-01-一层嵌套.json`、`05-02-两层嵌套.json` |

## 六、与其它问题的关系

- S2/N5 证据不可归因的根因见 [ISSUE-21](ISSUE-21-落盘证据无法归因且自相矛盾.md)；
- "解压后无变化仍空转到超时"的 GUI 侧同族问题见 [ISSUE-19](ISSUE-19-重复点击同一控件触顶后空转到超时.md)。
