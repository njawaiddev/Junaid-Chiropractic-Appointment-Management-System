[Setup]
AppName=Chiropractic Manager
AppVersion=1.0
AppPublisher=Naveed Jawaid
AppPublisherURL=https://github.com/njawaiddev/Junaid-Chiropractic-Appointment-Management-System
AppSupportURL=https://github.com/njawaiddev/Junaid-Chiropractic-Appointment-Management-System
AppUpdatesURL=https://github.com/njawaiddev/Junaid-Chiropractic-Appointment-Management-System
DefaultDirName={autopf}\Chiropractic Manager
DefaultGroupName=Chiropractic Manager
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=ChiropracticManager_Setup
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\ChiropracticManager\ChiropracticManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ChiropracticManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "credentials.json"; DestDir: "{userappdata}\ChiropracticManager"; Flags: ignoreversion; Check: FileExists('credentials.json')

[Dirs]
Name: "{userappdata}\ChiropracticManager"; Permissions: users-full

[Icons]
Name: "{group}\Chiropractic Manager"; Filename: "{app}\ChiropracticManager.exe"
Name: "{group}\{cm:UninstallProgram,Chiropractic Manager}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Chiropractic Manager"; Filename: "{app}\ChiropracticManager.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Chiropractic Manager"; Filename: "{app}\ChiropracticManager.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\ChiropracticManager.exe"; Description: "{cm:LaunchProgram,Chiropractic Manager}"; Flags: nowait postinstall skipifsilent 