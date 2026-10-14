# 批量（15 组）与光盘映像（13 组）实测（已提权）

> 本轮加了一个**防止系统休眠的守卫**（`SetThreadExecutionState(ES_CONTINUOUS|ES_SYSTEM_REQUIRED)`），
> 避免上一轮"A30-02 被睡眠冻结 7 小时"的情况重演。批次结束时已恢复。

## 一、批量 50 文件（`A6-批量50文件`，目录内正好 50 个文件）

| 指标 | 清单预期 | 实测 | 判定 |
|---|---|---|---|
| `summary.total` | **50** | **55** | ❌ [ISSUE-31](../../../reports/issues/ISSUE-31-summary.total包含解压子项导致计数不符.md) |
| `sum(by_status) == total` | 恒等 | 55 == 55 | ✅ |
| 单文件失败不影响整体 | 成立 | 成立（50 个输入全部有结果） | ✅ |

结果分布：`installed=5 failed=10 skipped=5 timeout=5 triggered=30`（合计 55）。

分类明细（50 个输入）：

```text
case01/11/21/31/41.exe  -> install_completed (5)
case02/12/22/32/42.dll  -> failed           (5)
case03/13/23/33/43.txt  -> killed_on_timeout(5)   <-- ISSUE-24 的批量放大
case04/14/24/34/44.pdf  -> triggered        (5)
case05/15/25/35/45.zip  -> triggered        (5)   + 每个解出 1 个 a.txt（即多出来的 5 条）
case06..09 系列          -> triggered（bat/ps1/vbs/js）
case10/20/30/40/50.bin  -> failed           (5)
```

耗时 **433 s**（平均 8.7 s/文件）。

## 二、三层嵌套（`01-三层嵌套.7z`）· F6 递归 ✅

| 条目 | 结果 |
|---|---|
| `level4-installer.exe` | **`install_completed / high`**（`ev=[S2+A1]`） |
| `level3.7z` / `level2.zip` / `01-三层嵌套.7z` | `install_completed` |
| `level4-payload.txt` | `skipped` |

**默认 3 层深度限制内成功触达最内层安装器并装成**，F6 这条不需要动。耗时仅 5.9 s。

## 三、光盘映像 ISO（10 个）· 8/10 分类正确，安全断言全过

### 3.1 关键安全断言：全部通过 ✅

| ISO | 断言 | 实测 |
|---|---|---|
| `A26-03-os_install_media.iso` | **全程不执行任何文件** | ✅ `entries=0`、`iso=skipped`、0 个 attempt |
| `A26-04-media_disc.iso` | 不执行 | ✅ `entries=0`、`iso=skipped` |

这是 A26 里最重要的一条，**结果是好的**。

### 3.2 入口选择与回退 · 全部符合 ✅

```text
A26-01-installer_media.iso   install.bat -> triggered, setup.exe -> install_completed
A26-02-malware_lure.iso      发票明细.lnk -> install_completed        （.lnk 最高优先 ✅）
A26-06-garbled-names.iso     install.bat + setup.exe -> install_completed（乱码名不影响 ✅）
A26-08-deep-longpath.iso     install.bat + setup.exe -> install_completed（8 层深目录 ✅）
A26-07-autorun-missing.iso   normal-setup.exe -> install_completed     （autorun 失效回落 ✅）
A27-09-UDF-only.iso          iso_strategy_used = extract               ✅
A27-10-截断损坏.iso            media_kind=null, iso=failed, 不阻塞后续   ✅
```

### 3.3 两处 `media_kind` 不符 ❌

- `A26-05-data_disc.iso` → 实测 `installer_media`（盘里真有 `setup.exe`，属**口径待裁决**）；
- `A26-07-autorun-missing.iso` → 实测 `data_disc`（**行为对、分类错**：有 `autorun.inf` + 安装器仍应判 `installer_media`）。

详见 [ISSUE-32](../../../reports/issues/ISSUE-32-ISO介质分类与清单不符.md)。

## 四、本轮新开条目

- **[ISSUE-31](../../../reports/issues/ISSUE-31-summary.total包含解压子项导致计数不符.md)**（中）：`total` 混入解压子项，批量计数契约失效；
  并记录 5 个 `.txt` 被当文档打开各超时一次。
- **[ISSUE-32](../../../reports/issues/ISSUE-32-ISO介质分类与清单不符.md)**（中）：ISO `media_kind` 2/10 与清单不符。

## 五、复现命令

```powershell
$Exe = "<DESKTOP>\AutoTrigger.exe"
$S   = "<SUITE_ROOT>\samples"
# 批量
& $Exe --input "$S\15-批量与嵌套\A6-批量50文件" --output ".\batch50.json" --timeout 120 --log-level debug --no-lock
# ISO 逐个
Get-ChildItem "$S\13-光盘映像 ISO" -File | ForEach-Object {
  & $Exe --input $_.FullName --output ".\$($_.BaseName).json" --timeout 120 --no-lock
}
```
