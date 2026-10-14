# ISSUE-33｜自绘窗口的 OCR / 模板回退**从未触发**，`gui_actions = 0`（高）

- **严重级别**：高（自绘/非标准控件安装器**永远装不上**，而这类安装器在国产软件里非常常见）
- **状态**：待修复
- **关联验收项**：**A18 / A19 / F14.6 / DC7**
- **发现环境**：已提权，样本 `16-自绘界面-OCR专项\

## 一、问题现象

清单要求：

> `OWNERDRAW-自绘向导-浅色.exe`：窗口**没有任何子控件**（全部 GDI+ 自绘）→ UIA 必然拿不到控件树
> → **必须靠图像模板 / OCR 定位**"我接受协议 / 下一步 / 安装 / 完成"并点击；
> 对应 `gui_actions[].source` 应为 `template` 或 `ocr`（**不是** `uia`）；最终 `install_completed`

实测（OCR 引擎本次**状态正常**：`ocr_engine_status=ok`、`ocr_startup_ms=1008`）：

```text
final_status = install_partial   install_confidence = low
gui_actions  = 0          <-- 一个动作都没有
duration     = 171.8 s（68.7 + 103.1）
evidence     = [A3]
```

## 二、证据：窗口看到了，但"找按钮"只走了 UIA/Win32

日志里 **333 行**全都是同一句：

```text
[调试] 【界面】界面识别详情：窗口 "自绘界面安装向导 Synthetic"（PID 11332）
       未识别到可点击控件：关闭/button/可用=true/选中=false
```

也就是：UIA/Win32 只枚举到窗口标题栏那个 **"关闭"** 按钮，于是判定"没有可点击控件"，
**然后就一直在那里轮询到超时**。

### 2.1 OCR 一次都没被调用

对 `16-01.log` 做关键词统计：

```text
"识别来源"    : 0 行      <-- 没有任何动作带来源
"ocr_score"  : 0 行      <-- 没有任何 OCR 结果被使用
"截图"        : 0 行      <-- 没有为 OCR 截过图
"模板命中"    : 0 行
```

**唯一提到 OCR 的地方是最开始那条"内置图像模板为空：仍会使用 UIA/Win32 与 OCR 识别"的配置提示**，
之后 OCR 再没出现在任何一行日志里。

### 2.2 与能力清单对照

```text
capabilities.ocr                  = true
prereq.ocr_engine_status          = ok
prereq.ocr_startup_ms             = 1008
capabilities.builtin_templates    = false      （见 ISSUE-04：0 张模板）
```

即：**OCR 是就绪的，模板是空的**。按 F14.6 的设计，此时应走"OCR 兜底"，
但实际连 OCR 兜底都没发生——所以最终一条腿都没用上。

## 三、根因推断

判定链看起来是这样的：

1. 枚举窗口 → 找到 1 个控件（`关闭`）；
2. 因为"找到了控件对象"，就认为"这个窗口有控件树"，于是**不进入 OCR/模板通道**；
3. 但那唯一的控件是**非动作控件**（close），于是每轮都"无可点击控件"；
4. 循环直到 idle/硬超时。

**判据应该是"有没有 *动作型* 控件（接受/下一步/安装/完成）"，而不是"有没有任何控件"。**
只要没找到动作型控件，就应立刻升级到 模板 → OCR 通道。

## 四、期望行为

1. **回退条件改为"未找到动作型控件"**：UIA/Win32 拿不到 `accept/next/install/finish/ok` 任一动作时，
   立即尝试（a）内置模板 →（b）OCR 文本定位；
2. **OCR 必须真的被调用并留下痕迹**：`gui_actions[].source` 记 `ocr`、`ocr_score` 记置信度、
   识别细节里给出"识别到哪些文本 / 候选按钮坐标"；
3. **自绘窗口要有专属结果**：若模板与 OCR 都没识别出动作按钮，应记
   `gui_identify_failed`（清单对该分支也有明确要求："若无内置模板覆盖深色，则应显式记 `gui_identify_failed` 而不是乱点"），
   而不是静默 `install_partial`；
4. 与 [ISSUE-04](ISSUE-04-内置图像模板为空导致GUI兜底缺失.md) 一起修：模板补齐 + OCR 通道打通，缺一不可。

## 四之二、深色变体也一样，且**没有**记录 `gui_identify_failed`

```text
OWNERDRAW-自绘向导-深色.exe
  final_status = install_partial   conf = low
  gui_actions  = 0
  notes        = ""
```

清单对深色变体的要求是：

> 若内置模板未覆盖深色，则应**显式记 `gui_identify_failed`** 而不是乱点。

实测：**"不乱点"这一半做到了（`gui_actions=0`）**，但 `gui_identify_failed` 这个标记
在 `16-01/16-02` 的日志与 JSON 里**各出现 0 次**——完全没有记录。

也就是说：使用者拿到的只是一个 `install_partial`，**看不出"其实是识别失败"**。
这层语义对修复非常关键（"模板没覆盖 OCR 也没识别出来" ≠ "装了一半"）。

## 五、影响面

- `16` 组两个样本（浅色/深色）都会失败；
- 真实软件里**自绘安装器非常多**（国产工具、游戏启动器、部分 InstallShield 皮肤化向导），
  这条不修等于对它们完全无能为力；
- 与 ISSUE-04（模板为空）、ISSUE-05（OCR 启动抖动）叠加，构成"GUI 兜底三连"。

## 六、证据文件

| 证据 | 位置 |
|---|---|
| 结果（gui_actions=0） | `elevated-misc/16-01.json` |
| 333 行"未识别到可点击控件" | `elevated-misc/16-01.log` |
| OCR 就绪但未被使用 | 同上（`prereq` 段与全文关键词统计） |
| 模板为空 | `--capabilities` / ISSUE-04 |
