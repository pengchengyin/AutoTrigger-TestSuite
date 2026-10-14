@echo off
if not exist "C:\Users\Public\AT-SENTINEL" mkdir "C:\Users\Public\AT-SENTINEL"
echo ARCH-CHOSEN-%%PROCESSOR_ARCHITECTURE%% >> "C:\Users\Public\AT-SENTINEL\ran.log"
if not exist "%ProgramFiles%\ATArchA2503" mkdir "%ProgramFiles%\ATArchA2503"
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATArchA2503" /v DisplayName /t REG_SZ /d "AT Arch A25-03" /f >nul
exit /b 0
