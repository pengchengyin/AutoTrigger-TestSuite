# ISSUE-11｜合成样本载荷 `app.exe` 不是有效 PE，`artifact_check=failed` 把 MSI-01 压到 medium（中，口径问题）

- **严重级别**：中（不是工具逻辑错，而是"样本载荷"与"清单预期置信度"互相矛盾，会让回归结论不可信）
- **状态**：待确认口径
- **关联验收项**：A13 / A29 ② / F15

## 一、问题现象

`MSI-01-标准安装成功.msi` 的安装**是成功的**（文件、注册表、ARP 一应俱全），但工具的 `artifact_check` 判 **failed**，于是最终置信度只有 `medium`，与样本清单写死的 `install_completed / high` 不符。

## 二、证据

### 2.1 安装确实成功

ARP 卸载项：

```text
[HKLM:] AT Synthetic MSI 01 | ver=1.0.0.0 | uninstall=MsiExec.exe /X{9B8F9F05-C520-40EB-91E3-C7B339D0749A}
```

落盘文件（`C:\Program Files\ATSynthMsi01`，来自 `_build\wix\MSI-01-标准安装成功.wxs` 的 `INSTALLFOLDER`）：

```text
 65538  app.exe
 98306  core.dll
   523  readme.txt
262155  resources.dat
```

注册表哨兵：

```text
HKLM\SOFTWARE\AT-TestSuite\MSI01
  Installed       : 1
  Version         : 1.0.0.0
  InstallLocation : C:\Program Files\ATSynthMsi01\
```

### 2.2 但 `app.exe` 不是可运行的 PE

```text
第一行为 PowerShell 运行 app.exe 的报错：
  Start-Process : 由于出现以下错误，无法运行此命令:
  指定的可执行文件不是此操作系统平台的有效应用程序。
```

直接读 PE 头（`_build\payload\app.exe`）：

```text
first 16 bytes: 4D 5A BA 48 4B D3 DC 1B CD 6E C5 09 C0 19 F2 B4
e_lfanew = 0xD9B38754
NO PE SIGNATURE (not a valid PE)
（对照：C:\WINDOWS\System32\notepad.exe  Machine = 0x8664）
```

即：`app.exe` 只有一个 `MZ` 前两字节，`e_lfanew` 是垃圾值，**根本没有 PE 签名**——它是刻意造的"假载荷"。

### 2.3 置信度差异只来自 `artifact_check`

| 样本 | `artifact_check` | 置信度 |
|---|---|---|
| MSI-01（装的是假 `app.exe`） | `failed` | medium |
| putty（装的是真 `putty.exe`） | `ok` | high |

两者其余证据完全同级（都有 `S1+S2+S3+S4`）。

## 二之四、★ 同一个 `artifact_check` 还在拖累 A29 组

在 `11-安装成功判定` 组里，凡是装这个假 `app.exe` 的样本，`artifact_check` 全是 `failed`，
置信度被压到 `medium` / 状态被降到 `install_unverified`：

| 样本 | `artifact_check` | 实测 | 清单预期 |
|---|---|---|---|
| `A29-03-标准安装-落盘+卸载项.exe` | （被黑名单跳过，见 ISSUE-03） | `skipped` | `install_completed / high` |
| `A29-05-绿色便携-仅落盘.exe` | `failed` | **`install_unverified / low`** | **`install_completed / high`** |
| `A29-07-反证据-装后回滚.exe` | `failed` | `install_completed / medium` | `install_partial` |
| `A29-10-已安装检测-幂等.exe` | `failed` | `install_completed / medium` | `install_completed` |
| `19-...\MSI-01` / `MSI-04` / `MSI-05` | `failed` | `install_completed / medium` | `high` |

**注意 `A29-05`**：它每一条 attempt 都拿到了 `S2（新增 13 个文件）`，
按 F15.1 的 S 级证据本应判 `install_completed/high`（清单也这么写），
但因为 `artifact_check=failed` 被降成 `install_unverified/low`。

## 三、结论与建议

**工具的行为本身是可辩护的**（"主程序根本跑不起来"确实是弱信号），但这条口径会让**所有**装载 `_build\payload\app.exe` 的合成样本（INNO-*、NSIS-*、MSI-*）都拿不到 `high`，回归时会到处报"置信度不符预期"。

建议二选一：

1. **修样本**（推荐）：把 `_build\payload\app.exe` 换成**真实可运行的 PE**（例如一个最小 Win32/Go/Console 探针，运行后写哨兵并退出 0）。这样 `artifact_check` 才能给出有意义的信号，`S1+S2+S3+S4+artifact_ok` 才能稳定判 `high`。
2. **修口径**：明确 `artifact_check` 只是在**能确证主程序存在但不可运行**时降级；当 `S1+S3+S4` 同时成立时不应降级，或在结果里输出 `notes: "artifact_not_runnable"` 让使用者自行判断。

无论选哪个，都建议在 `install_verify` 里把 `artifact_check` 的判定规则写进文档（当前 `--dump-config` 只暴露 `launch_check:false`，看不出它与置信度的关系）。
