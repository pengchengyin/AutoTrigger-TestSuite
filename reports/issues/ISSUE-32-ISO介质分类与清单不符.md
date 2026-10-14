# ISSUE-32｜ISO 介质分类 `media_kind` 有 2/10 与清单不符（中）

- **严重级别**：中（介质性质是 A26 的核心产出；错分类会连带影响入口优先级与安全策略）
- **状态**：待修复
- **关联验收项**：A26 ⑥ / F18
- **发现环境**：已提权，10 个 ISO 逐个跑

## 一、结果总览：8/10 正确

| ISO | 清单预期 | 实测 `media_kind` | 判定 |
|---|---|---|---|
| `A26-01-installer_media.iso` | `installer_media` | `installer_media` | ✅ |
| `A26-02-malware_lure.iso` | `malware_lure` | `malware_lure` | ✅ |
| `A26-03-os_install_media.iso` | `os_install_media` | `os_install_media` | ✅ |
| `A26-04-media_disc.iso` | `media_disc` | `media_disc` | ✅ |
| **`A26-05-data_disc.iso`** | **`data_disc`** | **`installer_media`** | ❌ |
| `A26-06-garbled-names.iso` | `installer_media` | `installer_media` | ✅ |
| **`A26-07-autorun-missing.iso`** | **`installer_media`** | **`data_disc`** | ❌ |
| `A26-08-deep-longpath.iso` | `installer_media` | `installer_media` | ✅ |
| `A27-09-UDF-only.iso` | （UDF-only） | `installer_media` + `strategy=extract` | ✅ |
| `A27-10-截断损坏.iso` | 两轨皆失败 | `media_kind=null`、ISO 自身 `failed` | ✅ |

## 二、两处不符的具体情况

### 2.1 `A26-05-data_disc.iso` → 被判成 `installer_media`

用 7-Zip 看盘内容（`7z l`）：

```text
docs\file00.txt … docs\file05.txt
photos\image01.jpg
readme.txt
setup.exe            <-- 盘里确实有一个 setup.exe
```

工具因此判 `installer_media`，并**执行了 `setup.exe` → `install_completed`**。

**这里需要你裁决口径**：盘里既然有 `setup.exe`，判成 `installer_media` 并不算错；
但样本清单把它定义为 `data_disc` 并期望"走通用 F17 流程"。
**要么样本不该放 setup.exe，要么 `media_kind` 的判据要说明"有安装器就以 installer_media 优先"。**

### 2.2 `A26-07-autorun-missing.iso` → 被判成 `data_disc`

盘内容：

```text
autorun.inf            （指向不存在的 missing-installer.exe）
normal-setup.exe
readme.txt
```

- **行为是对的** ✅：没有执行不存在的目标，回落到 `normal-setup.exe` 并 `install_completed`；
- **分类是错的** ❌：有 `autorun.inf` + 可执行安装器，清单期望 `installer_media`，实测 `data_disc`。

推测实现里有一条"autorun 目标缺失就把介质降级为 data_disc"的逻辑——
但按 F18 的语义，介质性质应看**盘里有什么**，而不是**autorun 是否有效**。autorun 失效只影响"入口优先级"，
不应改变介质性质。

## 三、期望行为

1. **`A26-07` 修正**：`autorun.inf` 存在（无论目标是否有效）+ 存在安装器 → 仍应判 `installer_media`，
   autorun 失效只让该条目从 P0 候选里剔除；
2. **`A26-05` 明确口径**：在 PRD/样本里二选一——
   要么该盘不放 `setup.exe`（保持纯数据盘），要么承认"含安装器的数据盘判 installer_media"并同步改清单；
3. **`media_kind` 判据文档化**：把每种介质性质的判定输入（目录特征、autorun、扩展名集合）写清楚，
   便于逐条回归。

## 四、本组**做对了**的关键安全断言（回归时保护）

| 断言 | 实测 |
|---|---|
| `A26-03-os_install_media` **全程不执行任何文件** | ✅ `entries=0`，`iso=skipped`，无任何 attempt |
| `A26-04-media_disc` 不执行 | ✅ `entries=0`，`iso=skipped` |
| `A26-02-malware_lure` 最高优先执行 `.lnk` | ✅ `发票明细.lnk -> install_completed` |
| `A26-01` 优先 `setup.exe` | ✅ `install.bat` + `setup.exe` 执行，`install_completed` |
| `A26-06` 乱码名仍识别 | ✅ `setup.exe -> install_completed` |
| `A27-09` UDF-only 走 extract | ✅ `iso_strategy_used=extract` |
| `A27-10` 两轨皆失败且**不阻塞** | ✅ `failed`、`media_kind=null`，后续 ISO 正常 |

## 五、证据文件

| 证据 | 位置 |
|---|---|
| 10 个 ISO 的结果 | `elevated-batch/13-01.json` … `13-10.json` |
| 盘内容核对 | `7z l "...\A26-05-data_disc.iso"` / `A26-07-autorun-missing.iso` |
