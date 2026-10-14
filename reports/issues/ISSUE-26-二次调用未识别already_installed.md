# ISSUE-26｜二次调用未识别 `already_installed`，`pre_installed` 恒为 false（高）

- **严重级别**：高（批量场景会反复重装同一个软件；也是 A31 ⑤ 第三方集成契约的核心）
- **状态**：待修复
- **关联验收项**：A31 ⑤ / A29-10 幂等 / F15.5
- **发现环境**：已提权，样本 `11-安装成功判定\A29-10-已安装检测-幂等.exe` 连续跑两次

## 一、问题现象

清单要求：

> `A29-10-已安装检测-幂等.exe`：第 1 次 `install_completed`；**第 2 次必须 `already_installed`**

实测：

| 运行 | final_status | confidence | `pre_installed` |
|---|---|---|---|
| 第 1 次 | `install_completed` | medium | **false** |
| 第 2 次 | **`install_partial`** | low | **false** |

**第 2 次既没有判 `already_installed`，也不认为"装前已存在"（`pre_installed=false`）。**

## 二、证据：产品确实已经装在机器上

```text
HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
    ATSynthetic A29-10 Idempotent    ver = 3.3.3
```

（该条目正是第 1 次安装写入的，第 2 次运行开始时它**已经存在**。）

而第 1 次运行的证据中也明确出现了它：

```text
p1-A29-10  [1] exit=0  artifact=failed
   ev = S1|ATSynthetic A29-10 Idempotent 3.3.3
        S2|新增 7 个文件或目录实体
        A1|进程正常退出（退出码 0），不单独证明安装成功
```

## 三、第 2 次运行的证据链（同时叠加了 ISSUE-21 的噪音）

```text
p2-A29-10
  [1..5] exit=0   ev = A1（只有退出码 0）
  [6..9] exit=0   ev = S2|新增 443 个文件或目录实体
                       N5|移除 47 个文件或目录实体
                       A1
final_status = install_partial / low
```

两个问题叠加：

1. **幂等检测缺失**（本条）：没有因为"产品已存在"而提前判 `already_installed`，
   反而又完整跑了一遍 9 次尝试；
2. **磁盘证据未归因**（[ISSUE-21](ISSUE-21-落盘证据无法归因且自相矛盾.md)）：
   `S2 +443 / N5 −47` 这一对**数量不等、方向相反**的证据直接把结果压成 `install_partial`。

## 四、期望行为

1. **任务开始就做已安装检测**：在采集基线快照时，若目标产品已在其卸载根中（**含 HKCU**，本例就在 HKCU），
   应立即置 `pre_installed = true` 并判 `already_installed`，不再执行安装。
2. **匹配口径要明确定义并写进文档**：按 `DisplayName + Publisher`？按 `UpgradeCode`？
   还是按安装目录？目前 `pre_installed` 永远为 false，说明这条判定实际上没实现或没接上。
3. **`A29-04` 已经证明 S1 是含 HKCU 的**（清单原文："只写 HKCU，验证 S1 含 HKCU"），
   所以数据是有的，只是没有用在"装前检测"上。
4. 幂等命中时应输出 `install_confidence = high` 并给出命中的卸载项（便于人工核对）。

## 五、影响面

- **批量场景**：`A6-批量50文件` / 真实软件批量跑时，已装过的软件会被反复重装，
  既慢又可能触发修复/升级弹窗；
- **第三方集成契约**：A31 ⑤ 明确要求"重复调用 → `already_installed`"，
  当前无法满足，集成方无法靠返回值做幂等。

## 六、证据文件

| 证据 | 位置 |
|---|---|
| 第 1 次 | `elevated-a29/p1-10-A29-10-已安装检测-幂等.json` |
| 第 2 次 | `elevated-a29/p2-A29-10-已安装检测-幂等.json` |
| 全组对照 | `elevated-a29/RESULTS.md` |
