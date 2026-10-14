; ATS_ROOT: 本仓库根目录。构建时用 ISCC /DATS_ROOT=<绝对路径> 覆盖。
#ifndef ATS_ROOT
  #define ATS_ROOT "C:\ATS"
#endif


[Setup]
AppId={{9A7E1C10-4B2E-4E7A-9C1D-AT1000000000}}
AppName=AT Synthetic Inno 10 NetWait
AppVersion=1.0.0
AppVerName=AT Synthetic Inno 10 NetWait 1.0.0
AppPublisher=AT-TestSuite
DefaultDirName={autopf}\ATSynthInno10
DefaultGroupName=AT Synthetic Inno 10 NetWait
UninstallDisplayName=AT Synthetic Inno 10 NetWait
UninstallDisplayIcon={app}\app.exe
OutputDir={#ATS_ROOT}\samples\17-合成安装器(Inno)
OutputBaseFilename=INNO-10-联网下载组件等待
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
Name: "{group}\AT Synthetic Inno 10 NetWait"; Filename: "{app}\app.exe"
[Run]
Filename: "{#ATS_ROOT}\sources\payload\netwait.exe"; Flags: waituntilterminated


[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if not DirExists('C:\Users\Public\AT-SENTINEL') then CreateDir('C:\Users\Public\AT-SENTINEL');
    SaveStringToFile('C:\Users\Public\AT-SENTINEL\ran.log', 'INNO-10' + #13#10, True);
  end;
end;

