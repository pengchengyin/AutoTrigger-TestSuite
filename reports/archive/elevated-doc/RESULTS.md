# 文档类（08 组）与长样本（A30-07/09）实测（已提权）

## 一、08 组 · 文档类（8 个）

| 样本 | 清单预期 | 实测 | 判定 |
|---|---|---|---|
| `01-有效文档.pdf` | 有宿主 → 打开并 `triggered`，记宿主进程名 | `triggered`，`platform_meta.host_program = ...\msedge.exe` | ✅ |
| `02-Word文档.docx` | 无宿主 → `skipped: no_host_app` | `skipped`，notes=`no_host_app` | ✅ |
| `03-Excel表格.xlsx` | 同上 | `skipped` | ✅ |
| `04-文档.rtf` | 同上 | `skipped` | ✅ |
| `05-老格式.doc` | 同上（不得因内容非法崩溃） | `skipped`，无崩溃 | ✅ |
| `06-幻灯片.pptx` | 同上 | `skipped` | ✅ |
| `07-含宏文档.docm` | 同上 | `skipped` | ✅ |
| `08-无宿主扩展名.atdoc` | **`skipped: no_host_app`** | **`failed`，notes=`untriggerable`** | ❌ ISSUE-35 |

### 环境说明（很重要）

本机**没有安装 Office / WPS / LibreOffice**：

```text
cmd /c assoc .docx -> (无关联)
cmd /c assoc .xlsx -> (无关联)
cmd /c assoc .pptx -> (无关联)
cmd /c assoc .doc  -> (无关联)
cmd /c assoc .rtf  -> (无关联)
cmd /c assoc .pdf  -> (无关联)   但 FileExts\.pdf\UserChoice.ProgId = MSEdgePDF
cmd /c assoc .txt  -> .txt=txtfilelegacy        <-- 这就是 ISSUE-24 里 .txt 会挂住的原因
```

所以 02–07 判 `skipped: no_host_app` 是**环境正确**的（清单的"有宿主"分支在本机无法验证），
`01` 也正确识别了 Edge 作为 PDF 宿主。**只有 `.atdoc` 的口径不一致**（见 ISSUE-35）。

耗时：0.9 ` 3.9 s/文件，全部正常结束，无挂起。

## 二、长样本 · A30-07 / A30-09（`--timeout 600`）

| 样本 | 墙钟 | 尝试内时长 | term | evidence | final_status | 清单预期 |
|---|---|---|---|---|---|---|
| `A30-07-超长安装-持续700s` | **604.9 s** | 599.5 s | `graceful` | S2（842 个，真实落盘） | **`install_completed / high`** + notes | 600 s 终止、可判装成 | ✅ |
| `A30-09-超长安装-只在TEMP写盘700s` | **610.9 s** | 599.8 s | `graceful` | S2（5 个） | **`install_partial / low`** | **`killed_on_timeout`** | ❌ |

- **硬上限确实生效**：两者都在 `600 s` 处被终止（599.5 / 599.8 s），`termination_mode` 有值 ✅；
- **`A30-07` 的判定完全正确**：notes = `"terminated on timeout; installation evidence still collected"`；
- **`A30-09` 又栽在 `S2` 上**：该样本只写 `%TEMP%`，却出现 `S2|新增 5 个文件`，
  把 `killed_on_timeout` 抬成 `install_partial`（与 ISSUE-21/ISSUE-29 §二 同源）。

> 这对样本本意是"有落盘 vs 无落盘 → 不同判定"，而 `S2` 的误报把这个对照**精确地毁掉了**。

## 三、本轮新开条目

- **[ISSUE-35](../../issues/ISSUE-35-无宿主扩展名被判failed而非skipped.md)**（低）：
  无宿主扩展名被判 `failed: untriggerable`，而非 `skipped: no_host_app`。

## 四、复现命令

```powershell
$Exe = "<DESKTOP>\AutoTrigger.exe"
$S   = "<SUITE_ROOT>\samples"
Get-ChildItem "$S\08-文档类" -File | ForEach-Object {
  & $Exe --input $_.FullName --output ".\$($_.BaseName).json" --timeout 90 --log-level debug --no-lock
}
# 长样本（各约 10 分钟）
foreach ($p in @('A30-07','A30-09')) {
  $f = Get-ChildItem "$S\12-超时与活动感知" -File | Where-Object { $_.Name -like "$p*" }
  & $Exe --input $f.FullName --output ".\$p.json" --timeout 600 --log-level debug --no-lock
}
```
