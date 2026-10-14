# ISSUE-07｜`summary.by_status` 的键名与 `final_status` 枚举不一致（中）

- **严重级别**：中（第三方集成/断言脚本会踩坑，属 A31 契约问题）
- **状态**：待修复
- **关联验收项**：A6 / A28 / A31 ⑦

## 一、问题现象

`--capabilities` 声明的 `supported_final_status` 与结果 JSON 里 `summary.by_status` 的键**不是同一套命名**：

```text
supported_final_status:
  install_completed  install_unverified  install_partial  already_installed
  triggered          killed_on_timeout   failed           skipped

summary.by_status:
  installed  unverified  partial  already_installed
  triggered  timeout     failed   skipped
```

而每条结果里的 `final_status` 用的又是**第一套**（`install_completed` / `install_partial` / `killed_on_timeout` ...）。

## 二、证据

### 2.1 `--capabilities`

```json
"supported_final_status":["install_completed","install_unverified","install_partial",
 "already_installed","triggered","killed_on_timeout","failed","skipped"]
```

### 2.2 任意一次结果 JSON 的 summary（`evidence\18-NSIS-01.json`）

```json
"summary":{"total":1,
  "by_status":{"already_installed":0,"failed":1,"installed":0,"partial":0,
               "skipped":0,"timeout":0,"triggered":0,"unverified":0},
  "flags":{"artifact_check_failed":0,"evidence_conflict":0,"pre_installed":0,"requires_reboot":0}}
```

### 2.3 其他组同样是这套短名

```text
07 组: {"already_installed":0,"failed":2,"installed":0,"partial":1,"skipped":1,"timeout":0,"triggered":11,"unverified":0}
09 组: {"already_installed":0,"failed":6,"installed":1,"partial":3,"skipped":3,"timeout":0,"triggered":1,"unverified":0}
```

## 三、期望行为

1. `by_status` 直接用 `final_status` 的枚举名（`install_completed` 等），或用一份**显式映射表**在文档/Schema 里说明（如 `installed` ≡ `install_completed`）；
2. 两种命名择一，避免"按 `final_status` 聚合 `by_status`"的脚本拿到 0；
3. 建议顺带保证 `sum(by_status.*) == summary.total` 恒定（目前各样本成立，但需要在 schema 里写死为契约并加断言）。

## 四、影响面

`_run_tests.ps1` 目前只把 `by_status` 打印出来，没有硬断言；一旦有人按 `supported_final_status` 写断言（这是最自然的做法），立刻对不上。
