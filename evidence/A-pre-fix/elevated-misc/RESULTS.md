# 自绘界面 OCR（16 组）与 跳过/兜底（14 组）实测（已提权）

> 本轮同样带防休眠守卫。`14` 组逐个跑，**zip 炸弹放最后并盯磁盘**。

## 一、16 组 · 自绘界面 OCR 专项：❌ 两个样本都失败

| 样本 | 清单预期 | 实测 |
|---|---|---|
| `OWNERDRAW-自绘向导-浅色.exe` | `gui_actions[].source` 为 `template`/`ocr`，最终 `install_completed` | **`install_partial / low`，`gui_actions = 0`**，182.5 s |
| `OWNERDRAW-自绘向导-深色.exe` | 同上；若无模板须显式记 `gui_identify_failed` | `install_partial / low`，`gui_actions = 0`，182.1 s |

**根因**（详见 [ISSUE-33](../../../reports/issues/ISSUE-33-自绘窗口OCR模板回退从未触发.md)）：

```text
[调试] 【界面】界面识别详情：窗口 "自绘界面安装向导 Synthetic"（PID 11332）
       未识别到可点击控件：关闭/button/可用=true/选中=false
（同一句重复 333 次，直到超时）
```

- UIA/Win32 只枚举到标题栏的 **"关闭"** 按钮，就认为"这个窗口没有可点击控件"，然后一直轮询；
- **OCR 一次都没被调用**：日志里 `识别来源` / `ocr_score` / `截图` 各 0 行，
  尽管本次 `ocr_engine_status = ok`、`ocr_startup_ms = 1008`；
- `gui_identify_failed` 在日志与 JSON 里**各 0 次**——连"识别失败"都没记。

> 结论：**"模板为空 + OCR 回退不触发" = 自绘安装器完全无解**（ISSUE-04 + ISSUE-33 叠加）。

## 二、14 组 · 跳过与兜底：核心断言全部通过 ✅

| 样本 | 清单预期 | 实测 | 判定 |
|---|---|---|---|
| `01-空文件.exe` / `02-空文件.dat` | `skipped: empty_file` | `skipped`，notes=`empty_file` | ✅ |
| `03-单字节文件.bin` | `failed: untriggerable` | `failed`，notes=`untriggerable` | ✅ |
| `04/05/06 损坏/截断压缩包` | 失败且**不阻塞后续** | `failed`（notes 含 7z 原文） | ✅ |
| `07/08 加密压缩包` | 失败 | `failed`（`Wrong password` / `Headers Error`） | ✅ |
| `09-未知扩展名但MZ头.qwerty` | 按 PE 执行 | `install_completed` | ✅ |
| `未知扩展名-MZ头.bin` / `无扩展名文件` | — | `install_completed` / `install_unverified` | — |
| **`10-zip炸弹-解压超2G.zip`** | **`extract_size_exceeded`，7z l 阶段拦下、不落盘** | `failed` + `extract_size_exceeded: declared size exceeds 2147483648 bytes` | ✅✅ |

### 2.1 zip 炸弹：磁盘实测证据

```text
freeBefore = 28.62 GB
freeAfter  = 28.62 GB
delta      = 0.1 MB          <-- 根本没落盘
耗时       = 1.1 s           <-- 在 7z l 预检阶段就被拦下
```

这是本轮最有价值的一条**正面结论**：F6⑥ / F17.1 的"解压前预判"确实生效了。

### 2.2 唯一的瑕疵：错误码不结构化

同一个失败域里，只有 zip 炸弹给了机器可读的码：

```text
14-99  notes = "extract_size_exceeded: declared size exceeds 2147483648 bytes"   <-- 有码
14-04  notes = "7z.exe exited 2: ERROR: ... Is not archive"                       <-- 裸文本
14-06  notes = "7z.exe exited 2: "                                                <-- 只剩一句
```

`extract_failed` 在 6 个文件里**0 次命中**。详见 [ISSUE-34](../../../reports/issues/ISSUE-34-解压失败缺少结构化错误码.md)。

## 三、本轮新开条目

- **[ISSUE-33](../../../reports/issues/ISSUE-33-自绘窗口OCR模板回退从未触发.md)**（高）：自绘窗口 OCR/模板回退从未触发，`gui_actions=0`，
  且未记 `gui_identify_failed`。
- **[ISSUE-34](../../../reports/issues/ISSUE-34-解压失败缺少结构化错误码.md)**（低）：解压失败无结构化错误码，与 zip 炸弹的处理不一致。

## 四、复现命令

```powershell
$Exe = "<DESKTOP>\AutoTrigger.exe"
$S   = "<SUITE_ROOT>\samples"
Get-ChildItem "$S\16-自绘界面-OCR专项" -File | ForEach-Object {
  & $Exe --input $_.FullName --output ".\$($_.BaseName).json" --timeout 180 --log-level debug --no-lock
}
# 14 组：炸弹单独跑并盯磁盘
$bomb = "$S\14-跳过与兜底\10-zip炸弹-解压超2G.zip"
(Get-PSDrive C).Free / 1GB
& $Exe --input $bomb --output ".\zipbomb.json" --timeout 180 --log-level debug --no-lock
(Get-PSDrive C).Free / 1GB      # 必须几乎不变
```
