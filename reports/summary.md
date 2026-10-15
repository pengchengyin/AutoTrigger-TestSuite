# 测试结论汇总（按环境与工具版本分段）

◆ **本节所有数字来自各轮实际结果 JSON，逐样本汇总而成。**

## 一、为什么必须分段

用户须知：本套件的测试跨多个工具构建与权限上下文。
**不同构建 / 不同环境的分段不可相加、不可比较。**下面按 **(工具构建, 环境)** 分段。

| 段 | 工具构建 | 权限/环境 | 覆盖输入样本 | 状态分布 | 安装成功 / 分母 | 口径说明 |
|---|---|---|---|---|---|---|
| A-修复前提权 | 10,038,272 B | 管理员 | 207 | {install_completed:72,install_partial:20,skipped:35,failed:32,triggered:36,killed_on_timeout:8,install_unverified:4} | 72/172 | 41.9% |
| A-修复前未提权 | 10,038,272 B | 普通用户 | 32 | {install_partial:5,install_completed:3,skipped:3,failed:9,triggered:12} | 3/29 | 10.3% |
| B-修复后定向复测 | 10,235,904 B | 管理员 | 8 | {install_unverified:1,install_completed:6,install_partial:1} | 6/8 | 75% |
| D-自制备样 | 7,758,848 B | 管理员 | 120 | {install_completed:34,failed:20,容器展开:16,skipped:12,install_unverified:10,killed_on_timeout:10,install_partial:9,triggered:9} | 34/92 | 37.0% |
| E-全量 20 组 | 7,758,848 B | 管理员（GUI 环境阻塞） | 149 | {install_completed:43,install_partial:18,failed:20,killed_on_timeout:17,install_unverified:8,triggered:9,skipped:12,容器展开:22} | 43/115 | 37.4% |
| **F-全量 20 组（当前桌面构建）** | **10,967,552 B** | **管理员（桌面可交互）** | **149** | **{install_completed:55,install_partial:10,failed:22,killed_on_timeout:9,install_unverified:9,triggered:9,skipped:13,容器展开:22}** | **55/114** | **48.2%** |

> 分母 = 该段覆盖的输入样本数 − `skipped` − `容器展开`。`skipped` 表示「未执行」（无宿主、空文件、黑名单等），
> 不构成安装能力的证据；`install_unverified` / `install_partial` / `triggered` / `killed_on_timeout` / `failed` 在分母内但不计入分子。

### 分段明细

- **A-修复前提权**：2026-10-11 构建（10,038,272 字节），管理员会话；「工具实际效果」的历史参考段。
- **A-修复前未提权**：同一构建、普通用户会话，仅覆盖 07/09 两组 32 个样本。
- **B-修复后定向复测**：2026-10-12 构建（10,235,904 字节），只跑 6 项修复对应的 8 个定向样本。
- **D-自制备样**：2026-10-14 构建（7,758,848 字节），自制备样 07–20 全覆盖。
- **E-全量 20 组**：同一构建（7,758,848 字节），首次跑完 149 个输入样本；GUI 类样本受锁屏/前台为空影响。见 [run-2026-10-14-full.md](run-2026-10-14-full.md)。
- **F-全量 20 组（当前桌面构建）**：2026-10-15 构建（**10,967,552 字节 / SHA-256 11DCDB93…2727**），管理员会话、桌面可交互，149 个输入样本全覆盖；
  期间发生一次约 37 分钟系统休眠（ISSUE-28）、45 个样本快照不完整（ISSUE-08）。见 **[run-2026-10-15.md](run-2026-10-15.md)**。

## 二、状态口径（务必区分）

| 状态 | 含义 | 是否计入「安装成功」 |
|---|---|---|
| `install_completed` | 取得安装证据（卸载项 / 落盘 / MSI 11707 等） | ✅ 是 |
| `install_unverified` | 只有退出码 0 之类的弱证据，**未验证** | ❌ 否 |
| `install_partial` | 同时存在成功与失败反证据（如落盘 + 退出码非零） | ❌ 否 |
| `already_installed` | 装前已存在 | ❌ 否（另计） |
| `triggered` | 只是被触发，未确认安装 | ❌ 否 |
| `killed_on_timeout` | 超时终止 | ❌ 否 |
| `failed` | 失败 | ❌ 否 |
| `skipped` | 未执行（空文件 / 无宿主 / 命中黑名单等） | ❌ 否（**排除出分母**） |

◆ **退出码为 0、安装器窗口关闭、流程正常结束，都 _不_ 算安装成功。**

## 三、容器展开实体不计入

一次目录/压缩包输入会展开出大量子项。统计样本口径时，**只取 `samples\` 下的顶层输入样本**，
容器展开出的实体（如 `MobaXterm_Installer.zip` 的 1335 条、`A6-批量50文件` 的 55 条子项）不计入输入样本数。

## 四、样本构成

| 类别 | 数量 | 是否随仓库分发 |
|---|---|---|
| 自制合成样本（组 07–20） | 发布集内 240 个文件 | ✅ 随仓库 |
| 真实第三方安装包（组 01–06） | 约 692 MB | ❌ 仅登记官方来源与 SHA-256 |

## 五、未提供的信息（不补造）

| 项 | 状态 |
|---|---|
| 截图 | **未提供** — 证据目录中 `.png/.jpg/.jpeg/.bmp` 计数为 0 |
| 组 01–06 中部分样本的官方下载地址 | **未提供** — 见 `manifests/samples.thirdparty.json` 的 `source_status` |
| 工具源码 commit | **未提供** — 测试基于分发二进制 |
| 每次运行的精确时间戳 | 部分提供（见各结果 JSON 的 `started_at` / `finished_at`） |


