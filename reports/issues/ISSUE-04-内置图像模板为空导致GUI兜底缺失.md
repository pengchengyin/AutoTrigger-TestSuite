# ISSUE-04｜内置图像模板包为空（0 张），GUI 自动化的"模板"这条腿完全缺失（高）

- **严重级别**：高（GUI 兜底能力大幅缩水，直接影响"能自动安装的软件数量"）
- **状态**：待修复
- **关联验收项**：A32 内置资源包开箱即用 / A18 / F14.2 / F14.6

## 一、问题现象

工具随包宣称 `gui_automation.builtin_templates = true`，但**实际内置模板数量为 0**，导出出来的索引文件里明确写着"等待真实安装器截图"。

在完全没有 UIA 控件树的自绘安装器（`samples\16-自绘界面-OCR专项`）场景下，"模板匹配"这条路等于不存在，只剩 UIA/Win32 + OCR。

## 二、复现步骤

```powershell
.\AutoTrigger.exe --capabilities
.\AutoTrigger.exe --dump-resources C:\ATTest\atres
Get-Content C:\ATTest\atres\templates\templates.index.json
```

## 三、证据

### 3.1 `--capabilities` 输出

```text
[警告] 【任务】配置提示：内置图像模板为空：仍会使用 UIA/Win32 与 OCR 识别；
       如需更高命中率，请按 D17 补齐模板
```

```json
{"capabilities":{"builtin_resources":true,"builtin_templates":false,...},
 "resources":{"builtin_template_variants":0,"external_template_entries":0,
              "master_count":0,"template_acceptance_ready":false,
              "template_pack":"merged"}}
```

### 3.2 导出的模板索引（`--dump-resources`）

```json
{"resource_pack_version":"0.1.0",
 "status":"awaiting_real_installer_captures",
 "entries":[]}
```

### 3.3 生效配置（`--dump-config`）

```json
"gui_automation":{"enabled":true, ..., "template_pack":"merged","template_dir":"templates",
                  "template_min_similarity":0.86,"builtin_templates":true,
                  "dump_failed_shots":false}
```

配置说 `builtin_templates:true`，实际 `entries:[]`——**配置与运行结果自相矛盾**，且 `--capabilities` 用了 "false" 的写法，两处口径不一致。

### 3.4 与 OCR 叠加（见 ISSUE-05）

同一环境下 OCR 自检还会间歇失败，于是 `samples\16` 这类自绘向导同时失去模板与 OCR 两条腿，只剩概率很低的 UIA/Win32。

## 四、期望行为

1. **要么补齐模板**：把 Inno / NSIS / InstallShield / WiX 常见向导的"我接受 / 下一步 / 安装 / 完成"按钮截图（含浅色/深色、100%/125%/150% DPI）编入资源包；
2. **要么如实上报能力**：`--capabilities.builtin_templates` 与 `resources.*` 保持一致，并在 GUI 自动化开始时就输出一条"当前无模板可用，将仅依赖 UIA/Win32+OCR"的显著提示；
3. `--self-test templates` 在当前状态下的行为也应明确（空包应当报"无模板可测"而不是"通过"）。

## 五、备注

`--dump-resources` 导出的目录结构本身是好的（`templates/`、`keywords/`、`params/`、`exclude_entries.json`、`install_entries.json`、`magic.json`、`media_kinds.json`、`gui_rules.json`），补齐内容即可，不需要改架构。
