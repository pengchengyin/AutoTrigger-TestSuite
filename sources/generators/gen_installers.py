# -*- coding: utf-8 -*-
"""
生成「真实格式」的合成安装器：
  - Inno Setup  -> samples/17-合成安装器(Inno)
  - NSIS        -> samples/18-合成安装器(NSIS)
这些样本带真实安装器家族特征，用于验证 F13 静默参数表 / F17 P2 识别 / F14 GUI 向导 / F15 判定。
用法: python sources/gen_installers.py
"""
import os, shutil, subprocess, sys, textwrap

ROOT = os.environ.get("ATS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "samples")
BUILD = os.path.join(ROOT, "sources")
PAYLOAD = os.path.join(BUILD, "payload")
ISCC = os.path.join(ROOT, "_toolchain", "innosetup", "ISCC.exe")
MAKENSIS = os.path.join(ROOT, "_toolchain", "nsis", "makensis.exe")
HAS_ZH = os.path.exists(os.path.join(ROOT, "_toolchain", "innosetup", "Languages", "ChineseSimplified.isl"))

# 样本运行时的哨兵/落盘目录
SENT = r"C:\Users\Public\AT-SENTINEL"


def ensure_payload():
    os.makedirs(PAYLOAD, exist_ok=True)
    # 普通载荷
    for n, size in [("app.exe", 64 * 1024), ("readme.txt", 512), ("core.dll", 96 * 1024),
                    ("resources.dat", 256 * 1024)]:
        p = os.path.join(PAYLOAD, n)
        if not os.path.exists(p):
            with open(p, "wb") as f:
                f.write(b"MZ" + os.urandom(size) if n.endswith((".exe", ".dll")) else b"AT payload\n" + b"x" * size)
    # 长安装用的大块载荷（可压缩，体积小但写入量大）
    big = os.path.join(PAYLOAD, "bigpayload.bin")
    if not os.path.exists(big):
        with open(big, "wb") as f:
            f.write(b"\0" * (256 * 1024 * 1024))       # 256MB 零，压缩后很小
    # 从 C# 合成样本里借几个"行为助手"
    helpers = {
        "hanger.exe": ("12-超时与活动感知", "A30-04-完成安装后卡在完成页.exe"),
        "netwait.exe": ("12-超时与活动感知", "A30-05-联网下载组件等待.exe"),
        "slowwriter.exe": ("12-超时与活动感知", "A30-01-慢安装器-持续写盘90s.exe"),
        "rollback.exe": ("11-安装成功判定", "A29-07-反证据-装后回滚.exe"),
    }
    for dst, (sub, src) in helpers.items():
        sp = os.path.join(S, sub, src)
        dp = os.path.join(PAYLOAD, dst)
        if os.path.exists(sp) and not os.path.exists(dp):
            shutil.copy2(sp, dp)
    print("[OK] 载荷就绪: %d 个文件" % len(os.listdir(PAYLOAD)))


# ==================================================================== Inno Setup
INNO_BASE = r"""
[Setup]
AppId={{{{9A7E1C{n:02d}-4B2E-4E7A-9C1D-AT{n:02d}00000000}}}}
AppName={appname}
AppVersion={appver}
AppVerName={appname} {appver}
AppPublisher=AT-TestSuite
DefaultDirName={appdir}
DefaultGroupName={appname}
UninstallDisplayName={appname}
UninstallDisplayIcon={{app}}\app.exe
OutputDir={outdir}
OutputBaseFilename={outbase}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
SetupLogging=yes
PrivilegesRequired={priv}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
{extra_setup}
[Languages]
{langs}
[Files]
Source: "{payload}\app.exe"; DestDir: "{{app}}"; Flags: ignoreversion{files_check}
Source: "{payload}\core.dll"; DestDir: "{{app}}"; Flags: ignoreversion{files_check}
Source: "{payload}\resources.dat"; DestDir: "{{app}}"; Flags: ignoreversion{files_check}
Source: "{payload}\readme.txt"; DestDir: "{{app}}"; Flags: ignoreversion{files_check}
{files_extra}
[Icons]
Name: "{{group}}\{appname}"; Filename: "{{app}}\app.exe"
{run_section}
{code_section}
"""

CODE_SLOW = r"""
[Code]
function GetTickCount: DWORD; external 'GetTickCount@kernel32.dll stdcall';
procedure CurStepChanged(CurStep: TSetupStep);
var
  i: Integer;
  t: DWORD;
begin
  if CurStep = ssPostInstall then
  begin
    for i := 1 to 30 do
    begin
      SaveStringToFile(ExpandConstant('{app}\progress.txt'),
        'progress step ' + IntToStr(i) + #13#10, True);
      t := GetTickCount;
      while (GetTickCount - t) < 3000 do ;
    end;
  end;
end;
"""

CODE_FAIL = r"""
[Code]
function GetCustomSetupExitCode: Integer;
begin
  Result := 1;
end;
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    SaveStringToFile(ExpandConstant('{app}\fail.txt'), 'simulated failure', False);
  end;
end;
procedure DeinitializeSetup();
begin
  MsgBox('安装失败：模拟致命错误，正在回滚。' + #13#10 + 'Installation failed, rolling back changes.',
         mbError, MB_OK);
end;
"""

CODE_REBOOT = r"""
[Code]
function GetCustomSetupExitCode: Integer;
begin
  Result := 3010;   // ERROR_SUCCESS_REBOOT_REQUIRED
end;
procedure DeinitializeSetup();
begin
  MsgBox('安装完成，需要重启才能生效。' + #13#10 + 'A reboot is required to complete the installation.',
         mbInformation, MB_OK);
end;
"""

CODE_SENTINEL = r"""
[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if not DirExists('{sent}') then CreateDir('{sent}');
    SaveStringToFile('{sent}\ran.log', 'INNO-{tag}' + #13#10, True);
  end;
end;
"""

# 「仅 GUI 向导」样本：Inno 本身无法禁用 /SILENT，故用 WizardSilent 让静默运行成为空操作，
# 强制工具回退到「无参数运行 + GUI 自动化」（正好验证 F13 回退链与 F14）。
CODE_GUI_ONLY = r"""
[Code]
function NotSilent: Boolean;
begin
  Result := not WizardSilent;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  loc: String;
begin
  if CurStep = ssPostInstall then
  begin
    if not WizardSilent then
    begin
      loc := ExpandConstant('{{app}}');
      if not DirExists('{sent}') then CreateDir('{sent}');
      SaveStringToFile('{sent}\ran.log', 'INNO-{tag}-GUI' + #13#10, True);
      RegWriteStringValue(HKCU,
        'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthInno{tag}',
        'DisplayName', '{appname}');
      RegWriteStringValue(HKCU,
        'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthInno{tag}',
        'DisplayVersion', '1.0.0');
      RegWriteStringValue(HKCU,
        'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthInno{tag}',
        'InstallLocation', loc);
    end;
  end;
end;
"""


def gen_inno():
    outdir = os.path.join(S, "17-合成安装器(Inno)")
    os.makedirs(outdir, exist_ok=True)
    if HAS_ZH:
        langs_zh = 'Name: "chinesesimplified"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"'
    else:
        langs_zh = 'Name: "english"; MessagesFile: "compiler:Default.isl"'
    langs_en = 'Name: "english"; MessagesFile: "compiler:Default.isl"'
    license = os.path.join(PAYLOAD, "license.txt")
    if not os.path.exists(license):
        open(license, "w", encoding="utf-8").write(
            "AT 测试许可协议 / AT Test License Agreement\r\n"
            "1. 本样本仅用于自动化安装工具的测试。\r\n"
            "2. This sample is for installer-automation testing only.\r\n")

    specs = [
        dict(n=1, base="INNO-01-静默安装成功", appname="AT Synthetic Inno 01", priv="admin",
             appdir=r"{autopf}\ATSynthInno01", extra='LicenseFile=%s' % license,
             langs=langs_en, code=CODE_SENTINEL.format(sent=SENT, tag="01"), tail="", fc=""),
        dict(n=2, base="INNO-02-仅GUI向导-中文", appname="AT 合成安装向导 02（中文）", priv="admin",
             appdir=r"{autopf}\ATSynthInno02",
             extra='Uninstallable=no\r\nCreateUninstallRegKey=no\r\nLicenseFile=%s' % license,
             langs=langs_zh + "\r\n" + langs_en,
             code=CODE_GUI_ONLY.format(sent=SENT, tag="02", appname="AT Synth Inno 02 GUI ZH"), tail="", fc="; Check: NotSilent"),
        dict(n=3, base="INNO-03-仅GUI向导-英文", appname="AT Synthetic Wizard 03 (English)", priv="admin",
             appdir=r"{autopf}\ATSynthInno03",
             extra='Uninstallable=no\r\nCreateUninstallRegKey=no\r\nLicenseFile=%s' % license,
             langs=langs_en,
             code=CODE_GUI_ONLY.format(sent=SENT, tag="03", appname="AT Synth Inno 03 GUI EN"), tail="", fc="; Check: NotSilent"),
        dict(n=4, base="INNO-04-per-user安装-lowest", appname="AT Synthetic Inno 04 PerUser", priv="lowest",
             appdir=r"{localappdata}\ATSynthInno04", extra="", langs=langs_en,
             code=CODE_SENTINEL.format(sent=SENT, tag="04"), tail=""),
        dict(n=5, base="INNO-05-长安装-持续写盘90s", appname="AT Synthetic Inno 05 Slow", priv="admin",
             appdir=r"{autopf}\ATSynthInno05", extra="", langs=langs_en, code=CODE_SLOW, tail=""),
        dict(n=6, base="INNO-06-假成功-只解压无卸载项", appname="AT Synthetic Inno 06 FakeOK", priv="lowest",
             appdir=r"{tmp}\ATSynthInno06",
             extra="Uninstallable=no\r\nCreateUninstallRegKey=no\r\nDisableDirPage=yes",
             langs=langs_en, code="", tail=""),
        dict(n=7, base="INNO-07-安装后失败框-退出码1", appname="AT Synthetic Inno 07 Fail", priv="admin",
             appdir=r"{autopf}\ATSynthInno07", extra="", langs=langs_en, code=CODE_FAIL, tail=""),
        dict(n=8, base="INNO-08-需重启-返回3010", appname="AT Synthetic Inno 08 Reboot", priv="admin",
             appdir=r"{autopf}\ATSynthInno08", extra="", langs=langs_en, code=CODE_REBOOT, tail=""),
        dict(n=9, base="INNO-09-卡在完成页-超时验证", appname="AT Synthetic Inno 09 Hanger", priv="admin",
             appdir=r"{autopf}\ATSynthInno09", extra="", langs=langs_en,
             code=CODE_SENTINEL.format(sent=SENT, tag="09"),
             tail='[Run]\r\nFilename: "{payload}\\hanger.exe"; Flags: waituntilterminated; StatusMsg: "等待用户点击完成..."\r\n'.replace("{payload}", PAYLOAD)),
        dict(n=10, base="INNO-10-联网下载组件等待", appname="AT Synthetic Inno 10 NetWait", priv="admin",
             appdir=r"{autopf}\ATSynthInno10", extra="", langs=langs_en,
             code=CODE_SENTINEL.format(sent=SENT, tag="10"),
             tail='[Run]\r\nFilename: "{payload}\\netwait.exe"; Flags: waituntilterminated\r\n'.replace("{payload}", PAYLOAD)),
        dict(n=11, base="INNO-11-仅GUI向导-无许可页", appname="AT Synthetic Wizard 11", priv="admin",
             appdir=r"{autopf}\ATSynthInno11",
             extra='Uninstallable=no\r\nCreateUninstallRegKey=no', langs=langs_en,
             code=CODE_GUI_ONLY.format(sent=SENT, tag="11", appname="AT Synth Inno 11 GUI"), tail="", fc="; Check: NotSilent"),
    ]

    ok = fail = 0
    for sp in specs:
        files_extra = ""
        if sp["n"] in (5,):
            files_extra = 'Source: "%s\\bigpayload.bin"; DestDir: "{app}"; Flags: ignoreversion\r\n' % PAYLOAD
        code = sp["code"]
        if sp["n"] in (9, 10):
            code = sp["code"]
        body = INNO_BASE.format(
            n=sp["n"], appname=sp["appname"], appver="1.0.0",
            appdir=sp["appdir"], outdir=outdir, outbase=sp["base"],
            priv=sp["priv"], extra_setup=sp["extra"], langs=sp["langs"],
            payload=PAYLOAD, files_extra=files_extra, files_check=sp.get("fc", ""),
            run_section=sp["tail"], code_section=code)
        iss = os.path.join(BUILD, sp["base"] + ".iss")
        with open(iss, "w", encoding="utf-8-sig") as f:
            f.write(body)
        p = subprocess.run([ISCC, "/Q", iss], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if p.returncode == 0 and os.path.exists(os.path.join(outdir, sp["base"] + ".exe")):
            ok += 1
            print("[OK]   %-42s %8.1fKB" % (sp["base"], os.path.getsize(os.path.join(outdir, sp["base"] + ".exe")) / 1024))
        else:
            fail += 1
            print("[FAIL] %-42s\n%s\n%s" % (sp["base"], (p.stdout or "")[-800:], (p.stderr or "")[-500:]))
    print("Inno: 成功 %d / 失败 %d\n" % (ok, fail))


# ==================================================================== NSIS
NSIS_TMPL = r"""
Unicode true
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

Name "{appname}"
OutFile "{outfile}"
InstallDir "{installdir}"
RequestExecutionLevel {execlevel}
ShowInstDetails show

!define MUI_ABORTWARNING
!define MUI_LANGDLL_ALLLANGUAGES
{muipages}
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

Function .onInit
{silentcheck}
FunctionEnd

Section "Install"
  SetOutPath "$INSTDIR"
  File "{payload}\app.exe"
  File "{payload}\core.dll"
  File "{payload}\resources.dat"
  File "{payload}\readme.txt"
  {extra_files}
  ; 写卸载项（真实安装器行为）
  WriteRegStr {regroot} "Software\Microsoft\Windows\CurrentVersion\Uninstall\{regname}" "DisplayName" "{appname}"
  WriteRegStr {regroot} "Software\Microsoft\Windows\CurrentVersion\Uninstall\{regname}" "DisplayVersion" "1.0.0"
  WriteRegStr {regroot} "Software\Microsoft\Windows\CurrentVersion\Uninstall\{regname}" "InstallLocation" "$INSTDIR"
  WriteRegStr {regroot} "Software\Microsoft\Windows\CurrentVersion\Uninstall\{regname}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  ; 哨兵
  CreateDirectory "C:\Users\Public\AT-SENTINEL"
  FileOpen $0 "C:\Users\Public\AT-SENTINEL\ran.log" a
  FileSeek $0 0 END
  FileWrite $0 "NSIS-{tag}$\r$\n"
  FileClose $0
  {extra_section}
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\app.exe"
  RMDir /r "$INSTDIR"
  DeleteRegKey {regroot} "Software\Microsoft\Windows\CurrentVersion\Uninstall\{regname}"
SectionEnd
"""


def gen_nsis():
    outdir = os.path.join(S, "18-合成安装器(NSIS)")
    os.makedirs(outdir, exist_ok=True)

    specs = [
        dict(tag="NSIS-01-静默安装成功", appname="AT Synthetic NSIS 01", instdir="$PROGRAMFILES64\\ATSynthNsis01",
             regroot="HKLM", regname="ATSynthNsis01", exec="admin", silentcheck="", extra_section="", muipages=""),
        dict(tag="NSIS-02-仅GUI向导-中文", appname="AT 合成 NSIS 向导 02（中文）",
             instdir="$PROGRAMFILES64\\ATSynthNsis02", regroot="HKLM", regname="ATSynthNsis02",
             exec="admin", silentcheck="  ; 忽略 /S：强制走 GUI 向导（F14/A12 用）\n  SetSilent normal",
             extra_section="", muipages="!define MUI_LANGDLL_DISPLAY\n  !insertmacro MUI_PAGE_WELCOME\n  !insertmacro MUI_PAGE_LICENSE \"%s\"" % os.path.join(PAYLOAD, "license.txt")),
        dict(tag="NSIS-03-仅GUI向导-英文", appname="AT Synthetic NSIS Wizard 03",
             instdir="$PROGRAMFILES64\\ATSynthNsis03", regroot="HKLM", regname="ATSynthNsis03",
             exec="admin", silentcheck="  SetSilent normal", extra_section="", muipages=""),
        dict(tag="NSIS-04-静默无效果-需GUI兜底", appname="AT Synthetic NSIS 04 SilentNoop",
             instdir="$PROGRAMFILES64\\ATSynthNsis04", regroot="HKLM", regname="ATSynthNsis04",
             exec="admin", silentcheck="  ${If} ${Silent}\n    ; 静默模式下什么都不做，直接退出 0（模拟假成功）\n    SetErrorLevel 0\n    Quit\n  ${EndIf}",
             extra_section="", muipages=""),
        dict(tag="NSIS-05-安装后回滚", appname="AT Synthetic NSIS 05 Rollback",
             instdir="$PROGRAMFILES64\\ATSynthNsis05", regroot="HKLM", regname="ATSynthNsis05",
             exec="admin", silentcheck="",
             extra_section="  ; 模拟回滚：装完再把文件删掉，并写失败痕迹\n"
                           "  DetailPrint \"Installation failed, rolling back...\"\n"
                           "  Sleep 4000\n"
                           "  RMDir /r \"$INSTDIR\"\n"
                           "  DeleteRegKey HKLM \"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ATSynthNsis05\"\n"
                           "  SetErrorLevel 1603",
             muipages=""),
        dict(tag="NSIS-06-需重启-3010", appname="AT Synthetic NSIS 06 Reboot",
             instdir="$PROGRAMFILES64\\ATSynthNsis06", regroot="HKLM", regname="ATSynthNsis06",
             exec="admin", silentcheck="", extra_section="  SetErrorLevel 3010", muipages=""),
        dict(tag="NSIS-07-长安装-持续写盘", appname="AT Synthetic NSIS 07 Slow",
             instdir="$PROGRAMFILES64\\ATSynthNsis07", regroot="HKLM", regname="ATSynthNsis07",
             exec="admin", silentcheck="", muipages="",
             extra_section="  StrCpy $1 0\n"
                           "  loop_slow:\n"
                           "    IntOp $1 $1 + 1\n"
                           "    FileOpen $2 \"$INSTDIR\\progress.txt\" w\n"
                           "    FileWrite $2 \"progress $1\"\n"
                           "    FileClose $2\n"
                           "    DetailPrint \"progress $1 / 30\"\n"
                           "    Sleep 3000\n"
                           "    IntCmp $1 30 done_slow loop_slow loop_slow\n"
                           "  done_slow:\n"),
    ]

    ok = fail = 0
    for sp in specs:
        outfile = os.path.join(outdir, sp["tag"] + ".exe")
        body = NSIS_TMPL.format(
            appname=sp["appname"], outfile=outfile, installdir=sp["instdir"],
            execlevel=sp["exec"], payload=PAYLOAD, tag=sp["tag"],
            regroot=sp["regroot"], regname=sp["regname"],
            silentcheck=sp["silentcheck"], extra_section=sp["extra_section"],
            extra_files="", muipages=sp["muipages"])
        nsi = os.path.join(BUILD, sp["tag"] + ".nsi")
        with open(nsi, "w", encoding="utf-8-sig") as f:
            f.write(body)
        p = subprocess.run([MAKENSIS, "/V2", nsi], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if os.path.exists(outfile):
            ok += 1
            print("[OK]   %-42s %8.1fKB" % (sp["tag"], os.path.getsize(outfile) / 1024))
        else:
            fail += 1
            print("[FAIL] %-42s\n%s\n%s" % (sp["tag"], (p.stdout or "")[-900:], (p.stderr or "")[-400:]))
    print("NSIS: 成功 %d / 失败 %d" % (ok, fail))


if __name__ == "__main__":
    ensure_payload()
    if not os.path.exists(ISCC):
        print("缺少 ISCC.exe"); sys.exit(1)
    gen_inno()
    if os.path.exists(MAKENSIS):
        gen_nsis()
    else:
        print("缺少 makensis.exe，跳过 NSIS 样本")
