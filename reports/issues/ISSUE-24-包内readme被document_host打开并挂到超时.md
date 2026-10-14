# ISSUE-24｜包内 readme（`.txt`）被 `document_host` 打开并挂到超时（中）

- **严重级别**：中（每个带 readme 的包都可能白耗一次超时；且与"readme 指向不存在文件时不得执行动作"的要求冲突）
- **状态**：待修复
- **关联验收项**：A25-02 / F7 / F5
- **发现环境**：已提权，样本 `10-入口分层与黑名单\A25-02-readme指向不存在文件`

## 一、问题现象

样本设计（见清单）：

> `A25-02-readme指向不存在文件\`：readme 指向 `notexist-installer.exe`（不存在）→ **不得产生任何执行动作**；
> 仅剩的 `unrelated.exe` 走 P5 兜底

实测：

```text
unrelated.exe    -> install_completed          （合理）
安装说明.txt      -> killed_on_timeout          （❌ 不该有执行动作）
    reason      = non_executable_entry
    detected    = unknown
    attempt[1]  method=document_host
                cmd="C:\Program Files\WindowsApps\Microsoft.WindowsNotepad_...\Notepad.exe"
                result=killed_on_timeout  dur=67.3s  err=idle_timeout
```

**工具把这个 `.txt` 当作文档类条目，用 `document_host` 拉起了系统记事本，然后一直等它退出，
67.3 秒后按 `idle_timeout` 强杀。**

## 二、为什么这是个问题

1. **判据与动作矛盾**：`selection_reason` 已经是 `non_executable_entry`，却仍然产生了执行动作
   （与 [ISSUE-10](ISSUE-10-document_host直接执行非可执行文档本体.md) 同一类）。
2. **`document_host` 的等待语义错误**：记事本这类**常驻编辑器**打开后不会自动退出，
   按"等进程结束"来判定必然走到超时。实测 67.3 s 纯浪费。
3. **与清单要求冲突**：本条明确要求"不得产生任何执行动作"。
4. **行为不一致**：同一批实验里，`A25-01` 的 `安装说明.txt` 是 `skipped`（`att=0`），
   而 `A25-02` 的同类文件却被执行了——**同一类文件两种处理**，说明这个分支缺少一致规则。

## 三、期望行为

1. **readme 类文件只用于"读取提示"，不应进入可执行路径**：
   若要用它，就用文本读取解析其中的安装器文件名（这正是"readme 指示入口"的用途），
   读取后即结束，不得 `ShellExecute` 打开。
2. **`document_host` 不应"等进程退出"**：文档类宿主（记事本/Word/PDF 阅读器）都是常驻进程，
   正确做法是"启动后确认已拉起即记 `triggered`"，或给一个很短的确认窗口，而不是等 idle 超时。
3. **`non_executable_entry` 必须无执行动作**：把这条不变量写成断言。

## 四、证据文件

| 证据 | 位置 |
|---|---|
| 结果 JSON | `elevated-a25/02-A25-02-readme指向不存在文件.json` |
| 日志（`document_host` + idle_timeout） | `elevated-a25/02-A25-02-readme指向不存在文件.log` |

## 五、同批实验的其它观察（供参考，各见独立条目）

- **A25-03 架构优先 —— 顺序正确 ✅**：`选用入口` 的顺序是 `setup_x64.exe → install.bat → setup_x86.exe`，
  满足"不得先出现 x86"。但 **x64 装成后仍然继续执行了 x86**（`skipped_after_success=0`），建议成功后跳过异架构。
  另外该样本的哨兵写成了字面量 `ARCH-CHOSEN-%PROCESSOR_ARCHITECTURE%`（变量没展开），
  所以清单里"哨兵出现 ARCH-x64"这条**实际上无法验证**——属样本缺陷。
- **批量场景被放大 5 倍 ⚠️**：`15-批量与嵌套\A6-批量50文件` 里的 5 个纯文本文件
  （`case03/13/23/33/43.txt`）**全部走到 `killed_on_timeout`**，即 5 次超时；
  同目录的 `case04.pdf` 等文档类也只是 `triggered`。见 [ISSUE-31](ISSUE-31-summary.total包含解压子项导致计数不符.md) §五。

- **A25-01 / A25-04 黑名单 —— 通过 ✅**：11 个黑名单陷阱全部列入 `excluded`，
  跑完后 `C:\Users\Public\AT-SENTINEL` 下 **`VIOLATION-*.txt = 0 个**，铁证通过。
- **A25-04（.7z / .zip）—— 通过 ✅**：解压前就产出 `entries=51 / excluded=11`，符合 F17.1。
