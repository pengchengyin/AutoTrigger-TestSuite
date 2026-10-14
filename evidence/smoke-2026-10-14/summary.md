# 冒烟验证 20261014-105328

- 工具: <DESKTOP>\AutoTrigger.exe
- 版本: {"go_version":"go1.20.1","resource_pack_version":"0.1.0","schema_version":"2.8","tool_version":"0.1.0"}
- 权限: 未提权
- Profile: quick   超时: 60 s

| 样本 | 预期 | 实际 | 置信度 | 退出码 | 耗时秒 | VIOLATION |
|---|---|---|---|---|---|---|
| samples\14-跳过与兜底\01-空文件.exe | skipped | skipped |  | 0 | 4.8 | 0 |
| samples\14-跳过与兜底\02-空文件.dat | skipped | skipped |  | 0 | 7.5 | 0 |
| samples\14-跳过与兜底\03-单字节文件.bin | failed | failed |  | 0 | 3.8 | 0 |

## 与预期不符：无（全部符合）

> install_unverified / triggered 不等于安装成功；成功率口径见 reports/README.md。
