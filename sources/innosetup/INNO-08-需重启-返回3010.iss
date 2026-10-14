; ATS_ROOT: 本仓库根目录。构建时用 ISCC /DATS_ROOT=<绝对路径> 覆盖。
#ifndef ATS_ROOT
  #define ATS_ROOT "C:\ATS"
#endif


[Setup]
AppId={{9A7E1C08-4B2E-4E7A-9C1D-AT0800000000}}
AppName=AT Synthetic Inno 08 Reboot
AppVersion=1.0.0
AppVerName=AT Synthetic Inno 08 Reboot 1.0.0
AppPublisher=AT-TestSuite
DefaultDirName={autopf}\ATSynthInno08
DefaultGroupName=AT Synthetic Inno 08 Reboot
UninstallDisplayName=AT Synthetic Inno 08 Reboot
UninstallDisplayIcon={app}\app.exe
OutputDir={#ATS_ROOT}\samples\17-合成安装器(Inno)
OutputBaseFilename=INNO-08-需重启-返回3010
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
Name: "{group}\AT Synthetic Inno 08 Reboot"; Filename: "{app}\app.exe"


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

