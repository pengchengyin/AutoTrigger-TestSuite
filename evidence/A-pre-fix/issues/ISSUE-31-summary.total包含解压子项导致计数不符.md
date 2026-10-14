# ISSUE-31｜`summary.total` 把压缩包解出的子项也算进去，批量总数 ≠ 输入文件数（中）

- **严重级别**：中（A6/A31 的计数契约被破坏；批量方无法用 total 对账"到底处理了几个输入"）
- **状态**：待修复
- **关联验收项**：A6 批量处理 / A31 ⑦ 计数守恒
- **发现环境**：已提权，样本 `15-批量与嵌套\A6-批量50文件`（目录正好 **50 个文件**）

## 一、问题现象

清单断言：

> `A6-批量50文件\`（50 个混合文件）→ **`summary.total == 50`**，且 **`by_status` 各项之和恒等于 `total`**

实测：

```json
"summary": { "total": 55,
  "by_status": { "failed":10, "installed":5, "skipped":5,
                 "timeout":5, "triggered":30,
                 "already_installed":0, "partial":0, "unverified":0 } }
```

- **`sum(by_status) = 55 == total`** ✅（计数守恒这一条是过的）
- **`total = 55`，而输入目录只有 50 个文件** ❌

## 二、多出来的 5 条是什么

目录里 `case05.zip / case15.zip / case25.zip / case35.zip / case45.zip` 各包含一个 `a.txt`，
工具把解压出来的子项也写成了独立结果：

```text
<DESKTOP>\<USER>\AppData\Local\Temp\AT-3269365168\a.txt -> skipped (non_executable_entry)
<DESKTOP>\<USER>\AppData\Local\Temp\AT-318485150\a.txt  -> skipped
<DESKTOP>\<USER>\AppData\Local\Temp\AT-2570396841\a.txt -> skipped
<DESKTOP>\<USER>\AppData\Local\Temp\AT-4171390726\a.txt -> skipped
<DESKTOP>\<USER>\AppData\Local\Temp\AT-1691017461\a.txt -> skipped
```

**50（输入）+ 5（解压子项）= 55**，正好对上。

## 三、为什么这是个问题

1. **`total` 语义不明**：它到底是"输入条目数"还是"处理过的实体数"？
   现在两者混在一起，任何"total == 输入数"的断言都会失败；
2. **对账困难**：批量跑 740 MB 样本时，无法用 `total` 判断是否漏处理了输入；
3. **与 `layout_analysis` 的口径也不一致**（`entries/excluded/skipped_after_success` 是另一套计数）。

## 四、期望行为

二选一（推荐第一种）：

1. **`total` 只统计输入条目**，解压子项单独放在嵌套结构里（例如每个容器结果带
   `children: [...]`，顶层 `summary` 另给 `expanded_total`）；
2. 或者保留现在的口径，但**在 schema 里明确写出** `total = 输入 + 解压展开后的实体数`，
   并同时提供 `input_total` 供对账。

无论哪种，都请把"A6-批量50文件 → total 应该是 50"这条清单断言与实现对齐。

## 五、顺带记录：这一组里 `.txt` 又被当文档打开（5 次超时）

```text
case03.txt -> killed_on_timeout
case13.txt -> killed_on_timeout
case23.txt -> killed_on_timeout
case33.txt -> killed_on_timeout
case43.txt -> killed_on_timeout
```

**5 个纯文本文件全部走到 `killed_on_timeout`**——正是 [ISSUE-24](ISSUE-24-包内readme被document_host打开并挂到超时.md)
（`document_host` 拉起居宿主却等它退出）在批量场景下的放大版。
一个含 5 个 readme 的目录就要白耗 5 次超时。

## 六、证据文件

| 证据 | 位置 |
|---|---|
| 批量结果（total=55） | `elevated-batch/15-batch50.json` |
| 逐条日志 | `elevated-batch/15-batch50.log` |
| 目录实际文件数 | `Get-ChildItem '...\A6-批量50文件' -File | Measure-Object` → 50 |
