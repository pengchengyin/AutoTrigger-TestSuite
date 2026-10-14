; ATS_ROOT: 本仓库根目录。构建时用 ISCC /DATS_ROOT=<绝对路径> 覆盖。
#ifndef ATS_ROOT
  #define ATS_ROOT "C:\ATS"
#endif


[Setup]
AppId={{9A7E1C05-4B2E-4E7A-9C1D-AT0500000000}}
AppName=AT Synthetic Inno 05 Slow
AppVersion=1.0.0
AppVerName=AT Synthetic Inno 05 Slow 1.0.0
AppPublisher=AT-TestSuite
DefaultDirName={autopf}\ATSynthInno05
DefaultGroupName=AT Synthetic Inno 05 Slow
UninstallDisplayName=AT Synthetic Inno 05 Slow
UninstallDisplayIcon={app}\app.exe
OutputDir={#ATS_ROOT}\samples\17-合成安装器(Inno)
OutputBaseFilename=INNO-05-长安装-持续写盘90s
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
Source: "{#ATS_ROOT}\sources\payload\bigpayload.bin"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AT Synthetic Inno 05 Slow"; Filename: "{app}\app.exe"


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

