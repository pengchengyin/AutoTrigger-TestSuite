; ATS_ROOT: 本仓库根目录。构建时用 makensis /DATS_ROOT=<绝对路径> 覆盖。
!ifndef ATS_ROOT
  !define ATS_ROOT "C:\ATS"
!endif


Unicode true
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

Name "AT Synthetic NSIS 07 Slow"
OutFile "${ATS_ROOT}\samples\18-合成安装器(NSIS)\NSIS-07-长安装-持续写盘.exe"
InstallDir "$PROGRAMFILES64\ATSynthNsis07"
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

FunctionEnd

Section "Install"
  SetOutPath "$INSTDIR"
  File "${ATS_ROOT}\sources\payload\app.exe"
  File "${ATS_ROOT}\sources\payload\core.dll"
  File "${ATS_ROOT}\sources\payload\resources.dat"
  File "${ATS_ROOT}\sources\payload\readme.txt"
  
  ; 写卸载项（真实安装器行为）
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis07" "DisplayName" "AT Synthetic NSIS 07 Slow"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis07" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis07" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis07" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  ; 哨兵
  CreateDirectory "C:\Users\Public\AT-SENTINEL"
  FileOpen $0 "C:\Users\Public\AT-SENTINEL\ran.log" a
  FileSeek $0 0 END
  FileWrite $0 "NSIS-NSIS-07-长安装-持续写盘$\r$\n"
  FileClose $0
    StrCpy $1 0
  loop_slow:
    IntOp $1 $1 + 1
    FileOpen $2 "$INSTDIR\progress.txt" w
    FileWrite $2 "progress $1"
    FileClose $2
    DetailPrint "progress $1 / 30"
    Sleep 3000
    IntCmp $1 30 done_slow loop_slow loop_slow
  done_slow:

SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\app.exe"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthNsis07"
SectionEnd
