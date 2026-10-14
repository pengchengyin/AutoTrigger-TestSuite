; ATS_ROOT: 本仓库根目录。构建时用 ISCC /DATS_ROOT=<绝对路径> 覆盖。
#ifndef ATS_ROOT
  #define ATS_ROOT "C:\ATS"
#endif


[Setup]
AppId={{9A7E1C02-4B2E-4E7A-9C1D-AT0200000000}}
AppName=AT 合成安装向导 02（中文）
AppVersion=1.0.0
AppVerName=AT 合成安装向导 02（中文） 1.0.0
AppPublisher=AT-TestSuite
DefaultDirName={autopf}\ATSynthInno02
DefaultGroupName=AT 合成安装向导 02（中文）
UninstallDisplayName=AT 合成安装向导 02（中文）
UninstallDisplayIcon={app}\app.exe
OutputDir={#ATS_ROOT}\samples\17-合成安装器(Inno)
OutputBaseFilename=INNO-02-仅GUI向导-中文
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
SetupLogging=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Uninstallable=no
CreateUninstallRegKey=no
LicenseFile={#ATS_ROOT}\sources\payload\license.txt
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
[Files]
Source: "{#ATS_ROOT}\sources\payload\app.exe"; DestDir: "{app}"; Flags: ignoreversion; Check: NotSilent
Source: "{#ATS_ROOT}\sources\payload\core.dll"; DestDir: "{app}"; Flags: ignoreversion; Check: NotSilent
Source: "{#ATS_ROOT}\sources\payload\resources.dat"; DestDir: "{app}"; Flags: ignoreversion; Check: NotSilent
Source: "{#ATS_ROOT}\sources\payload\readme.txt"; DestDir: "{app}"; Flags: ignoreversion; Check: NotSilent

[Icons]
Name: "{group}\AT 合成安装向导 02（中文）"; Filename: "{app}\app.exe"


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
      loc := ExpandConstant('{app}');
      if not DirExists('C:\Users\Public\AT-SENTINEL') then CreateDir('C:\Users\Public\AT-SENTINEL');
      SaveStringToFile('C:\Users\Public\AT-SENTINEL\ran.log', 'INNO-02-GUI' + #13#10, True);
      RegWriteStringValue(HKCU,
        'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthInno02',
        'DisplayName', 'AT Synth Inno 02 GUI ZH');
      RegWriteStringValue(HKCU,
        'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthInno02',
        'DisplayVersion', '1.0.0');
      RegWriteStringValue(HKCU,
        'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATSynthInno02',
        'InstallLocation', loc);
    end;
  end;
end;

