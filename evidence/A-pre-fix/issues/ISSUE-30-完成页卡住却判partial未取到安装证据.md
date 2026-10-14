# ISSUE-30｜「完成安装后卡在完成页」被判 `install_partial`——已装成却取不到安装证据（高）

- **严重级别**：高（这恰恰是 ISSUE-16 的镜像场景，说明"超时 ≠ 没装成"的口径**不稳定**）
- **状态**：待修复
- **关联验收项**：A30 ④ / A29 / F15
- **发现环境**：已提权，样本 `12-超时与活动感知\A30-04-完成安装后卡在完成页.exe`

## 一、问题现象

清单要求：

> `A30-04-完成安装后卡在完成页.exe` → **`install_completed`**（notes 注明"超时终结但已取得安装证据"），
> 验证"**超时 ≠ 没装成**"（A30 ④）

实测：

```text
final_status = install_partial   install_confidence = low
notes        = ""
duration     = 189 s
install_evidence = [A3]                      <-- 只有一条无来源的 A3
attempt[1] killed_on_timeout  dur= 75.4s  err=idle_timeout
attempt[2] killed_on_timeout  dur= 85.6s  err=idle_timeout
attempt[3] killed_on_timeout  dur= 27.9s  err=deadline_or_interrupt
```

**既没有 `S1（卸载项）` 也没有 `S2（落盘）`**，所以"已取得安装证据"这条根本无从成立，
最终被判 `install_partial / low`，notes 也为空。

## 二、与 `INNO-09` 形成矛盾对照

同一个"卡在完成页"的形态，在合成 Inno 组里是**对的**：

```text
elevated/17-group.json
  INNO-09-卡在完成页-超时验证.exe
    final_status = install_completed / high
    notes = "terminated on timeout; installation evidence still collected"
    evidence = S1|ATSynthetic A30-04 DonePage + S1|Inno 09 Hanger + S2|新增 23 个文件
```

（注：`INNO-09` 的证据里出现了 `ATSynthetic **A30-04** DonePage` ——和本条是同一个产品的不同形态。）

所以规则本身存在且能生效，**问题在于 `A30-04` 这条路径上没能采到 S1/S2**。可能原因：

1. 该样本的落盘/卸载项写入发生在**基线快照之后的窗口之外**，被 tool 的稳定期窗口错过；
2. 或者写入的目录不在 `watch_dirs` 覆盖范围内；
3. 或者被 ISSUE-08 的"快照预算触顶、负向证据禁用"连带影响。

## 三、期望行为

1. **先查明 S1/S2 为何缺失**：这是判定链的输入问题，修好它本条的判定自然会对；
2. **"超时终结 + 有安装证据"要稳定生效**：与 `INNO-09` 对齐，notes 必须写明；
3. **即使证据不足，也不应静默判 partial**：至少要说明"未采到安装证据"的原因（快照预算/排除目录/权限），
   便于区分"真没装"和"没看见"。

## 四、证据文件

| 证据 | 位置 |
|---|---|
| A30-04（缺失证据） | `elevated-a30/04-A30-04-完成安装后卡在完成页.json` |
| 对照：INNO-09（正确） | `elevated/17-group.json` |
| 快照预算告警 | `evidence/07-group.log`（ISSUE-08） |
