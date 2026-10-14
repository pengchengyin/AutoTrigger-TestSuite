# 合并汇总

- 结果目录: C:\Users\<USER>\Desktop\AutoTrigger-TestSuite\runs\20261014-165241 ; C:\Users\<USER>\Desktop\AutoTrigger-TestSuite\runs\20261014-154759 ; C:\Users\<USER>\Desktop\AutoTrigger-TestSuite\runs\20261014-153006 ; C:\Users\<USER>\Desktop\AutoTrigger-TestSuite\runs\20261014-151140 ; C:\Users\<USER>\Desktop\AutoTrigger-TestSuite\runs\20261014-141508 ; C:\Users\<USER>\Desktop\AutoTrigger-TestSuite\runs\_thirdparty-spotcheck ; C:\Users\<USER>\Desktop\AutoTrigger-TestSuite\runs\20261014-135034 ; C:\Users\<USER>\Desktop\AutoTrigger-TestSuite\runs\20261014-134917
- 枚举样本: 149（已覆盖 124 / 未执行 25）

## 分组状态分布

| 分组 | 样本数 | 已覆盖 | 状态分布 |
|---|---|---|---|
| 01-Inno Setup | 5 | 4 | install_completed=2 install_partial=1 (无结果项)=1 (未执行)=1 |
| 02-NSIS | 5 | 0 | (未执行)=5 |
| 03-MSI | 6 | 0 | (未执行)=6 |
| 04-Burn bootstrapper | 3 | 0 | (未执行)=3 |
| 05-其它厂商安装器 | 3 | 0 | (未执行)=3 |
| 06-压缩包 | 7 | 0 | (未执行)=7 |
| 07-脚本与快捷方式 | 15 | 15 | triggered=8 killed_on_timeout=3 install_completed=1 failed=2 install_unverified=1 |
| 08-文档类 | 8 | 8 | triggered=1 skipped=6 failed=1 |
| 09-类型识别与伪装 | 13 | 13 | skipped=2 failed=6 install_completed=3 容器展开=1 install_unverified=1 |
| 10-入口分层与黑名单 | 6 | 6 | 容器展开=6 |
| 11-安装成功判定 | 13 | 13 | install_unverified=6 install_completed=4 install_partial=2 failed=1 |
| 12-超时与活动感知 | 9 | 9 | install_completed=2 killed_on_timeout=6 install_partial=1 |
| 13-光盘映像 ISO | 10 | 10 | 容器展开=7 skipped=2 failed=1 |
| 14-跳过与兜底 | 12 | 12 | skipped=2 failed=7 install_completed=1 install_unverified=2 |
| 15-批量与嵌套 | 2 | 2 | 容器展开=2 |
| 16-自绘界面-OCR专项 | 2 | 2 | killed_on_timeout=1 install_partial=1 |
| 17-合成安装器(Inno) | 11 | 11 | install_completed=10 install_partial=1 |
| 18-合成安装器(NSIS) | 7 | 7 | install_completed=5 install_partial=2 |
| 19-合成安装器(MSI-WiX) | 9 | 9 | install_completed=6 install_partial=1 failed=2 |
| 20-静默参数探测 | 3 | 3 | install_partial=1 install_completed=2 |

## 逐样本结果

| 分组 | 样本 | 类型 | 最终状态 | 置信度 | 证据 | 耗时秒 | 覆盖 |
|---|---|---|---|---|---|---|---|
| 01-Inno Setup | 01-Inno Setup\audacity-win-3.7.1-64bit.exe | 文件 | install_completed | high | S1/A1 | 67.1 | 是 |
| 01-Inno Setup | 01-Inno Setup\Git-2.47.1-64-bit.exe | 文件 | install_completed | low | A3/A1 | 209.3 | 是 |
| 01-Inno Setup | 01-Inno Setup\Notepad3-Setup.exe | 文件 | install_partial | low | N1/S1/A2 | 227.8 | 是 |
| 01-Inno Setup | 01-Inno Setup\ShareX-17.0.0-setup.exe | 文件 | (无结果项) |  |  |  | 是 |
| 01-Inno Setup | 01-Inno Setup\WinMerge-2.16.46-x64-Setup.exe | 文件 | (未执行) |  |  |  | 否 |
| 02-NSIS | 02-NSIS\Defraggler.exe | 文件 | (未执行) |  |  |  | 否 |
| 02-NSIS | 02-NSIS\Everything-1.4.1.1026.x64-Setup.exe | 文件 | (未执行) |  |  |  | 否 |
| 02-NSIS | 02-NSIS\Firefox-Setup-zh-CN.exe | 文件 | (未执行) |  |  |  | 否 |
| 02-NSIS | 02-NSIS\npp.8.8.1.Installer.x64.exe | 文件 | (未执行) |  |  |  | 否 |
| 02-NSIS | 02-NSIS\Recuva.exe | 文件 | (未执行) |  |  |  | 否 |
| 03-MSI | 03-MSI\7z2600-x64.msi | 文件 | (未执行) |  |  |  | 否 |
| 03-MSI | 03-MSI\KeePassXC-2.7.9-Win64.msi | 文件 | (未执行) |  |  |  | 否 |
| 03-MSI | 03-MSI\MobaXterm_installer_26.5.msi | 文件 | (未执行) |  |  |  | 否 |
| 03-MSI | 03-MSI\node-v22.11.0-x64.msi | 文件 | (未执行) |  |  |  | 否 |
| 03-MSI | 03-MSI\putty-64bit-0.85-installer.msi | 文件 | (未执行) |  |  |  | 否 |
| 03-MSI | 03-MSI\TortoiseGit-2.17.0.0-64bit.msi | 文件 | (未执行) |  |  |  | 否 |
| 04-Burn bootstrapper | 04-Burn bootstrapper\python-3.13.0-amd64.exe | 文件 | (未执行) |  |  |  | 否 |
| 04-Burn bootstrapper | 04-Burn bootstrapper\VC_redist.x64.exe | 文件 | (未执行) |  |  |  | 否 |
| 04-Burn bootstrapper | 04-Burn bootstrapper\windowsdesktop-runtime-8.0-win-x64.exe | 文件 | (未执行) |  |  |  | 否 |
| 05-其它厂商安装器 | 05-其它厂商安装器\TeraCopy.exe | 文件 | (未执行) |  |  |  | 否 |
| 05-其它厂商安装器 | 05-其它厂商安装器\VeraCrypt.exe | 文件 | (未执行) |  |  |  | 否 |
| 05-其它厂商安装器 | 05-其它厂商安装器\ZoomInstallerFull.exe | 文件 | (未执行) |  |  |  | 否 |
| 06-压缩包 | 06-压缩包\7z2501-extra.7z | 文件 | (未执行) |  |  |  | 否 |
| 06-压缩包 | 06-压缩包\7z2600-x64-32bit.exe | 文件 | (未执行) |  |  |  | 否 |
| 06-压缩包 | 06-压缩包\MobaXterm_Installer.zip | 文件 | (未执行) |  |  |  | 否 |
| 06-压缩包 | 06-压缩包\npp.8.8.1.portable.x64.zip | 文件 | (未执行) |  |  |  | 否 |
| 06-压缩包 | 06-压缩包\nssm-2.24.zip | 文件 | (未执行) |  |  |  | 否 |
| 06-压缩包 | 06-压缩包\putty-0.85-w64.zip | 文件 | (未执行) |  |  |  | 否 |
| 06-压缩包 | 06-压缩包\嵌套包 | 目录 | (未执行) |  |  |  | 否 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\01-批处理.bat | 文件 | triggered |  |  | 4.8 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\02-命令脚本.cmd | 文件 | triggered |  |  | 1.1 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\03-PowerShell.ps1 | 文件 | triggered |  |  | 3 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\04-VBScript.vbs | 文件 | killed_on_timeout |  |  | 31.4 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\05-JScript.js | 文件 | killed_on_timeout |  |  | 31.3 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\06-WSF脚本.wsf | 文件 | triggered |  |  | 1.1 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\07-普通JS文本.js | 文件 | killed_on_timeout |  |  | 31.3 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\08-UTF16LE批处理.bat | 文件 | triggered |  |  | 1.1 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\09-快捷方式-指向安装器.lnk | 文件 | install_completed | medium | S1/A1/B1 | 4.7 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\10-导出函数库.dll | 文件 | failed |  |  | 1.6 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\10-快捷方式-指向不存在目标.lnk | 文件 | failed |  |  | 1.1 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\11-快捷方式-指向文档.lnk | 文件 | triggered |  |  | 1.1 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\11-原生导出表(7z).dll | 文件 | install_unverified | low | A1 | 20.1 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\com-命令触发器.com | 文件 | triggered |  |  | 2.6 | 是 |
| 07-脚本与快捷方式 | 07-脚本与快捷方式\scr-屏保触发器.scr | 文件 | triggered |  |  | 2.7 | 是 |
| 08-文档类 | 08-文档类\01-有效文档.pdf | 文件 | triggered |  |  | 1.2 | 是 |
| 08-文档类 | 08-文档类\02-Word文档.docx | 文件 | skipped |  |  | 1.3 | 是 |
| 08-文档类 | 08-文档类\03-Excel表格.xlsx | 文件 | skipped |  |  | 1 | 是 |
| 08-文档类 | 08-文档类\04-文档.rtf | 文件 | skipped |  |  | 1 | 是 |
| 08-文档类 | 08-文档类\05-老格式.doc | 文件 | skipped |  |  | 0.9 | 是 |
| 08-文档类 | 08-文档类\06-幻灯片.pptx | 文件 | skipped |  |  | 0.9 | 是 |
| 08-文档类 | 08-文档类\07-含宏文档.docm | 文件 | skipped |  |  | 1 | 是 |
| 08-文档类 | 08-文档类\08-无宿主扩展名.atdoc | 文件 | failed |  |  | 0.9 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\ELF头文件.so | 文件 | skipped |  |  | 0.9 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\LNK头伪lnk.lnk | 文件 | failed |  |  | 1 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\MachO头文件.dylib | 文件 | skipped |  |  | 0.9 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\MZ头但非PE.exe | 文件 | failed |  |  | 17.3 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\OLE头伪msi.msi | 文件 | failed |  | N1 | 16.1 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\实际是PDF的exe.exe | 文件 | failed |  |  | 0.9 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\实际是PE的docx.docx | 文件 | install_completed | medium | S1/S2/A1 | 4.7 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\实际是PE的jpg.jpg | 文件 | install_completed | low | A3/A1 | 4.7 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\实际是PE的txt.txt | 文件 | install_completed | low | A3/A1 | 4.6 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\实际是ZIP的exe.exe | 文件 | 容器展开 |  |  | 1 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\实际是文本的exe.exe | 文件 | failed |  |  | 0.9 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\随机高熵数据.xyz | 文件 | failed |  |  | 0.9 | 是 |
| 09-类型识别与伪装 | 09-类型识别与伪装\伪装成exe的文本.exe | 文件 | install_unverified | low | A1 | 783 | 是 |
| 10-入口分层与黑名单 | 10-入口分层与黑名单\A25-01-规范包-含黑名单 | 目录 | 容器展开 |  | A3/A1 | 13.5 | 是 |
| 10-入口分层与黑名单 | 10-入口分层与黑名单\A25-02-readme指向不存在文件 | 目录 | 容器展开 |  | A3/A1 | 30.7 | 是 |
| 10-入口分层与黑名单 | 10-入口分层与黑名单\A25-03-架构优先 | 目录 | 容器展开 |  | A1 | 273.3 | 是 |
| 10-入口分层与黑名单 | 10-入口分层与黑名单\A25-04-规范包压缩版.7z | 文件 | 容器展开 |  | A1 | 140.7 | 是 |
| 10-入口分层与黑名单 | 10-入口分层与黑名单\A25-04-规范包压缩版.zip | 文件 | 容器展开 |  | A1 | 135.2 | 是 |
| 10-入口分层与黑名单 | 10-入口分层与黑名单\A25-06-阶段2兜底 | 目录 | 容器展开 |  |  | 75.1 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-01-假成功bootstrapper.exe | 文件 | install_unverified | low | A1 | 156.1 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-02-纯退出码0.exe | 文件 | install_unverified | low | A1 | 123.5 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-03-标准安装-落盘+卸载项.exe | 文件 | install_completed | medium | S1/S2/A1/B1 | 4.4 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-04-per-user安装-HKCU卸载项.exe | 文件 | install_completed | medium | S1/S2/A1 | 5.1 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-05-绿色便携-仅落盘.exe | 文件 | install_unverified | low | S2/A1 | 51 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-06-反证据-失败码+回滚日志.exe | 文件 | install_partial | low | S2/N1 | 52.9 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-07-反证据-装后回滚.exe | 文件 | install_partial | low | N6/S1/A1 | 68.4 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-08-退出码1603失败.exe | 文件 | failed |  | N1 | 455.2 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-09-覆盖升级-字段变化.exe | 文件 | install_completed | medium | S1/S2/A1 | 5.1 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-10-已安装检测-幂等.exe | 文件 | install_completed | medium | S1/S2/A1 | 4.7 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-11b-宽松口径-A1加落盘副作用.exe | 文件 | install_unverified | low | S2/A1 | 48.5 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-11-口径对照-仅非卸载项注册表副作用.exe | 文件 | install_unverified | low | A1 | 48.4 | 是 |
| 11-安装成功判定 | 11-安装成功判定\A29-12-落盘到监控外目录.exe | 文件 | install_unverified | low | A1 | 49.3 | 是 |
| 12-超时与活动感知 | 12-超时与活动感知\A30-01-慢安装器-持续写盘90s.exe | 文件 | install_completed | medium | S1/A1 | 137 | 是 |
| 12-超时与活动感知 | 12-超时与活动感知\A30-02-启动后无动作.exe | 文件 | killed_on_timeout |  |  | 157.6 | 是 |
| 12-超时与活动感知 | 12-超时与活动感知\A30-03-运行中静止.exe | 文件 | killed_on_timeout |  |  | 129 | 是 |
| 12-超时与活动感知 | 12-超时与活动感知\A30-04-完成安装后卡在完成页.exe | 文件 | install_completed | medium | S1/S2 | 121.4 | 是 |
| 12-超时与活动感知 | 12-超时与活动感知\A30-05-联网下载组件等待.exe | 文件 | killed_on_timeout |  |  | 152.6 | 是 |
| 12-超时与活动感知 | 12-超时与活动感知\A30-06-子进程脱离-进程树清理.exe | 文件 | killed_on_timeout |  |  | 161.6 | 是 |
| 12-超时与活动感知 | 12-超时与活动感知\A30-07-超长安装-持续700s.exe | 文件 | killed_on_timeout |  |  | 127.8 | 是 |
| 12-超时与活动感知 | 12-超时与活动感知\A30-08-GUI窗口-正在下载组件.exe | 文件 | install_partial | low | A3 | 124.7 | 是 |
| 12-超时与活动感知 | 12-超时与活动感知\A30-09-超长安装-只在TEMP写盘700s.exe | 文件 | killed_on_timeout |  |  | 124.6 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A26-01-installer_media.iso | 文件 | 容器展开 |  |  | 138.1 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A26-02-malware_lure.iso | 文件 | 容器展开 |  | A1 | 81.5 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A26-03-os_install_media.iso | 文件 | skipped |  |  | 1.5 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A26-04-media_disc.iso | 文件 | skipped |  |  | 1.3 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A26-05-data_disc.iso | 文件 | 容器展开 |  | A3/A1 | 4.8 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A26-06-garbled-names.iso | 文件 | 容器展开 |  |  | 4.8 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A26-07-autorun-missing.iso | 文件 | 容器展开 |  | A3/A1 | 4.9 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A26-08-deep-longpath.iso | 文件 | 容器展开 |  |  | 5 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A27-09-UDF-only.iso | 文件 | 容器展开 |  |  | 5.2 | 是 |
| 13-光盘映像 ISO | 13-光盘映像 ISO\A27-10-截断损坏.iso | 文件 | failed |  |  | 1.3 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\01-空文件.exe | 文件 | skipped |  |  | 7.8 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\02-空文件.dat | 文件 | skipped |  |  | 4.1 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\03-单字节文件.bin | 文件 | failed |  |  | 4.6 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\04-损坏的zip.zip | 文件 | failed |  |  | 3.3 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\05-损坏的7z.7z | 文件 | failed |  |  | 2.9 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\06-截断的zip.zip | 文件 | failed |  |  | 2.4 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\07-加密zip.zip | 文件 | failed |  |  | 3 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\08-加密7z-文件名加密.7z | 文件 | failed |  |  | 4.1 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\09-未知扩展名但MZ头.qwerty | 文件 | install_completed | medium | S1/A1 | 34.8 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\10-zip炸弹-解压超2G.zip | 文件 | failed |  |  | 2.4 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\未知扩展名-MZ头.bin | 文件 | install_unverified | low | A1 | 140.8 | 是 |
| 14-跳过与兜底 | 14-跳过与兜底\无扩展名文件 | 文件 | install_unverified | low | A1 | 87.8 | 是 |
| 15-批量与嵌套 | 15-批量与嵌套\01-三层嵌套.7z | 文件 | 容器展开 |  | A3/A1 | 5.7 | 是 |
| 15-批量与嵌套 | 15-批量与嵌套\A6-批量50文件 | 目录 | 容器展开 |  | A3/A1 | 724 | 是 |
| 16-自绘界面-OCR专项 | 16-自绘界面-OCR专项\OWNERDRAW-自绘向导-浅色.exe | 文件 | killed_on_timeout |  |  | 125.7 | 是 |
| 16-自绘界面-OCR专项 | 16-自绘界面-OCR专项\OWNERDRAW-自绘向导-深色.exe | 文件 | install_partial | low | A3 | 133.3 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-01-静默安装成功.exe | 文件 | install_completed | medium | A1/A2 | 110.6 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-02-仅GUI向导-中文.exe | 文件 | install_completed | medium | A1/S1/A2 | 69.8 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-03-仅GUI向导-英文.exe | 文件 | install_completed | medium | S2/A1/S1/A2 | 60.8 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-04-per-user安装-lowest.exe | 文件 | install_completed | high | S1/S2/A1 | 19.8 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-05-长安装-持续写盘90s.exe | 文件 | install_completed | high | S1/A1 | 141 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-06-假成功-只解压无卸载项.exe | 文件 | install_completed | medium | A1/A2 | 58.1 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-07-安装后失败框-退出码1.exe | 文件 | install_partial | low | S1/N1/N2/A2 | 164.1 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-08-需重启-返回3010.exe | 文件 | install_completed | high | S1/S2 | 23.5 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-09-卡在完成页-超时验证.exe | 文件 | install_completed | high | S1/S2 | 154 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-10-联网下载组件等待.exe | 文件 | install_completed | high | S1/S2 | 126.7 | 是 |
| 17-合成安装器(Inno) | 17-合成安装器(Inno)\INNO-11-仅GUI向导-无许可页.exe | 文件 | install_completed | medium | S2/A1/S1/A2 | 47.8 | 是 |
| 18-合成安装器(NSIS) | 18-合成安装器(NSIS)\NSIS-01-静默安装成功.exe | 文件 | install_completed | high | S1/A1 | 9.7 | 是 |
| 18-合成安装器(NSIS) | 18-合成安装器(NSIS)\NSIS-02-仅GUI向导-中文.exe | 文件 | install_completed | high | S1/A1/A2 | 18.9 | 是 |
| 18-合成安装器(NSIS) | 18-合成安装器(NSIS)\NSIS-03-仅GUI向导-英文.exe | 文件 | install_completed | high | S1/S2/A1/A2 | 21.3 | 是 |
| 18-合成安装器(NSIS) | 18-合成安装器(NSIS)\NSIS-04-静默无效果-需GUI兜底.exe | 文件 | install_completed | high | A1/S1/S2/A2 | 37.4 | 是 |
| 18-合成安装器(NSIS) | 18-合成安装器(NSIS)\NSIS-05-安装后回滚.exe | 文件 | install_partial | low | N4/S2/N1/A2 | 126.1 | 是 |
| 18-合成安装器(NSIS) | 18-合成安装器(NSIS)\NSIS-06-需重启-3010.exe | 文件 | install_partial | low | S1/S2/N1/A2 | 134.8 | 是 |
| 18-合成安装器(NSIS) | 18-合成安装器(NSIS)\NSIS-07-长安装-持续写盘.exe | 文件 | install_completed | high | S1/A1 | 128.2 | 是 |
| 19-合成安装器(MSI-WiX) | 19-合成安装器(MSI-WiX)\MSI-01-标准安装成功.msi | 文件 | install_completed | medium | S1/S3/S4/B1 | 43.7 | 是 |
| 19-合成安装器(MSI-WiX) | 19-合成安装器(MSI-WiX)\MSI-02-安装致命错误1603.msi | 文件 | install_partial | low | N1/A2 | 123.5 | 是 |
| 19-合成安装器(MSI-WiX) | 19-合成安装器(MSI-WiX)\MSI-03-需重启3010.msi | 文件 | install_completed | medium | S1/S3/S4/B1 | 37.3 | 是 |
| 19-合成安装器(MSI-WiX) | 19-合成安装器(MSI-WiX)\MSI-04-per-user安装.msi | 文件 | install_completed | medium | S1/S3/S4/B1 | 36.1 | 是 |
| 19-合成安装器(MSI-WiX) | 19-合成安装器(MSI-WiX)\MSI-05-多文件较长安装.msi | 文件 | install_completed | medium | S1/S3/S4/B1 | 40.1 | 是 |
| 19-合成安装器(MSI-WiX) | 19-合成安装器(MSI-WiX)\MSI-06-升级覆盖V1.msi | 文件 | install_completed | medium | S1/S3/S4/B1 | 38.5 | 是 |
| 19-合成安装器(MSI-WiX) | 19-合成安装器(MSI-WiX)\MSI-06-升级覆盖V2.msi | 文件 | install_completed | medium | S1/S3/S4/B1 | 40.8 | 是 |
| 19-合成安装器(MSI-WiX) | 19-合成安装器(MSI-WiX)\MSI-07-无效MSI-纯文本内容.msi | 文件 | failed |  | N1 | 109 | 是 |
| 19-合成安装器(MSI-WiX) | 19-合成安装器(MSI-WiX)\MSI-08-损坏的MSI.msi | 文件 | failed |  | N1 | 103.7 | 是 |
| 20-静默参数探测 | 20-静默参数探测\F13-参数探测桩-记录全部尝试.exe | 文件 | install_partial | low | A3/N1 | 52.3 | 是 |
| 20-静默参数探测 | 20-静默参数探测\F13-参数探测桩-见VERYSILENT即成功.exe | 文件 | install_completed | medium | S1/S2/A1 | 4.3 | 是 |
| 20-静默参数探测 | 20-静默参数探测\F13-参数探测桩-只认NSIS的S.exe | 文件 | install_completed | medium | N1/S1/S2/A1 | 10.2 | 是 |
