# 测试方法

## 一、总体流程

```text
准备环境 → 清理残留 → 逐样本调用 AutoTrigger → 读取结果 JSON → 汇总 → 人工判读 → 生成问题文档
```

## 二、调用方式

每个样本**单独调用一次**（不让工具自己去遍历目录），以保证样本与结果的对应关系清晰：

```powershell
& AutoTrigger.exe --input <样本绝对路径> --output <结果json> --log-file <日志> --timeout <秒> --log-level debug --no-lock
```

参数来源：均为实测可用（`--version / --capabilities / --input / --output / --log-file / --timeout / --log-level / --no-lock`）。
**未使用任何未经验证的参数。**

- `--no-lock`：避免与本机已打开的工具实例抢单实例锁。
- `--timeout`：按样本类型给 60–600 s；超长安装样本（A30-07 等）给更长。
- `--log-level debug`：保留界面识别/点击的细节，便于定位 GUI 问题。

批量场景用 **scripts\Invoke-SampleTest.ps1**，按「组根目录条目」逐样本调用并归档
（目录类样本整体作为一个输入，其展开子项只出现在结果 JSON 的 results[] 中）；
多次运行（中途退出后续跑）用 **scripts\Summarize-Run.ps1** 按样本名合并汇总。
直接把**目录**传给工具时，结果 JSON 会包含大量展开子项，统计时必须过滤（见 reports/README.md）。

## 三、权限上下文

| 上下文 | 启动方式 | 用途 |
|---|---|---|
| 普通用户 | 直接运行 | 第 1 轮：验证未提权行为 |
| 管理员 | `Start-Process -Verb RunAs` | 后续所有轮次 |

> 本机 `ConsentPromptBehaviorAdmin=0`（静默提权），因此 `RunAs` 不会弹 UAC。

## 四、环境准备与清理

**每次开跑前必须清理**，否则状态类样本会给出假结果
（例：A29-07 的卸载项若已存在，回滚证据 N6 根本不会产生）。

```powershell
# 管理员
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Cleanup-SyntheticSamples.ps1
```

## 五、结果判读

见 [interpreting-results.md](interpreting-results.md)。核心原则：

1. **只有拿到安装证据（S1/S2/S3/S4/A2/B1 等）才算 `install_completed`。**
2. 退出码 0、窗口关闭、流程结束 —— **都不算**。
3. 出现反证据（N1–N6）时进入 `install_partial` / `failed`，并与正面证据并列记录。
4. `install_unverified` 是"弱证据"，单独统计，**不并入成功率**。

## 六、防干扰措施

| 干扰 | 措施 |
|---|---|
| 系统休眠导致耗时异常 | 用 `SetThreadExecutionState` 阻止休眠（本次测试中曾因休眠出现 26118 s 的异常耗时，已剔除并记为问题） |
| 残留状态 | 每轮前跑清理脚本 |
| OCR 启动不稳定 | 记录 `ocr_engine_status`，失败时标注该轮 GUI/OCR 结论不可靠 |
| 容器展开污染统计 | 只按**完整路径**前缀判定输入样本 |
| 长任务与工具轮询冲突 | 用标记文件（`_done*.txt`）判断结束，避免中途杀进程树 |

## 七、证据留存

- 每个样本：结果 JSON + 日志 + 控制台输出，**独立文件，不覆盖历史**。
- 每轮：汇总 `summary.md`，列出预期与实际差异。
- 发布时：原始证据 → 脱敏副本（见 evidence/SANITIZATION.csv），**保留映射规则但不公开敏感映射**。
