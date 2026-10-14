# AGENTS.md

本文件为在本仓库中工作的 AI Agent 提供约定与操作规范。

## 项目简介

AutoTrigger-TestSuite 是面向 [AutoTrigger](https://github.com/pengchengyin/AutoTrigger)（Windows 任意文件自动安装/触发工具）的**可复现测试套件**，包含自制样本、样本源码、脚本、样本清单、逐样本结果、测试报告与已知问题。

## 目录结构

| 目录 | 说明 |
|---|---|
| `samples/` | 自制样本（组 07–20，14 组 / 240 文件） |
| `sources/` | 自制样本源码（C#/Inno/NSIS/WiX/ISO）与 `BUILD.md` |
| `scripts/` | 冒烟验证 / 清单校验 / 第三方获取 / 结果对比 / 清理 |
| `manifests/` | 自制与第三方样本清单、工具链、SHA-256 索引 |
| `reports/` | 汇总报告、逐样本 CSV、问题文档、历史报告 |
| `evidence/` | 脱敏后的 JSON / 日志与脱敏映射表 |
| `docs/` | 测试方法、环境要求、结果判读、FAQ |

## 约定

- 结论只按实际跑出来的结果写，缺失信息一律标注「未提供」，**不猜测、不补造**。
- 第三方安装包不随仓库分发；大体积/生成物由 `.gitignore` 排除。
- 证据副本保持脱敏（用户名、机器名、邮箱、SID、绝对路径）。

## 提交规范（重要）

- **每次改完都自动提交**，无需再次询问确认。
- 提交必须使用已有 skill：**git-commit**。
- 提交信息（message）**使用中文**，遵循 Conventional Commits 格式。
- 除非明确要求，否则**不推送**（push）。
