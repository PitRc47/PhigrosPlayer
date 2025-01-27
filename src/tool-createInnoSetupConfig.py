import fix_workpath as _

from sys import argv
from os.path import abspath, dirname

if len(argv) < 6:
    print("Usage: tool-createInnoSetupConfig <version> <files-dir> <main-program> <output-exe> <output-issfile>")
    raise SystemExit

issfile = '''\
#define AppName " $$AppName$$ "
#define AppVersion " $$AppVersion$$ "
#define AppPublisher ""
#define AppURL " $$AppURL$$ "
#define AppExeName " $$AppExeName$$ "
#define AppAssocName " $$AppAssocName$$ "
#define AppAssocExt ".pez"
#define AppAssocKey StringChange(AppAssocName, " ", "") + AppAssocExt

[Setup]
AppId={{ $$AppId$$ }
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\\{#AppName}
ChangesAssociations=yes
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile= $$LicenseFile$$#
PrivilegesRequiredOverridesAllowed=dialog
OutputDir= $$OutputDir$$#
OutputBaseFilename= $$OutputBaseFilename$$#
SetupIconFile= $$SetupIconFile$$#
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: " $$AppFilesPath$$ \\ $$AppExeName$$ "; DestDir: "{app}"; Flags: ignoreversion
Source: " $$AppFilesPath$$ \\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
Root: HKA; Subkey: "Software\\Classes\\{#AppAssocExt}\\OpenWithProgids"; ValueType: string; ValueName: "{#AppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\\Classes\\{#AppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#AppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\\Classes\\{#AppAssocKey}\\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\\{#AppExeName},0"
Root: HKA; Subkey: "Software\\Classes\\{#AppAssocKey}\\shell\\open\\command"; ValueType: string; ValueName: ""; ValueData: """{app}\\{#AppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\\Classes\\Applications\\{#AppExeName}\\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""

[Icons]
Name: "{group}\\{#AppName}"; Filename: "{app}\\{#AppExeName}"
Name: "{group}\\{cm:ProgramOnTheWeb,{#AppName}}"; Filename: "{#AppURL}"
Name: "{group}\\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\{#AppName}"; Filename: "{app}\\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
'''

replacedict = {
    "AppId": "08986CF5-55F0-453B-B703-58A5D821C049",
    "AppName": "PhigrosPlayer",
    "AppVersion": argv[1],
    "AppURL": "https://github.com/qaqFei/PhigrosPlayer",
    "AppExeName": argv[3],
    "AppAssocName": "Phigros Re:PhiEdit 谱面文件",
    "LicenseFile": abspath("../LICENSE"),
    "OutputDir": dirname(abspath(argv[4])),
    "OutputBaseFilename": argv[4].split("/")[-1].split("\\")[-1],
    "SetupIconFile": abspath("./icon.ico"),
    "AppFilesPath": argv[2]
}

for k, v in replacedict.items():
    issfile = issfile.replace(f" $${k}$$ ", v)
    issfile = issfile.replace(f" $${k}$$#", v)

with open(argv[5], "w", encoding="utf-8") as f:
    f.write(issfile)