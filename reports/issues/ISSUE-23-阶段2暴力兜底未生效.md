# ISSUE-23｜阶段2"暴力兜底"（`fallback_to_brute`）未生效，深层 P5 入口根本没被枚举（高）

- **严重级别**：高（决定"结构不规范的安装包还能不能装上"，直接关系到可安装软件的数量）
- **状态**：待修复
- **关联验收项**：A25 / F17（P5 兜底、`fallback_to_brute`）
- **发现环境**：已提权，样本 `10-入口分层与黑名单\A25-06-阶段2兜底`

## 一、问题现象

样本设计（见清单）：

> `A25-06-阶段2兜底\`：P0–P4 全部失败（`install.bat` 退出 1）→ **回退执行 P5 的 `deep\tools\extra\runtime-helper.exe`**（`fallback_to_brute: true`）

实测结果：

```json
"layout_analysis": { "entries": 6, "fallback_used": false, "skipped_after_success": 0 }
"summary": { "total": 6, "by_status": { "failed": 5, "skipped": 1 } }
```

**P5 的 `runtime-helper.exe` 既没有出现在 `layout_analysis.entries` 里，也没有出现在 `results` 里，
`fallback_used` 恒为 `false`。**

## 二、证据

### 2.1 工具枚举到的入口（只有 6 个，且不含 P5 目标）

```text
vcredist_x64.exe    prio=P3  entry_p3_prereq
install.bat         prio=P0  entry_p0_manifest
install-helper.exe  prio=P1  entry_p1_named
setup.exe           prio=P1  entry_p1_named
MyApp.exe           prio=P4  entry_p4_main
安装说明.txt          prio=P5  non_executable_entry      <-- P5 槽位被一个 .txt 占了
```

### 2.2 但 P5 目标**确实在磁盘上**

```text
A25-06-阶段2兜底\deep\tools\extra\runtime-helper.exe     size=6656  MZ=True  PE=True   <-- 有效 PE
```

注意 `runtime-helper.exe` 是**整个样本里唯一一个真正有效的 PE**：

```text
install-helper.exe   size=514  MZ=True  PE=False   <-- 假 MZ 桩
setup.exe            size=514  MZ=True  PE=False
MyApp.exe            size=514  MZ=True  PE=False
vcredist_x64.exe     size=514  MZ=True  PE=False
install.bat          （脚本，按设计退出 1）
```

也就是说：**P0–P4 是"故意会失败的假 PE"，唯一能装成的就是深层的 P5 目标，而工具恰好把它漏掉了。**

### 2.3 P0–P4 的失败形态（9 次尝试都白跑）

```text
vcredist_x64.exe   att=9  每次都是 fork/exec ...: This version of %1 is not compatible with the
                            version of Windows you're running.  (...其余 3 个 exe 完全相同)
install.bat        att=1  script exit=1
```

顺带一提：对一个 **`MZ=True / PE=False` 的假桩仍然跑满 9 次尝试**（共 4 个文件 × 9 = 36 次无效启动），
说明"文件头声明 MZ 但 PE 签名非法"这一情况没有被提前识别（与 ISSUE-10 同族）。

## 三、根因推断

入口枚举看起来**只扫了浅层目录**（`prefer_shallowest: true`），
把 `deep\tools\extra\runtime-helper.exe` 这种 **3 层深**的条目直接排除了；
而 `fallback_to_brute` 又依赖"已经枚举出来的候选集"，候选集里没有它，兜底自然不可能发生。

同时 `P5` 这个槽位被 `安装说明.txt` 占了——**一个不可执行的 .txt 占据了最高优先级兜底位**，
进一步说明"P5 候选集"的构造方式有问题。

## 四、期望行为

1. **兜底要真的"暴力"**：当 P0–P4 全部失败且 `fallback_to_brute=true` 时，
   应当**不限深度地重新枚举**所有可执行条目（含 `deep\...`），挑出可运行的 PE 去尝试；
   本例至少应把 `runtime-helper.exe` 执行掉。
2. **`fallback_used` 要能反映真实行为**：现在恒为 false，等于这个字段没有信息量。
3. **P5 兜底槽位不要被不可执行条目占据**：`non_executable_entry`（如 `.txt`）不应进入可执行候选集。
4. **假 PE 早退**：`MZ=True 但无 PE 签名` 应在识别阶段就判 `failed: not_a_pe`，
   而不是套 9 次静默参数（4 个文件 × 9 次全是同一个错误）。

## 五、证据文件

| 证据 | 位置 |
|---|---|
| 结果（entries=6 / fallback=false） | `elevated-a25/04-A25-06-阶段2兜底.json` |
| 判定与尝试日志 | `elevated-a25/04-A25-06-阶段2兜底.log` |
| 磁盘树 + PE 头核验 | 见本文 §2.2（`A25-06-阶段2兜底\deep\tools\extra\runtime-helper.exe`） |

## 六、对照：同类场景里**做得对**的部分

同一批实验里，压缩包版的 A25-04 表现良好：

```text
A25-04-规范包压缩版.7z  -> 在解压前就产出 layout_analysis.entries = 51，excluded = 11，
                           解压后 vcredist_x64.exe / install.bat / setup.exe 依次执行，
                           setup.exe -> install_completed
```

说明"先 `7z l` 列清单、再分层选入口"这条主线是通的，**只是"全失败后往下兜底"这一跳断了**。
