# A25 入口分层与黑名单（已提权，10 组逐个子样本）

> 10 组整体跑过一次但被中断；本轮把 6 个子样本**逐个单独跑**（每个一个进程），全部 `EXIT=0`。

## 0. 结论速览

| 子样本 | 清单预期 | 实测 | 判定 |
|---|---|---|---|
| `A25-01-规范包-含黑名单` | readme 命中 `install.bat`；其余 `skipped_after_success`；黑名单绝不执行 | 执行 3 个（`vcredist_x64.exe`(P3) → `install.bat`(P0) → `setup.exe`(P0)），`excluded=11`，**`VIOLATION=0`** | ✅（黑名单铁证通过） |
| `A25-02-readme指向不存在文件` | **不得产生任何执行动作** | `安装说明.txt` 被 `document_host` 打开 → **`killed_on_timeout` 67.3 s** | ❌ [ISSUE-24](../../../reports/issues/ISSUE-24-包内readme被document_host打开并挂到超时.md) |
| `A25-03-架构优先` | 先 x64、不得先 x86 | 顺序 `setup_x64 → install.bat → setup_x86` **x64 在前 ✅**；但装成后仍执行 x86 | ⚠️ 基本通过 |
| `A25-06-阶段2兜底` | P0–P4 全败 → **回退 P5 的 `deep\tools\extra\runtime-helper.exe`** | `entries=6` **不含该文件**，`fallback_used=false`，5 个全 `failed` | ❌ [ISSUE-23](../../../reports/issues/ISSUE-23-阶段2暴力兜底未生效.md) |
| `A25-04-规范包压缩版.7z` | 解压前即产出 entries | `entries=51 / excluded=11`，`install.bat` + `setup.exe` 执行，`setup.exe` → `install_completed` | ✅ |
| `A25-04-规范包压缩版.zip` | 同上 | 与 .7z 完全一致 | ✅ |

## 1. 三条铁证（可直接引用）

1. **黑名单没有被执行** ✅
   ```text
   Get-ChildItem C:\Users\Public\AT-SENTINEL -Filter 'VIOLATION-*' | Measure-Object
   -> Count = 0
   ```
   同时 A25-01 有 `excluded=11`，与"11 个黑名单陷阱"数量一致。

2. **架构优先级顺序正确** ✅ —— 日志里 `选用入口` 的顺序：
   ```text
   setup_x64.exe (P1) -> install.bat (P1) -> setup_x86.exe (P1)
   ```

3. **压缩包在解压前就完成分层** ✅ —— `A25-04` 的 `layout_analysis.entries=51`，
   符合 F17.1 "先 `7z l` 列清单、解压前即产出 `layout_analysis.entries`"。

## 2. 两个失败项

- **ISSUE-23（高）**：阶段2兜底失效。P5 目标 `runtime-helper.exe` 是**整个样本里唯一有效的 PE**
  （`MZ=True / PE=True`，其余 4 个是 514 字节的假桩），却没被枚举、没被执行，`fallback_used=false`。
- **ISSUE-24（中）**：包内 `.txt` 被记事本打开并挂到 idle 超时（67.3 s）。
  且同一批里 `A25-01` 的同类 `.txt` 是 `skipped`，**同类文件两种处理**。

## 3. 顺带记录：假 PE 桩被跑满 9 次

`A25-06` 里 4 个 514 字节的假桩（`MZ=True / PE=False`）每个都被套满 9 次静默参数：

```text
fork/exec ...: This version of %1 is not compatible with the version of Windows you're running.
```

4 个文件 × 9 次 = **36 次必然失败的启动**。建议在识别阶段就判"非法 PE"并早退（与 ISSUE-10 同族）。

## 4. 样本侧缺陷（不影响工具判定）

`A25-03` 的哨兵写成了**字面量** `ARCH-CHOSEN-%PROCESSOR_ARCHITECTURE%`（变量未展开），
因此清单中"哨兵出现 `ARCH-x64`"这条断言**实际无法验证**。建议样本改为
`ARCH-CHOSEN-x64` / `ARCH-CHOSEN-x86` 或确保变量在正确的 shell 里展开。

## 5. 复现命令

```powershell
$Exe = "<DESKTOP>\AutoTrigger.exe"
$B   = "<SUITE_ROOT>\samples\10-入口分层与黑名单"
Get-ChildItem $B | ForEach-Object {
  & $Exe --input $_.FullName --output ".\$($_.BaseName).json" --timeout 240 --log-level debug --no-lock
}
Get-ChildItem C:\Users\Public\AT-SENTINEL -Filter 'VIOLATION-*'   # 必须为空
```
