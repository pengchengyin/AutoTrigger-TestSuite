; ATS_ROOT: 本仓库根目录。构建时用 ISCC /DATS_ROOT=<绝对路径> 覆盖。
#ifndef ATS_ROOT
  #define ATS_ROOT "C:\ATS"
#endif


[Setup]
AppId={{9A7E1C07-4B2E-4E7A-9C1D-AT0700000000}}
AppName=AT Synthetic Inno 07 Fail
AppVersion=1.0.0
AppVerName=AT Synthetic Inno 07 Fail 1.0.0
AppPublisher=AT-TestSuite
DefaultDirName={autopf}\ATSynthInno07
DefaultGroupName=AT Synthetic Inno 07 Fail
UninstallDisplayName=AT Synthetic Inno 07 Fail
UninstallDisplayIcon={app}\app.exe
OutputDir={#ATS_ROOT}\samples\17-合成安装器(Inno)
OutputBaseFilename=INNO-07-安装后失败框-退出码1
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
SetupLogging=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
[Files]
Source: "{#ATS_ROOT}\sources\payload\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ATS_ROOT}\sources\payload\core.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ATS_ROOT}\sources\payload\resources.dat"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ATS_ROOT}\sources\payload\readme.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AT Synthetic Inno 07 Fail"; Filename: "{app}\app.exe"


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

