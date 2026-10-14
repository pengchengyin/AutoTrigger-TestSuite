; ATS_ROOT: 本仓库根目录。构建时用 ISCC /DATS_ROOT=<绝对路径> 覆盖。
#ifndef ATS_ROOT
  #define ATS_ROOT "C:\ATS"
#endif


[Setup]
AppId={{9A7E1C06-4B2E-4E7A-9C1D-AT0600000000}}
AppName=AT Synthetic Inno 06 FakeOK
AppVersion=1.0.0
AppVerName=AT Synthetic Inno 06 FakeOK 1.0.0
AppPublisher=AT-TestSuite
DefaultDirName={tmp}\ATSynthInno06
DefaultGroupName=AT Synthetic Inno 06 FakeOK
UninstallDisplayName=AT Synthetic Inno 06 FakeOK
UninstallDisplayIcon={app}\app.exe
OutputDir={#ATS_ROOT}\samples\17-合成安装器(Inno)
OutputBaseFilename=INNO-06-假成功-只解压无卸载项
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
SetupLogging=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Uninstallable=no
CreateUninstallRegKey=no
DisableDirPage=yes
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
[Files]
Source: "{#ATS_ROOT}\sources\payload\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ATS_ROOT}\sources\payload\core.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ATS_ROOT}\sources\payload\resources.dat"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ATS_ROOT}\sources\payload\readme.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AT Synthetic Inno 06 FakeOK"; Filename: "{app}\app.exe"


