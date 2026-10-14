# ISSUE-10｜`document_host` 分支把"文档"本体当程序执行，未按识别类型找宿主（中）

- **严重级别**：中（错误执行 + 错误分类，存在安全与判定双重问题）
- **状态**：待修复
- **关联验收项**：F7 / F8 / A5

## 一、问题现象

`samples\09-类型识别与伪装\实际是PDF的exe.exe`（真实魔数 `%PDF`，扩展名却是 `.exe`）：

- 工具识别正确：`detected_type = document`、`extension_disguised = true`；
- 但随后走 `document_host` 分支时，**直接把文件本体当程序启动**，报 Windows 的"不是有效程序"错误：

```text
fork/exec ...\实际是PDF的exe.exe:
  This version of %1 is not compatible with the version of Windows you're running.
  Check your computer's system information and then contact the software publisher.
```

同样问题出现在 `实际是文本的exe.exe`（`detected_type = unknown`，同样被 `document_host` 当程序执行）。

## 二、证据（`evidence\09-group.json`）

```text
实际是PDF的exe.exe
   type=document  disguised=true  status=failed  reason=non_executable_entry
     attempt: method=document_host
              cmd="C:\\...\\实际是PDF的exe.exe"
              exit=null
              err=fork/exec C:\\...\\实际是PDF的exe.exe: This version of %1 is not
                  compatible with the version of Windows you're running. ...

实际是文本的exe.exe
   type=unknown   disguised=true  status=failed  reason=non_executable_entry
     attempt: method=document_host
              cmd="C:\\...\\实际是文本的exe.exe"
              exit=null
              err=(同上)
```

注意 `selection_reason` 已经是 `non_executable_entry`（判定为"不可执行入口"），却仍然发起了 `document_host` 执行尝试，**判据与动作自相矛盾**。

样本清单的预期是：

> `实际是PDF的exe.exe` | `%PDF` | **按文档处理**，`extension_disguised: true`
> `实际是文本的exe.exe` | 无魔数 | **未知格式兜底（F8），不得当成 PE 执行**

## 三、期望行为

1. **宿主按"识别出的内容类型"解析，而不是按扩展名**：`document` → 用 ShellExecute `open`（或显式查 `HKCR\.pdf\OpenWithProgids`）拉起 PDF 宿主；识别不出宿主时记 `skipped: no_host_app`（与 `08-无宿主扩展名.atdoc` 同一分支）。
2. **绝不能对非 PE 文件调用 `CreateProcess`**：`CreateProcess` 只应作用于真实 PE；文档/未知类型统一走 ShellExecute + 关联程序。
3. **判据与动作必须一致**：既然 `selection_reason = non_executable_entry`，就不应再产生执行类 attempt。

## 四、影响面

所有"扩展名与实际内容不符"的样本（伪装、下载到的错误扩展名文件、`.exe` 实为压缩包/文档）都会走进这条错误路径；在开启关联程序的情况下还可能意外弹出编辑器或触发 SmartScreen。
