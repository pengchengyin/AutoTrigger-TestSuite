# ISSUE-25｜反证据（N 级）被正向证据覆盖：N6"装后回滚"仍判 `install_completed`（高）

- **严重级别**：高（把"装完又删掉"的失败场景报成"安装成功"，是最危险的误报方向）
- **状态**：待修复
- **关联验收项**：A29 ⑤ / F15.3 / N6 / N5
- **发现环境**：已提权，样本 `11-安装成功判定` 逐个跑

## 一、问题一：`N6（装后回滚）` 被判成 `install_completed`

样本 `A29-07-反证据-装后回滚.exe`（清单预期：**`install_partial`**，N4/N6：退出后约 2 s 删目录并销卸载项）：

```text
final_status = install_completed   install_confidence = medium
evidence_conflicts = []

attempt[1] silent_install exit=0 dur=3.0
   ev = N6|新增目录在稳定期消失，疑似回滚      <-- 明确的反证据
        S1|ATSynthetic A29-07 Rollback 1.0.0
        A1|进程正常退出（退出码 0），不单独证明安装成功
attempt[2] silent_install exit=0 dur=2.2
   ev = S1|ATSynthetic A29-07 Rollback 1.0.0
        A1|进程正常退出（退出码 0），不单独证明安装成功
```

**第 1 次尝试明明拿到了 `N6"新增目录在稳定期消失，疑似回滚"`，最终却判 `install_completed`。**

猜想（供参考，需工具侧确认）：判定合成时似乎**只看最后一次尝试的证据**，
而第 2 次尝试恰好没有复现回滚（因为第 1 次已经把目录删了，第 2 次"新增"的东西还在），
于是 N6 被丢弃、S1 单独成立 → `install_completed`。
这和 [ISSUE-16](ISSUE-16-走完GUI向导仍被硬超时判partial.md) 里"首次秒退的 N1 却一直挂着"正好相反——
**N 级证据到底按"跨尝试累积"还是"只看最后一次"，两次表现不一致。**

## 二、问题二：纯 `1603` 失败被判 `install_partial`

样本 `A29-08-退出码1603失败.exe`（清单预期：**`failed`**，N1，无任何副作用）：

```text
final_status = install_partial   install_confidence = low
evidence_conflicts = [N1:1603 ×9, N5:移除 10 个文件或目录实体]

attempt[1..9] 全部 exit=1603
   [4..8] ev = A3|监控文件或目录发生变化 + N1|1603
   [9]    ev = S2|新增 10 个文件或目录实体 + N5|移除 10 个文件或目录实体 + N1|1603
```

9 次尝试**全部 1603**（明确的失败码），却被 `install_partial`：

- `A3（目录发生变化）` 把结果从 `failed` 抬成了 `partial`；
- 第 9 次又出现 `S2(+10) + N5(−10)` 这一对**同数反向**的证据（见 [ISSUE-21](ISSUE-21-落盘证据无法归因且自相矛盾.md)）。

## 三、期望行为

1. **N 级反证据必须参与合成，且方向明确**：`N6（装后回滚）`、`N4（卸载项被移除）` 出现时，
   结果不应高于 `install_partial`；当前"最后一次尝试没有 N6 就丢掉"的做法等于让回滚证据随机失效。
2. **统一"跨尝试"口径**：要么所有证据都按"任一尝试取得即计入"，要么都按"最后一次"，
   并把规则写进文档。现在 ISSUE-16（N1 累积）与本条（N6 丢弃）**互相矛盾**。
3. **`A3` 不应单独把 `failed` 抬成 `partial`**：`A3` 只是"监控目录发生变化"，
   在 `N1` 明确失败码的情况下，需要更强的可归因副作用才能升格。
4. **同数反向的 S/N 对要拦截**：`S2(+10)` 与 `N5(−10)` 同时出现时应标记证据不可信（同 ISSUE-21 §四.4）。

## 四、A29 组整体对照（本轮实测）

| 样本 | 清单预期 | 实测 | 结论 |
|---|---|---|---|
| `A29-01-假成功bootstrapper` | `install_unverified / low` | `install_completed / low` | ❌ 被 `A3` 抬升 |
| `A29-02-纯退出码0` | `install_unverified / low` | `install_unverified / low` | ✅ |
| `A29-03-标准安装` | `install_completed / high` | **`skipped`** | ❌ 黑名单（ISSUE-03） |
| `A29-04-per-user` | `install_completed / high` | **`skipped`** | ❌ 黑名单（ISSUE-03） |
| `A29-05-绿色便携-仅落盘` | `install_completed / high` | `install_unverified / low` | ❌ `artifact_check`（ISSUE-11） |
| `A29-06-反证据-失败码+回滚日志` | `install_partial / low` + conflicts | `install_partial / low`，conflicts=9 | ✅ |
| `A29-07-反证据-装后回滚` | `install_partial` | `install_completed / medium` | ❌ **本条** |
| `A29-08-退出码1603失败` | `failed` | `install_partial / low` | ❌ **本条** |
| `A29-09-覆盖升级` | `install_completed` → `already_installed` | **`skipped`（两次都跳过）** | ❌ 黑名单（ISSUE-03） |
| `A29-10-已安装检测-幂等` | 第 2 次必须 `already_installed` | 第 1 次 `install_completed / medium` | ⚠️ 第 2 次待查 |
| `A29-11-口径对照` | 口径相关 | **`skipped`** | ❌ 黑名单（ISSUE-03） |
| `A29-11b-宽松口径` | `install_completed / high` | `install_partial / low` | ❌ |
| `A29-12-落盘到监控外目录` | `triggered` | `install_partial / low` | ❌ `N5` 噪音（ISSUE-21） |

**13 个样本里只有 3 个完全符合预期**，其余分别被黑名单、`artifact_check`、反证据合成、磁盘噪音拖偏。
这也说明：**工具"能装"之外，"能不能正确说自己装成了"同样是大问题。**

## 五、证据文件

| 证据 | 位置 |
|---|---|
| A29-07（N6 被忽略） | `elevated-a29/p1-07-A29-07-反证据-装后回滚.json` |
| A29-08（1603 判 partial） | `elevated-a29/p1-08-A29-08-退出码1603失败.json` |
| 全组对照 | `elevated-a29/RESULTS.md` |
