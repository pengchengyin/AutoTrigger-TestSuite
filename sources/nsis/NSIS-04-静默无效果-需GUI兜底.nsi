; ATS_ROOT: 本仓库根目录。构建时用 makensis /DATS_ROOT=<绝对路径> 覆盖。
!ifndef ATS_ROOT
  !define ATS_ROOT "C:\ATS"
!endif


Unicode true
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

Name "AT Synthetic NSIS 04 SilentNoop"
OutFile "${ATS_ROOT}\samples\18-合成安装器(NSIS)\NSIS-04-静默无效果-需GUI兜底.exe"
InstallDir "$PROGRAMFILES64\ATSynthNsis04"
RequestExecutionLevel admin
ShowInstDetails show

!define MUI_ABORTWARNING
!define MUI_LANGDLL_ALLLANGUAGES

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

Function .onInit
  ${If} ${Silent}
    ; 静默模式下什么都不做，直接退出 0（模拟假成功）
    SetErrorLevel 0
    Quit
  ${EndIf}
FunctionEnd

Section "Install"
  SetOutPath "$INSTDIR"
  File "${ATS_ROOT}\sources\payload\app.exe"
  File "${ATS_ROOT}\sources\payload\core.dll"
  File "${ATS_ROOT}\sources\payload\resources.dat"
  File "${ATS_ROOT}\sources\payload\readme.txt"
  
  ; 写卸载项（真实安装器行为）
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis04" "DisplayName" "AT Synthetic NSIS 04 SilentNoop"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis04" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis04" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis04" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  ; 哨兵
  CreateDirectory "C:\Users\Public\AT-SENTINEL"
  FileOpen $0 "C:\Users\Public\AT-SENTINEL\ran.log" a
  FileSeek $0 0 END
  FileWrite $0 "NSIS-NSIS-04-静默无效果-需GUI兜底$\r$\n"
  FileClose $0
  
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\app.exe"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis04"
SectionEnd
