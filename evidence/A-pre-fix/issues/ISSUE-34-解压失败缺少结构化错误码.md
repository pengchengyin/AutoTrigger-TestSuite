# ISSUE-34｜解压失败没有结构化错误码，只有裸的 7z 输出（与 `extract_size_exceeded` 不一致）（低）

- **严重级别**：低（不影响拦截效果，但影响"失败可诊断性"与按码分类统计）
- **状态**：待修复
- **关联验收项**：F6⑦ / A16 / A34
- **发现环境**：已提权，样本 `14-跳过与兜底` 逐个跑

## 一、问题现象

同样是"7-Zip 处理失败"，工具的产出**两种风格**：

### 1.1 结构化的（好）

```text
10-zip炸弹-解压超2G.zip
  final_status = failed
  notes = "extract_size_exceeded: declared size exceeds 2147483648 bytes"     <-- 有码有值
```

### 1.2 裸文本的（不一致）

```text
04-损坏的zip.zip
  final_status = failed
  notes = "C:\...\7z.exe exited 2: \r\nERROR: ... Open ERROR: Cannot open the file as [zip] archive\r\nERRORS:\r\nIs not archive"

05-损坏的7z.7z
  notes = "... Open ERROR: Cannot open the file as [7z] archive ... Is not archive"

06-截断的zip.zip
  notes = "...7z.exe exited 2: "                     <-- 只剩一句，信息很少

07-加密zip.zip
  notes = "...7z.exe exited 2: ERROR: Wrong password : secret.txt"

08-加密7z-文件名加密.7z
  notes = "...ERROR: Cannot open encrypted archive. Wrong password?\r\nERRORS:\r\nHeaders Error"
```

对全部 6 个文件做 grep：

```text
extract_failed   : 0 次命中
extract_size_exceeded : 1 次命中（只有 zip 炸弹）
```

也就是说：**清单里写的 `extract_failed` 这个码，工具从未产出**；损坏/截断/加密三类失败全都被塞进
`notes` 的原始 `stderr` 里。

## 二、为什么值得修

1. **无法按码统计**：想知道"这批样本里有多少是因加密失败、多少是因文件损坏"，只能去正则匹配 7z 的英文措辞；
2. **措辞会变**：7-Zip 版本升级后 `Is not archive` / `Wrong password` 字面量可能变化，按文本匹配很脆；
3. **`notes` 被当垃圾桶**：`notes` 字段现在既放机器可读的码（zip 炸弹），又放人类可读的整段 stderr，
   Schema 上无法区分；
4. **`06-截断的zip.zip` 信息量过少**：`notes` 里只有一句 `"7z.exe exited 2: "`，
   连错误原因都没有——使用者无从判断。

## 三、期望行为

1. **统一产出结构化错误码**（建议放 `attempts[].error_code` 或 `results[].failure_code`），至少覆盖：
   `extract_failed` / `extract_size_exceeded` / `extract_password_required` / `extract_truncated` / `extract_unsupported`；
2. **原始 stderr 另存**：放进 `notes` 或专门的 `diagnostics` 字段，并**截断到合理长度**（现在把整个 7z 输出塞进 `notes`）；
3. **`06-截断` 至少要带上 7z 的退出码与最后一行错误**（当前只有 "exited 2: "）；
4. 与 zip 炸弹的处理保持一致——它是目前唯一"做对了"的（有码 + 关键数值）。

## 四、顺带确认：这一组的核心断言是**通过**的

| 断言 | 实测 | 判定 |
|---|---|---|
| `01/02 空文件` → `skipped: empty_file` | 均 `skipped`，notes=`empty_file` | ✅ |
| `03 单字节文件` → `failed: untriggerable` | `failed`，notes=`untriggerable` | ✅ |
| `09 未知扩展名但 MZ 头` → 按 PE 执行 | `install_completed` | ✅ |
| 损坏/截断/加密 → 失败但**不阻塞后续样本** | 12 个样本全部处理完，无阻塞 | ✅ |
| **`10-zip炸弹` → 7z l 阶段拦下、不落盘** | `failed` + `extract_size_exceeded`；**磁盘只变化 0.1 MB** | ✅✅ |

zip 炸弹那条尤其漂亮：`freeBefore=28.62GB → freeAfter=28.62GB，`delta=0.1MB`，
即**在解压前就被拦住了**（F6⑥ / F17.1 达标）。

## 五、证据文件

| 证据 | 位置 |
|---|---|
| 各失败样本的 notes | `elevated-misc/14-04.json` … `14-08.json` |
| 结构化的对照（好例子） | `elevated-misc/14-99-zipbomb.json` |
| 磁盘前后对照 | `elevated-misc/_status.txt`（`freeBefore/freeAfter/deltaMB`） |
