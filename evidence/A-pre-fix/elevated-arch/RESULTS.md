# 压缩包安装效果（已提权，06 组逐包单跑）

> 背景：06 组整体跑时触发 **ISSUE-20（Go 回调表耗尽崩溃）**，1613 条结果全丢。
> 本轮把每个压缩包**单独作为一个进程**重跑——既绕开了累积崩溃，也拿到了真实结果。

## 0. 结论

- **8/8 全部正常结束，0 崩溃**（8 个 console 里没有任何 `fatal error`）→ 反证 ISSUE-20 是**累积性**的：
  同一个 `putty-0.85-w64.zip`（解出数百文件）单独跑只用 185 s、正常收尾；混在 06 组里就崩。
- **压缩包递归是正确的**：一层 / 两层嵌套都能走到最内层并 `install_completed`。
- **压缩包里的安装器能装成**：`MobaXterm_Installer.zip` 里的 MSI 装成功（`S3`，high）。
- **主要问题集中在"便携工具集被当安装器"**（见 ISSUE-22）与 **S2/N5 证据不可归因**（见 ISSUE-21）。

## 1. 逐包结果

| # | 样本 | 规模 | 清单预期 | 实测 |
|---|---|---|---|---|
| 01 | `nssm-2.24.zip` | 36 条（32 skipped） | `triggered` 即可 | nssm.exe 被套 9 种参数、全 Usage 退出 → `install_partial` |
| 02 | `7z2501-extra.7z` | 23 条（16 skipped） | `triggered` 即可 | 7za.exe / 7za.dll / 7zxa.dll 多次 `install_partial` |
| 03 | `7z2600-x64-32bit.exe` | 1 条 | `install_completed` | `install_partial`："确定"已点击且无变化仍空转到 154 s |
| 04 | `嵌套包\01-一层嵌套.7z` | 3 条 | 触达最内层安装器 | **level4-installer.exe → install_completed / high ✅** |
| 05 | `嵌套包\02-两层嵌套.zip` | 4 条 | 触达最内层安装器 | **level4-installer.exe → install_completed / low ✅** |
| 06 | `putty-0.85-w64.zip` | 8 条（6 skipped） | `triggered`（便携包） | PAGEANT.EXE（常驻托盘）→ `killed_on_timeout` |
| 07 | `npp.8.8.1.portable.x64.zip` | 218 条（216 skipped） | 靠 S2 判成功（F15.8） | notepad++.exe → `install_partial / low`，只有 A3 |
| 08 | `MobaXterm_Installer.zip` | **1335 条**（1330 skipped） | `install_completed` | **内层 MSI → install_completed / high ✅** |

## 2. 本轮的三个关键证据

1. **单进程隔离不崩** → ISSUE-20 的根因锁定为"回调累计"，而不是"某个压缩包本身有毒"；
2. **`MobaXterm_Installer.zip` 内层 MSI 装成** → 证实 ISSUE-18 是"`03-MSI` 样本缺 `.dat`"；
3. **`S2` 与 `N5` 在 5+ 个条目上同现**（含**非压缩包**的 `7z2600-x64-32bit.exe`）→ 见 ISSUE-21。

## 3. 复现命令

```powershell
$Exe = "<DESKTOP>\AutoTrigger.exe"
$S   = "<SUITE_ROOT>\samples\06-压缩包"
# 关键：每个压缩包单独一个进程，避免回调表耗尽
Get-ChildItem $S -File | ForEach-Object {
  & $Exe --input $_.FullName --output ".\\$($_.BaseName).json" --timeout 180 --no-lock
}
```

## 4. 已知的规模问题

`MobaXterm_Installer.zip` 产生 **1335 条**逐文件结果、`npp.portable` 产生 **218 条**，
其中约 99% 是 `skipped`。这说明压缩包处理是"**全解压 + 全遍历 + 逐条判定**"，
既慢（`185 s/包`）也是 ISSUE-20 崩溃的燃料。建议按 F17/A25 的设计，
在 `7z l` 列清单阶段就挑出少量入口，而不是把整棵树都当样本。
