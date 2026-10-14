# 阶段一：目录清单、整理方案与「不适合公开」清单

> 本文件是 **实施前** 的评估记录。原始目录 `<DESKTOP>\<USER>\Desktop\安装包测试` **未被修改**，
> 发布内容全部落在旁边的新目录 `<DESKTOP>\<USER>\Desktop\AutoTrigger-TestSuite`。

## 一、目录清单（实测）

### 1.1 `安装包测试` 顶层

| 条目 | 类型 | 文件数 | 体积 | 用途 | 可否公开 |
|---|---|---|---|---|---|
| `samples\` | 目录 | 277 | 740.1 MB | 20 组测试样本 | **部分**（见 1.2） |
| `_build\` | 目录 | 137 | 1 MB | 自制样本源码 + 生成脚本 | ✅ 可（需脱敏） |
| `_toolchain\` | 目录 | 792 | **206.3 MB** | 第三方编译器（Inno/NSIS/WiX/choco） | ❌ **不可** |
| `_trap\` | 目录 | 12 | 0.1 MB | 黑名单陷阱（自制） | ⚠️ 需警示后发布 |
| `README.md` | 文件 | - | 4 KB | 样本集说明 | ✅（需重写） |
| `_cleanup.ps1` | 文件 | - | 5 KB | 清理合成样本痕迹 | ✅ |
| `_run_tests.ps1` | 文件 | - | 4 KB | 分组批量跑 | ✅（需核对 CLI 契约） |
| `测试样本清单.md` | 文件 | - | 31 KB | 逐样本预期结果 ↔ PRD 验收项 | ✅（脱敏后） |
| `results\` | — | — | — | **不存在**（尚未归档过结果） | — |

### 1.2 `samples\` 分组（含「自制 / 真实第三方」区分）

| 组 | 文件数 | 体积 | 性质 | 可否公开 |
|---|---|---|---|---|
| 01-Inno Setup | 5 | 139.8 MB | **真实第三方** | ❌ 仅登记链接 |
| 02-NSIS | 5 | 117.0 MB | **真实第三方** | ❌ 仅登记链接 |
| 03-MSI | 6 | 102.9 MB | **真实第三方** | ❌ 仅登记链接 |
| 04-Burn bootstrapper | 3 | 107.3 MB | **真实第三方** | ❌ 仅登记链接 |
| 05-其它厂商安装器 | 3 | 166.3 MB | **真实第三方** | ❌ 仅登记链接 |
| 06-压缩包 | 8 | 58.3 MB | **真实第三方** | ❌ 仅登记链接 |
| 07-脚本与快捷方式 | 16 | 1.8 MB | 自制 | ✅ |
| 08-文档类 | 8 | <0.1 MB | 自制 | ✅ |
| 09-类型识别与伪装 | 13 | <0.1 MB | 自制 | ✅ |
| 10-入口分层与黑名单 | 76 | 1.8 MB | 自制 | ✅ |
| 11-安装成功判定 | 13 | 0.1 MB | 自制 | ✅ |
| 12-超时与活动感知 | 9 | 0.1 MB | 自制 | ✅ |
| 13-光盘映像 ISO | 10 | 10.9 MB | 自制 | ✅ |
| 14-跳过与兜底 | 12 | 2.3 MB | 自制 | ✅ |
| 15-批量与嵌套 | 51 | <0.1 MB | 自制 | ✅ |
| 16-自绘界面-OCR专项 | 2 | <0.1 MB | 自制 | ✅ |
| 17-合成安装器(Inno) | 11 | 23.8 MB | 自制（用 Inno 编译） | ✅ |
| 18-合成安装器(NSIS) | 7 | 1.7 MB | 自制（用 NSIS 编译） | ✅ |
| 19-合成安装器(MSI-WiX) | 16 | 5.9 MB | 自制（用 WiX 编译） | ✅（去掉 `.wixpdb`） |
| 20-静默参数探测 | 3 | <0.1 MB | 自制 | ✅ |

**自制样本合计约 48 MB**，可直接进仓库；**真实第三方合计约 692 MB**，不进仓库。

### 1.3 `_build\` 内容（全部自制，可公开）

| 子项 | 内容 |
|---|---|
| `cs\` | 45 个 C# 源码（`A29-*`、`A30-*`、`F13-*`、`OWNERDRAW-*`、`_trap` 等） |
| `wix\` | 8 组 `.wxs` + `.wixobj`（构建中间产物） |
| `isotrees\` | 8 套 ISO 源树 |
| `payload\` | 9 个载荷（含**假 MZ 桩** `app.exe`） |
| `*.py / *.ps1` | 生成器：`gen_csharp.py`、`gen_installers.py`、`gen_msi.py`、`gen_iso*.py/.ps1`、`gen_data.py`、`download_samples.py`、`verify_samples.py`、`reorganize.py`、`toolchain.ps1`、`fix_bom.py` |
| `*.iss / *.nsi` | 11 + 7 个合成安装器脚本 |
| `sample-index.json` | **170 条**逐文件索引（path/group/size/ext/magic/family/sections） |

### 1.4 已有的测试报告与证据（在 `安装包测试` 之外）

| 目录 | 文件数 | 体积 | 内容 |
|---|---|---|---|
| `AutoTrigger测试报告\` | 423 | 15.5 MB | 35 份问题文档 + 9 套提权复测原始证据 + RESULTS |
| `AutoTrigger复测报告\` | 55 | 4.4 MB | 6 项修复复测报告 + 原始 json/log |

◆ **这两处是本仓库报告与证据的**唯一**来源**，必须纳入，但要脱敏。
◆ **没有任何截图**（实测 `.png/.jpg/.jpeg/.bmp` 计数 = 0）——报告中一律标注「未提供」，不补造。

## 二、整理方案

### 2.1 目标目录结构

```text
AutoTrigger-TestSuite\
├─ README.md                    主入口（效果摘要 / 环境 / 统计 / 已知问题 / 快速验证）
├─ LICENSE                      Apache-2.0（仅覆盖本仓库自制内容）
├─ THIRD_PARTY_NOTICES.md       第三方软件与工具链的许可与获取方式
├─ .gitignore                   排除大文件与生成物
├─ samples\                     自制样本（07–20，去 wixpdb）约 48 MB
├─ sources\                     自制样本源码与构建说明（原 _build，脱敏）
│   ├─ csharp\  innosetup\  nsis\  wix\  iso\  payload\  generators\
│   └─ BUILD.md
├─ scripts\
│   ├─ Invoke-SmokeTest.ps1     快速冒烟（默认少量自制样本，含确认与前置检查）
│   ├─ Invoke-FullSuite.ps1     分组批量跑（复用 _run_tests.ps1）
│   ├─ Compare-Results.ps1      预期 vs 实际差异
│   ├─ Get-SampleManifest.ps1   校验样本 SHA-256 / 完整性
│   ├─ Get-ThirdPartySamples.ps1 按 manifest 下载真实样本（不随仓库分发）
│   └─ Cleanup-SyntheticSamples.ps1
├─ manifests\
│   ├─ samples.selfmade.json    自制样本清单（ID/类别/大小/SHA-256/预期）
│   ├─ samples.thirdparty.json  真实样本（名称/版本/官方 URL/SHA-256/预期）
│   ├─ expectations.csv         逐样本预期结果（来自测试样本清单.md）
│   └─ toolchain.json           编译器版本与官方来源
├─ reports\
│   ├─ README.md                报告索引与统计口径说明
│   ├─ summary.md               汇总（按组、按状态、分母与口径）
│   ├─ per-sample.csv           逐样本结果（ID/类别/名称/版本/SHA-256/预期/实际/证据/耗时/问题）
│   ├─ issues\                  35 份问题文档（脱敏）
│   ├─ retest-2026-10-12.md     6 项修复复测结果
│   └─ coverage.md              已验证范围与未验证场景
├─ evidence\                    脱敏后的 JSON/日志（按目录分组，含 MANIFEST 与脱敏规则）
└─ docs\
    ├─ test-method.md           测试方法与判定口径
    ├─ environment.md           环境要求（VM/权限/UAC/交互桌面）
    ├─ interpreting-results.md  结果判读（严格区分 安装成功/已触发/未验证/已安装）
    └─ faq.md
```

### 2.2 关键口径（写进 README 与 reports/README.md）

1. **严格区分状态**：`install_completed`（安装成功）/ `install_unverified`（未验证）/ `install_partial`（部分完成）/ `already_installed`（已安装）/ `triggered`（已触发）/ `killed_on_timeout` / `failed` / `skipped`。
   **退出码 0、安装器窗口关闭、流程结束都不算安装成功。**
2. **成功率必须带分母与口径**：只统计**同一环境、同一工具版本**的那一批；排除未验证/跳过/超时；说明排除项。
3. **历史问题三态标注**：已确认修复并复测 / 已修改但未复测 / 仍存在。
   本仓库目前只有第 5 轮修复的 6 项做过复测（5 项通过、2 项部分），**其余 29 份问题文档均为「仍存在（未复测修复）」**。
4. **报告缺失信息**：标注「未提供」，不补造。

### 2.3 需要脱敏的内容（实测命中）

| 敏感项 | 命中范围 | 处理 |
|---|---|---|
| 用户名 `<USER>` | 安装包测试 28 文件 / 测试报告 335 / 复测报告 51 | 副本中替换为 `%USERPROFILE%` 或 `<USER>` |
| 机器名 `<HOST>` | 测试报告 12 / 复测报告 3 | 副本中替换为 `<HOST>` |
| 硬编码绝对路径 | `_build` 全部脚本与 `.iss/`.nsi`（每文件 1–6 处） | 改为参数化（`-Root` / `$Root`） |
| IP `<内网IP>` | **无命中** | — |
| SSH 私钥 / authorized_keys | **无命中** | — |
| 疑似 token/secret | 安装包测试 3 / 测试报告 4 | 人工复核后决定（多为 MSI 日志噪声） |

◆ **原始证据保持不动**；发布的是**脱敏副本**，并保留一份不公开的映射规则记录。

## 三、「不适合公开」清单

### 3.1 明确排除（不进仓库、不设 Git 历史）

| 路径 | 原因 |
|---|---|
| `_toolchain\*`（206 MB） | 第三方编译器发行包（Inno Setup / NSIS / WiX 3.14 / chocolatey nupkg）。体积大且应从其官方渠道获取，不宜由本仓库再分发。**改为 `manifests/toolchain.json` 登记版本与官方 URL**。 |
| `samples\01\06\`（约 692 MB） | 真实第三方安装包。再分发许可**逐项不同**（Zoom/MobaXterm 等为专有 EULA，明确限制再分发），且体积远超 Git 合理范围。**改为 `manifests/samples.thirdparty.json` 登记官方 URL + SHA-256，由用户自行下载**。 |
| `_build\wix\*.wixobj` | 构建中间产物，可由源码重新生成。 |
| `samples\19-*\*.wixpdb` | WiX 调试符号，非样本（原报告 ISSUE-13 已记录其污染统计）。 |
| `安装包测试.zip`（Desktop，845 MB） | 打包副本，与本任务无关。 |
| `C:\ATTest\`（含我本轮安装 SSH 用的脚本与临时文件） | 工作目录，不在套件范围，且可能含机器特定信息。 |

### 3.2 需警示后发布

| 路径 | 说明 |
|---|---|
| `_trap\`（12 个 + `_build\cs` 对应源码） | 文件名故意模仿卸载/更新/调试程序（`uninstall.exe`、`卸载.exe`、`update.exe`、`crashpad_handler.exe` …），实际是可重编译的**惰性桩**。发布价值：用于验证「黑名单是否被正确拦截」。**风险**：可能触发杀软误报。计划：保留二进制并在 `samples\10\README` 显著警示，同时提供源码供自行编译。 |

### 3.3 可公开但需改写

| 路径 | 处理 |
|---|---|
| `README.md`（套件） | 重写为面向使用者的入口文档。 |
| `测试样本清单.md` | 脱敏 + 拆分：预期结果进 `manifests/expectations.csv`，说明进 `docs/test-method.md`。 |
| `_run_tests.ps1` / `_cleanup.ps1` | 核对当前 CLI 契约后保留（原脚本写的 `--log-file` / `--timeout` / `--log-level` 已实测有效）。 |
| `_build\*` 脚本 | 参数化根路径 + 去用户名。 |

## 四、许可与合规判断（初判）

| 对象 | 许可 | 是否随仓库分发 |
|---|---|---|
| 本仓库自制样本与脚本 | 由作者决定（建议 Apache-2.0） | ✅ |
| Inno Setup / NSIS / WiX | 各自许可（Inno: 自定义允许免费使用；NSIS: zlib/libpng；WiX: MS-RL） | ❌ 仅登记来源 |
| 真实第三方安装包 | 各不相同（GPL/MPL/BSD/专有 EULA） | ❌ 仅登记官方 URL + SHA-256 |

◆ 具体条款需你在发布前最终确认；本仓库只做「登记来源、不代为分发」的低风险选择。

## 五、下一步（实施顺序）

1. 建立发布目录骨架 + `.gitignore` + LICENSE + THIRD_PARTY_NOTICES。
2. 复制自制样本（去 `.wixpdb`）与 `_build` 源码（参数化、脱敏）。
3. 生成 manifests（自制 + 第三方 + 预期结果 CSV + 工具链）。
4. 脱敏并归档 reports 与 evidence（保留可追溯副本与脱敏规则）。
5. 依据**实测过的** CLI 契约编写 `scripts\Invoke-SmokeTest.ps1` 等脚本。
6. 实际跑一次冒烟验证，把真实结果写进 README（不夸大）。
7. 全量校验：相对链接、SHA-256、统计口径、文档与脚本一致性。
8. 输出最终汇报（发布目录 / 排除清单 / 报告入口 / 冒烟命令 / 实测结果 / 许可与隐私风险 / 未完成事项）。

◆ **不会**创建 GitHub 仓库、推送代码或上传附件。
