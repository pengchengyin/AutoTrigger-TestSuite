# A29 安装成功判定（已提权，11 组逐个样本 + 关键样本二次运行）

> 13 个样本各自单独一个进程跑；`A29-09` / `A29-10` 额外跑了第二次（幂等 / 覆盖升级）。

## 0. 结论：13 个样本里只有 3 个完全符合清单预期

| 判定 | 数量 | 原因分布 |
|---|---|---|
| ✅ 完全符合 | 3 | `A29-02`、`A29-06` |
| ❌ 被**黑名单**跳过 | 4 | ISSUE-03（`A29-03/04/09/11`） |
| ❌ 被 `artifact_check` 压低 | 1 | ISSUE-11（`A29-05`） |
| ❌ 反证据/噪音导致方向错误 | 4 | ISSUE-25、ISSUE-21（`A29-01/07/08/12/11b`） |
| ❌ 幂等检测缺失 | 1 | ISSUE-26（`A29-10` 第 2 次） |

## 1. 逐条对照

| 样本 | 清单预期 | 实测 | 归属 |
|---|---|---|---|
| `A29-01-假成功bootstrapper` | `install_unverified / low` | `install_completed / low` | ISSUE-21（`A3` 噪音抬升） |
| `A29-02-纯退出码0` | `install_unverified / low` | `install_unverified / low` | ✅ |
| `A29-03-标准安装-落盘+卸载项` | `install_completed / high` | **`skipped`** | ISSUE-03 |
| `A29-04-per-user安装-HKCU卸载项` | `install_completed / high` | **`skipped`** | ISSUE-03 |
| `A29-05-绿色便携-仅落盘` | `install_completed / high` | `install_unverified / low` | ISSUE-11（`artifact_check=failed`） |
| `A29-06-反证据-失败码+回滚日志` | `install_partial / low` + conflicts | `install_partial / low`，conflicts=9 | ✅ |
| `A29-07-反证据-装后回滚` | `install_partial` | `install_completed / medium` | **ISSUE-25**（N6 被忽略） |
| `A29-08-退出码1603失败` | `failed` | `install_partial / low` | **ISSUE-25** |
| `A29-09-覆盖升级-字段变化` | 1st `install_completed` → 2nd `already_installed` | **两次都 `skipped`** | ISSUE-03 |
| `A29-10-已安装检测-幂等` | 2nd 必须 `already_installed` | 1st `install_completed / medium`；**2nd `install_partial / low`** | **ISSUE-26** |
| `A29-11-口径对照` | 口径相关 | **`skipped`** | ISSUE-03 |
| `A29-11b-宽松口径` | `install_completed / high` | `install_partial / low` | ISSUE-21 / ISSUE-25 |
| `A29-12-落盘到监控外目录` | `triggered` | `install_partial / low` | ISSUE-21 |

## 2. 本轮新开的条目

- **[ISSUE-25](../../issues/ISSUE-25-反证据N6被正向证据覆盖.md)**（高）：`N6（装后回滚）` 出现却判 `install_completed`；
  纯 `1603` 失败被判 `install_partial`。核心是 **N 级反证据没有真正参与合成**。
- **[ISSUE-26](../../issues/ISSUE-26-二次调用未识别already_installed.md)**（高）：重复调用未识别 `already_installed`，
  `pre_installed` 恒为 false——尽管产品就在 `HKCU\...\Uninstall` 里。

## 3. 两个被反复验证的"放大器"

1. **ISSUE-03（黑名单子串匹配）** 在本组一次干掉 4 个样本，是**单点影响最大**的问题；
2. **ISSUE-21（S2/N5/A3 不可归因）** 反复给出 `S2 +443 / N5 −47`、`S2 +10 / N5 −10` 这类证据，
   把判定推离预期方向。

> 换句话说：**A29 组的偏差大多不是"算法不会判"，而是"输入证据里有脏东西 + 候选样本被黑名单吃掉"。**
> 修 ISSUE-03 与 ISSUE-21 的性价比明显高于调整判定权重。

## 4. 复现命令

```powershell
$Exe = "<DESKTOP>\AutoTrigger.exe"
$D   = "<SUITE_ROOT>\samples\11-安装成功判定"
Get-ChildItem $D -File | ForEach-Object {
  & $Exe --input $_.FullName --output ".\$($_.BaseName).json" --timeout 180 --log-level debug --no-lock
}
# 幂等样本必须再跑一次
& $Exe --input "$D\A29-10-已安装检测-幂等.exe" --output ".\A29-10-2nd.json" --no-lock
```
