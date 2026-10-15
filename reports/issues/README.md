# 问题追踪总表（ISSUE-01 ~ ISSUE-36）

> 用途：把散落在 36 份问题文档里的问题**统一到一张表**，每轮复测时只需更新「最近复测」一列，
> 就能一眼看出**哪些 issue 可以关闭、哪些仍存在、哪些是环境阻塞**。
> 逐条详细复现与建议仍见同目录下的 `ISSUE-*.md`。

## 一、怎么用

1. 开跑前先确认环境：杀软已排除被测 exe（见 [../../docs/environment.md](../../docs/environment.md) 第八节）；
   桌面**未锁屏且前台可交互**（`Get-Process LogonUI` 无输出）。
2. 跑完后按「复现样本」列核对每个 issue 的「关闭判据」。
3. 满足判据 → 把「最近复测」改成 `✅ 已关闭` 并写明轮次；不满足 → `❌ 仍存在`；
   因环境（锁屏/杀软/休眠）拿不到有效数据 → `⚠️ 环境阻塞`。
4. 在第四节「复测记录」追加一行。

## 二、状态定义

| 标记 | 含义 |
|---|---|
| ✅ 已关闭 | 满足该 issue 的关闭判据，且证据完整 |
| 🔶 疑似已修复 | 本轮已不满足问题现象，但样本/口径或轮次不足，需再确认 |
| ❌ 仍存在 | 本轮仍然复现问题现象 |
| ⚠️ 环境阻塞 | 因锁屏 / 前台为空 / 杀软 / 休眠，未取得有效数据 |
| ⏭ 未复测 | 本轮未覆盖（如未提权场景、稳定性序列） |
| 🆕 新增 | 本轮新发现的问题 |

## 三、本轮环境说明（判读前必看）

本轮为**当前桌面构建（10,967,552 B）**、**管理员会话**、**桌面可交互**下跑完全部 20 组 149 个输入样本。
与上一轮相比，GUI 点击（UIA / 模板 / OCR）本轮可用，因此 Inno / NSIS 中英文向导、3010、完成页、自绘界面等样本拿到了真实结论。

仍然存在的环境因素：

- 被测机在 15:48–16:25 发生一次约 37 分钟的系统休眠，跨休眠样本的墙钟耗时不可用（ISSUE-28）。
- 仍有 45 个样本日志出现「文件系统快照不完整…文件差异证据已禁用」（ISSUE-08），会使部分已确认落盘的样本降级为 `install_unverified`。
- 缺少真实 InstallShield 安装器样本（清单已知缺口），F13 的 InstallShield 参数路径由 20 组参数探测桩等价覆盖。

## 四、复测记录

| 轮次 | 日期 | 构建 | 权限 | 覆盖输入样本 | 备注 |
|---|---|---|---|---|---|
| 修复前第 1 轮 | 2026-10-11 | 10,038,272 B | 管理员 | 207 | 35 份问题文档的来源 |
| 修复后定向复测 | 2026-10-12 | 10,235,904 B | 管理员 | 8 | 6 项修复通过 |
| D-自制备样 | 2026-10-14 | 7,758,848 B | 管理员 | 120 | 合成安装器 21/27 |
| E-全量 20 组 | 2026-10-14/15 | 7,758,848 B | 管理员 | 149 | 见 [../run-2026-10-14-full.md](../run-2026-10-14-full.md)；GUI 环境阻塞 |
| **F-全量 20 组（当前桌面构建）** | **2026-10-15** | **10,967,552 B** | **管理员** | **149** | 桌面可交互，见 [../run-2026-10-15.md](../run-2026-10-15.md) |

---

## 五、逐条状态（ISSUE-01 ~ ISSUE-36）

| ID | 标题 | 严重度 | 复现样本 | 关闭判据（简） | 修复前基线 | 最近复测（2026-10-15 F/当前桌面构建） |
|---|---|---|---|---|---|---|
| ISSUE-01 | 未提权导致管理员安装器无法启动 | 致命 | NSIS-01 | 非提权下能起，或给出 requires_elevation 专属状态 | 仍存在 | ⏭ 未复测（本轮全部为管理员会话） |
| ISSUE-02 | 目标完整性级别更高时 UIPI 拦截点击且不快速失败 | 致命 | Notepad3 | 识别 IL 高于工具即快速失败或自动提权重试，不再空耗约 300 s | 仍存在 | ❌ 仍存在（Notepad3 4 次尝试中 3 次超时，合计约 228 s，且仍 pre_installed） |
| ISSUE-03 | 黑名单误杀含卸载字样的合法安装器 | 高 | 09-快捷方式指向安装器.lnk MSI-06 V1 V2 INNO-06 A29-03 04 09 11 | 上述样本不再 excluded_blacklist，真卸载器仍被排除 | 仍存在 | ✅ 已关闭（合法样本均未被黑名单跳过；A25-01 复跑 VIOLATION=0） |
| ISSUE-04 | 内置图像模板为空导致 GUI 兜底缺失 | 高 | --capabilities / --dump-resources | 模板口径一致，或显著提示无模板 | 仍存在 | ❌ 仍存在（builtin_templates=false、master_count=0，日志仍提示内置图像模板为空） |
| ISSUE-05 | OCR 引擎启动自检不稳定 | 高 | --check-prereq 连续多次 | 多次自检稳定 ok，启动在超时内 | 仍存在 | ❌ 仍存在（INNO-01 出现 OCR initialization: context deadline exceeded） |
| ISSUE-06 | MSI 首次 quiet 返回 1603 且成功却只判 medium | 中 | MSI-01 putty | 首试不再 1603，且 MSI-01 达 high | 仍存在 | 🔶 部分（MSI-01 单次尝试即退出码 0，无 1603；但 artifact_check_failed 使其仍为 medium） |
| ISSUE-07 | summary.by_status 键名与 final_status 枚举不一致 | 中 | 任意结果 JSON | 键名与枚举一致，或给显式映射，且 sum==total | 仍存在 | ❌ 仍存在（仍为 installed/partial/timeout 等短名） |
| ISSUE-08 | 文件系统快照预算上限导致负向证据被禁用 | 中 | 07-原生导出表 10-导出函数库 | 体现 snapshot_complete=false 或明确声明 | 仍存在 | ❌ 仍存在（45 个样本日志出现「文件系统快照不完整」，文件差异证据被禁用） |
| ISSUE-09 | 非法 MSI 被判 install_partial 而非 failed | 中 | OLE头伪msi MSI-07 MSI-08 | 1620 判 failed 且不被 A3 抬升 | 仍存在 | ❌ 仍存在（MSI-07 / OLE头伪msi 仍判 partial，证据为 A3+N1） |
| ISSUE-10 | document_host 直接执行非可执行文档本体 | 中 | 实际是PDF的exe 实际是文本的exe | 不再对非 PE 调 CreateProcess | 仍存在 | 🔶 疑似已修复（PDF→skipped no_host_app；文本→failed untriggerable，均未按 PE 执行） |
| ISSUE-11 | 合成载荷 app.exe 非有效 PE 致 artifact_check 失败 | 中 | MSI-01 A29-05 07 10 MSI-04 05 | 口径统一后不降级，或换真实 PE | 仍存在 | ❌ 仍存在（artifact_check_failed 全轮 54 次；A29-03/05 等仍 install_unverified） |
| ISSUE-12 | 非 MSI 安装器返回 3010 被判失败 | 高 | NSIS-06 | 首试 3010 即 completed + requires_reboot | 仍存在 | ✅ 已关闭（NSIS-06 / INNO-08 / MSI-03 均 completed 且 requires_reboot=true） |
| ISSUE-13 | 构建中间产物被当作样本处理污染统计 | 低 | 19 组 .wixpdb | total 等于真实样本数 | 仍存在 | ✅ 可关闭（样本侧）（19 组已无 .wixpdb） |
| ISSUE-14 | requires_network 只在有窗口时才输出 | 中 | INNO-10 A30-08 | 两样本字段与状态一致 | 仍存在 | ❌ 仍存在（INNO-10 判 completed/high 且无 requires_network；全轮 0 次命中） |
| ISSUE-15 | 安装后拉起的应用窗口被持续自动化至硬超时 | 高 | ShareX | 安装器主进程退出即收敛 | 仍存在 | ❌ 仍存在（audacity 第二次尝试 228 s 超时；ShareX 判 partial） |
| ISSUE-16 | 走完 GUI 向导仍被硬超时判 partial | 高 | Notepad3 | 判 completed 且 notes 注明超时终结 | 仍存在 | 🔶 部分（多数 GUI 向导样本已 completed 且 notes 注明超时终结；Notepad3 仍超时） |
| ISSUE-17 | 升级式安装被误判为回滚 N4 | 高 | VC_redist | 首次即 completed 且无 N4 | 仍存在 | ✅ 已关闭（VC_redist completed/medium，证据 A3+A1，无 N4） |
| ISSUE-18 | 样本不完整 MobaXterm 缺 dat 且错误未提炼 | 中 | MobaXterm.msi | 补齐后 completed，或 1603 有二级归因 | 仍存在 | 🔶 疑似已修复（已产出 `*-msi-logs` 目录，1603 可二级归因；样本未补齐仍 1603） |
| ISSUE-19 | 重复点击同一控件触顶后空转到超时 | 高 | VeraCrypt 7z2600-32bit | 触顶即记 gui_actions_exhausted 并结束 | 仍存在 | ❌ 仍存在（全轮无 gui_actions_exhausted；VeraCrypt 243 s） |
| ISSUE-20 | Go 回调表耗尽导致致命崩溃 | 致命 | 06 组 | 不再出现 too many callback functions | 仍存在 | 🔶 未复现（06 组含 1335 条展开正常收尾，无 too many callback functions） |
| ISSUE-21 | 落盘证据无法归因且自相矛盾 | 高 | nssm 7z2501 7z2600-32bit | S2/N5 的 detail 带路径样例 | 仍存在 | ✅ 已关闭（S1/S2/A3 均带 source 路径与 detail，例如 `hklm\{...}`、`C:\Program Files\ATSynthNsis01`） |
| ISSUE-22 | 便携压缩包被当作安装器处理 | 中 | nssm 7z2501 putty.zip | 非安装器条目按 triggered 收敛 | 仍存在 | ❌ 仍存在（nssm / 7z2501 / putty / npp 容器内仍见 install_partial 子项） |
| ISSUE-23 | 阶段 2 暴力兜底未生效 | 高 | A25-06 | P0–P4 失败后执行 P5 且 fallback_used=true | 仍存在 | ❌ 仍存在（A25-06 fallback_used=false，5 条 failed，未执行 P5） |
| ISSUE-24 | 包内 readme 被 document_host 打开并挂到超时 | 中 | A25-02 | 安装说明.txt attempts=0，宿主确认即 triggered | 仍存在 | ✅ 已关闭（安装说明.txt → skipped entry_hint_document，未打开、无超时） |
| ISSUE-25 | 反证据 N6 被正向证据覆盖 | 高 | A29-07 A29-08 | A29-07 partial 且 N6 参与，A29-08 failed | 仍存在 | ❌ 仍存在（A29-08 判 failed ✓；A29-07 判 completed/medium，N6 未参与，受 ISSUE-08 影响） |
| ISSUE-26 | 二次调用未识别 already_installed | 高 | A29-10 连跑两次 | 第 2 次 already_installed + pre_installed=true | 仍存在 | ⏭ 未复测（本轮只跑一次，第 1 次判 install_completed） |
| ISSUE-27 | 启动后无动作从未判定 no_activity | 高 | A30-02 | startup 30 s 内 failed: no_activity | 仍存在 | ❌ 仍存在（A30-02 killed_on_timeout，单次尝试 240 s） |
| ISSUE-28 | 系统休眠期间计时照算 | 低 | A30-02 期间休眠 | duration 不含挂起区间 | 仍存在 | ❌ 仍存在（本轮休眠约 37 分钟；A29-02 墙钟 2247 s，attempts 合计约 1.5 s） |
| ISSUE-29 | 活动感知超时状态系统性偏差 | 高 | A30-03 05 06 09 | 03 05 09 判 timeout，06 判 triggered | 仍存在 | ❌ 部分（03/05 已对齐 timeout；06 应 triggered 实为 timeout；09 应 timeout 实为 partial） |
| ISSUE-30 | 完成页卡住却判 partial 未取到安装证据 | 高 | A30-04 | 采到 S1/S2 并判 completed + notes | 仍存在 | ✅ 已关闭（A30-04 completed/medium，证据 S1，notes 注明超时终结） |
| ISSUE-31 | summary.total 包含解压子项导致计数不符 | 中 | A6-批量50文件 | total=50 | 仍存在 | ❌ 仍存在（输入 50，total=55） |
| ISSUE-32 | ISO 介质分类与清单不符 | 中 | A26-05 A26-07 | 分类与清单一致 | 仍存在 | ❌ 仍存在（A26-05=installer_media、A26-07=data_disc，与清单相反） |
| ISSUE-33 | 自绘窗口 OCR 模板回退从未触发 | 高 | OWNERDRAW 浅色 深色 | source 出现 template/ocr 或显式 gui_identify_failed | 仍存在 | ✅ 已关闭（gui_actions.source = template + ocr；浅色向导 completed/medium） |
| ISSUE-34 | 解压失败缺少结构化错误码 | 低 | 14 组 04 05 06 07 08 | 输出结构化 error_code | 仍存在 | 🔶 疑似已修复（notes 出现 extract_failed / extract_size_exceeded 前缀；仍无独立 error_code 字段） |
| ISSUE-35 | 无宿主扩展名被判 failed 而非 skipped | 低 | 08-无宿主扩展名.atdoc | 判 skipped: no_host_app | 仍存在 | ❌ 仍存在（failed / untriggerable） |
| ISSUE-36 | Defender 误报并隔离 AutoTrigger 导致整轮中断 | 致命 | 全量运行环境 | 未加排除不再触发，或脚本在 exe 丢失时立即中止 | 🆕 新增 | ⏭ 未复测（本轮未在未加排除的干净机器验证；本会话无法读取 Defender 排除项） |

> 统计：致命 4（01 02 20 36）、高 16、中 12、低 4。
> 本轮判定：✅ 已关闭 8（03 12 13 17 21 24 30 33）、🔶 疑似已修复 / 部分 6（06 10 16 18 20 34）、
> ❌ 仍存在 19（02 04 05 07 08 09 11 14 15 19 22 23 25 27 28 29 31 32 35）、⏭ 未复测 3（01 26 36）。
> 计数以逐行标记为准。


