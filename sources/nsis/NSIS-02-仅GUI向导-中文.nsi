; ATS_ROOT: 本仓库根目录。构建时用 makensis /DATS_ROOT=<绝对路径> 覆盖。
!ifndef ATS_ROOT
  !define ATS_ROOT "C:\ATS"
!endif


Unicode true
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

Name "AT 合成 NSIS 向导 02（中文）"
OutFile "${ATS_ROOT}\samples\18-合成安装器(NSIS)\NSIS-02-仅GUI向导-中文.exe"
InstallDir "$PROGRAMFILES64\ATSynthNsis02"
RequestExecutionLevel admin
ShowInstDetails show

!define MUI_ABORTWARNING
!define MUI_LANGDLL_ALLLANGUAGES
!define MUI_LANGDLL_DISPLAY
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "${ATS_ROOT}\sources\payload\license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

Function .onInit
  ; 忽略 /S：强制走 GUI 向导（F14/A12 用）
  SetSilent normal
FunctionEnd

Section "Install"
  SetOutPath "$INSTDIR"
  File "${ATS_ROOT}\sources\payload\app.exe"
  File "${ATS_ROOT}\sources\payload\core.dll"
  File "${ATS_ROOT}\sources\payload\resources.dat"
  File "${ATS_ROOT}\sources\payload\readme.txt"
  
  ; 写卸载项（真实安装器行为）
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis02" "DisplayName" "AT 合成 NSIS 向导 02（中文）"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis02" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis02" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis02" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  ; 哨兵
  CreateDirectory "C:\Users\Public\AT-SENTINEL"
  FileOpen $0 "C:\Users\Public\AT-SENTINEL\ran.log" a
  FileSeek $0 0 END
  FileWrite $0 "NSIS-NSIS-02-仅GUI向导-中文$\r$\n"
  FileClose $0
  
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\app.exe"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis02"
SectionEnd
