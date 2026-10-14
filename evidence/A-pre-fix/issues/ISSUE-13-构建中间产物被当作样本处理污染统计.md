# ISSUE-13｜WiX 构建中间产物 `.wixpdb` 被当作样本处理，污染 `failed` 统计（低）

- **严重级别**：低（不影响安装，但让回归统计与"失败率"失真）
- **状态**：待确认（样本侧 or 工具侧）
- **关联验收项**：A6 / A31 ⑦

## 一、问题现象

`samples\19-合成安装器(MSI-WiX)` 目录里除了 8 个 `.msi`，还混着 8 个同名 `.wixpdb`（WiX 的调试符号文件，**不是样本**）。工具把它们当普通输入逐个处理并全部记 `failed`：

```text
MSI-01-标准安装成功.wixpdb  -> failed (untriggerable)
MSI-02-安装致命错误1603.wixpdb -> failed (untriggerable)
MSI-03-需重启3010.wixpdb    -> failed (untriggerable)
MSI-04-per-user安装.wixpdb   -> failed (untriggerable)
MSI-05-多文件较长安装.wixpdb  -> failed (untriggerable)
MSI-06-升级覆盖V1.wixpdb     -> skipped (excluded_blacklist)
MSI-06-升级覆盖V2.wixpdb     -> skipped (excluded_blacklist)
```

组结果因此变成：

```json
"total":16,
"by_status":{"failed":7,...},
"layout_analysis":{"entries":12,"excluded":4,...}
```

其中 **7 个 failed = 2 个真实失败（MSI-07/08）+ 5 个 `.wixpdb`**；`total=16` 而真实样本只有 12 个（8 msi + 4 因黑名单被排除的 msi）。

## 二、证据

`elevated\19-group.log`：

```text
[信息] 【入口】选用入口：...\MSI-03-需重启3010.wixpdb（优先级 P5，判定依据 non_executable_entry）
[信息] 【识别】识别结果：...\MSI-03-需重启3010.wixpdb → unknown（339.2 KB）
[信息] 【结果】...\MSI-03-需重启3010.wixpdb → 失败（untriggerable）
```

## 三、期望行为

二选一（建议都做）：

1. **样本侧**：`19` 组不要放 `.wixpdb`（它们是 `_build` 的产物，应留在 `_build\wix`）；这样 `total` 才能对上真实样本数。
2. **工具侧**：把已知**构建中间产物**扩展名列入跳过表（`skipped: build_artifact`），例如
   `.wixpdb`、`.wixobj`、`.pdb`、`.ilk`、`.exp`、`.lib`、`.obj`、`.res`、`.nsi`（源脚本）、`.wxs`、`.wxi`。
   这样批量目录里混入工程文件时不会把失败率抬高。

## 四、备注

本条与 ISSUE-03 有交集：`.wixpdb` 被跳过其实还是因为文件名带 `升级` 命中了黑名单——**同一个文件名前缀，`.msi` 与 `.wixpdb` 都遭殃**。
