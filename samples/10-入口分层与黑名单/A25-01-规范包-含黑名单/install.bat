@echo off
echo [install.bat] 正在安装 A25-01 测试包...
if not exist "C:\Users\Public\AT-SENTINEL" mkdir "C:\Users\Public\AT-SENTINEL"
echo ENTRY-install.bat >> "C:\Users\Public\AT-SENTINEL\ran.log"
if not exist "%ProgramFiles%\ATPackageA2501" mkdir "%ProgramFiles%\ATPackageA2501"
echo installed > "%ProgramFiles%\ATPackageA2501\installed.txt"
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATPackageA2501" /v DisplayName /t REG_SZ /d "AT Package A25-01" /f >nul
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATPackageA2501" /v DisplayVersion /t REG_SZ /d "1.0.0" /f >nul
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATPackageA2501" /v InstallLocation /t REG_SZ /d "%ProgramFiles%\ATPackageA2501" /f >nul
echo [install.bat] 安装完成
exit /b 0
