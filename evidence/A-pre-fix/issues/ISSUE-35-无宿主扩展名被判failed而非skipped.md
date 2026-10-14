# ISSUE-35｜"无宿主扩展名"被判 `failed: untriggerable`，而非清单要求的 `skipped: no_host_app`（低）

- **严重级别**：低（分类/状态口径不一致，会把"没装宿主"误记成"文件无法处理"，污染失败率）
- **状态**：待修复
- **关联验收项**：F7 / A5（文档类兜底）
- **发现环境**：已提权，样本 `08-文档类` 逐个跑

## 一、问题现象

清单要求：

> `08-无宿主扩展名.atdoc` → **`skipped: no_host_app`**

实测：

```text
08-无宿主扩展名.atdoc
  detected_type = unknown
  final_status  = failed
  notes         = "untriggerable"
  attempts      = 0 个
```

**同一个"没有宿主程序"的处境，Office 格式走的是 `skipped`，这个走的是 `failed`。**

## 二、同组的对照（说明工具是"会"判 no_host_app 的）

```text
01-有效文档.pdf          -> triggered        platform_meta={"host_program":"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"}
02-Word文档.docx         -> skipped  notes="no_host_app"
03-Excel表格.xlsx        -> skipped  notes="no_host_app"
04-文档.rtf              -> skipped  notes="no_host_app"
05-老格式.doc            -> skipped  notes="no_host_app"
06-幻灯片.pptx           -> skipped  notes="no_host_app"
07-含宏文档.docm         -> skipped  notes="no_host_app"
08-无宿主扩展名.atdoc     -> failed   notes="untriggerable"      <-- 只有它不一样
```

> 环境说明：本机**没有安装 Office/WPS/LibreOffice**（`HKLM\SOFTWARE\Classes` 下 `.docx/.xlsx/.pptx/.doc/.rtf` 均无关联），
> 所以 02–07 判 `skipped: no_host_app` 是**正确**的；`01` 因为 `.pdf` 的 UserChoice = `MSEdgePDF`，
> 被正确识别为"有宿主"并记录到 `platform_meta.host_program` ✅。
> **只有 `.atdoc` 这一条口径不一致。**

## 三、差异从哪来

看起来是**两条不同的兜底路径**：

| 情况 | 路径 | 结果 |
|---|---|---|
| 扩展名**已知**（`.docx` 等）、但查不到关联程序 | "文档类型 + 无宿主" | `skipped: no_host_app` |
| 扩展名**未知**（`.atdoc`） | 落到"未知格式兜底" | `failed: untriggerable` |

清单对"未知扩展名且无从处理"的场景其实同时存在两种期望（F8 说未知格式兜底，F7 说无宿主记 `no_host_app`），
所以这里**需要明确优先级**：

- 若"扩展名未知"**且**"没有可打开的宿主" → 建议仍记 `skipped: no_host_app`（因为本质就是没宿主）；
- 若"扩展名未知"但**有**关联（例如用户装了某个自定义程序） → 走 `document_host`。

## 四、期望行为

1. **`.atdoc` 改判 `skipped: no_host_app`**（与 02–07 对齐），notes 写明"扩展名无关联程序"；
2. **把"无宿主"做成统一的判定点**，不要在"已知扩展名/未知扩展名"两条路径里给出不同状态；
3. 顺带把 `notes` 结构化（`no_host_app: .atdoc`），便于统计"哪些格式在本机打不开"。

## 五、证据文件

| 证据 | 位置 |
|---|---|
| 8 个文档样本的结果 | `elevated-doc/08-01.json` … `08-08.json` |
| 本机关联实况 | `cmd /c assoc .docx` → 无关联；`FileExts\.pdf\UserChoice` → `MSEdgePDF` |
