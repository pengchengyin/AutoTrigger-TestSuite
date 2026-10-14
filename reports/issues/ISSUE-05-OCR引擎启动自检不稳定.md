# ISSUE-05｜OCR 引擎自检时好时坏（startup_failed ↔ ok），且冷启动耗时远超配置超时（高）

- **严重级别**：高（OCR 是自绘安装器唯一可靠的兜底，抖动会随机吃掉安装成功率）
- **状态**：待修复
- **关联验收项**：A18 / A21 / F14.6

## 一、问题现象

同一台机器、同一份部署（`third_party\ocr\packages\PaddleOCR-json_v1.4.1...`）在两次运行中给出**相反**的 OCR 状态：

| 运行 | `ocr_engine_status` | `ocr_startup_ms` | 说明 |
|---|---|---|---|
| `--check-prereq --json --no-deploy-deps`（10:07） | `startup_failed` | `0` | 自检失败 |
| `--input 18-...\NSIS-01...`（10:12） | `ok` | `1672` | 正常 |

而且自检失败时**同时**给出两条互相冲突的信息：先说 "`ok: true`"，又在 issues 里说 OCR 不可用。

## 二、复现步骤

```powershell
.\AutoTrigger.exe --check-prereq --json --no-deploy-deps   # 观察 ocr 字段
.\AutoTrigger.exe --capabilities                            # 观察 ocr / prereq
.\AutoTrigger.exe --input ".\安装包测试\samples\18-合成安装器(NSIS)\NSIS-01-静默安装成功.exe" `
  --output ".\AutoTrigger测试报告\evidence\18-NSIS-01.json"
```

## 三、证据

### 3.1 自检失败的运行（10:07:18–10:07:32）

```text
[警告] 【任务】环境提示：OCR 能力自检失败：OCR recognition: context deadline exceeded
[警告] 【任务】环境提示：未检测到可用 OCR 引擎：请部署 third_party\ocr\PaddleOCR-json 或
       RapidOCR-json；当前退回 UIA/Win32 + 模板；可用 --no-ocr 显式跳过
```

```json
"prereq":{"ocr_engine":"paddleocr_json",
          "ocr_engine_path":"C:\\Users\\<USER>\\Desktop\\third_party\\ocr\\packages\\PaddleOCR-json_v1.4.1_windows_x64-d6167eb3\\PaddleOCR-json_v1.4.1\\PaddleOCR-json.exe",
          "ocr_engine_status":"startup_failed","ocr_engine_version":null,
          "ocr_engine_languages":[],"ocr_startup_ms":0,
          "ok":true,
          "issues":["...","OCR 能力自检失败：OCR recognition: context deadline exceeded",
                    "未检测到可用 OCR 引擎：..."]}
```

注意：`ok:true` 与 `ocr_engine_status:"startup_failed"` 并存。

### 3.2 随后成功的运行（`evidence\18-NSIS-01.json`）

```json
"prereq":{"ocr_engine_status":"ok","ocr_engine_version":"unknown",
          "ocr_engine_languages":["ch","en"],"ocr_startup_ms":1672,"ok":true}
```

### 3.3 原生冷启动实测（绕开工具，直接跑引擎）

单图一次性模式（`PaddleOCR-json.exe -image_path=... -config_path=...`）：

```text
ELAPSED_MS=18937        # 引擎 EXE 存在、模型齐全、识别结果正确
{"code":100,"data":[{"box":[[6,7],[116,8],[116,23],[6,22]],
  "score":0.9050501585006714,"text":"NSIS 2.0 Setup"}, ... ]}
```

匿名管道（stdio）模式逐行计时：

```text
FIRST_RESPONSE_MS=1398   # 第一行是 banner，不是识别结果
FIRST_LINE=PaddleOCR-json v1.4.1
SECOND_LINE=OCR anonymous pipe mode.
SECOND_RESPONSE_MS=2188  # 预热后的识别耗时
```

### 3.4 生效配置中的超时

```json
"ocr":{"enabled":true,"engine":"paddleocr_json","transport":"stdio",
       "startup_timeout_ms":10000,"recognize_timeout_ms":3000,
       "restart_on_failure":true,"max_restarts":2,"min_score":0.6}
```

**冷启动 18.9 s > startup_timeout_ms=10 s**；一旦首次识别落在模型尚未加载完成的窗口内，就会命中 `recognize_timeout_ms=3 s` → `context deadline exceeded`。

## 四、期望行为

1. **启动自检不要以"识别一次"作为就绪判据**。stdio 模式下应先读到引擎的就绪 banner（`OCR anonymous pipe mode.`），再做一次**预热识别**（或把预热结果丢弃），预热阶段不计入 `recognize_timeout_ms`。
2. **区分"启动等待"与"识别超时"**：`startup_timeout_ms` 应覆盖"进程启动 + 模型加载"（建议 30–60 s，或做成可配置），`recognize_timeout_ms` 只覆盖稳态识别。
3. **`ok` 字段语义要对**：既然 issues 里列了 OCR 不可用，`prereq.ok` 不应还是 `true`；或者拆成 `ok` 与 `ocr_ok` 两个字段。
4. **失败要可诊断**：把引擎 stderr、启动耗时、退出码写进 `prereq`，而不是只给一句 `context deadline exceeded`。

## 五、影响面

`samples\16-自绘界面-OCR专项` 是纯 OCR/模板场景；OCR 抖动 + 模板为空（ISSUE-04）叠加后，该组基本不可能通过。真实软件里所有自绘/非标准控件安装器同理。
