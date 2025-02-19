import PyInstaller.__main__
import sys
import os
import shutil
from pathlib import Path
import uuid

DEVELOPER_NAME = "Naveed Jawaid"

def create_assets():
    """Create necessary asset directories and files"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    
    # Create assets directory if it doesn't exist
    os.makedirs(assets_dir, exist_ok=True)
    
    # Ensure logo exists
    logo_path = os.path.join("src", "assets", "logo.png")
    icon_path = os.path.join(assets_dir, "icon.ico")
    
    if not os.path.exists(icon_path) and os.path.exists(logo_path):
        from PIL import Image
        img = Image.open(logo_path)
        img.save(icon_path, format='ICO')

def collect_data_files():
    """Collect all necessary data files"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_files = []
    
    # Add assets directory
    assets_dir = os.path.join(script_dir, "assets")
    if os.path.exists(assets_dir):
        data_files.append((assets_dir, 'assets'))
    
    # Add source directory
    src_dir = os.path.join(script_dir, "src")
    if os.path.exists(src_dir):
        data_files.append((src_dir, 'src'))
    
    return data_files

def build_exe():
    """Build the executable using PyInstaller"""
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure assets exist
    create_assets()
    
    # Set the paths
    main_script = os.path.join(script_dir, "src", "main.py")
    icon_path = os.path.join(script_dir, "assets", "icon.ico")
    dist_path = os.path.join(script_dir, "dist")
    build_path = os.path.join(script_dir, "build")
    
    # Clean previous builds
    for path in [dist_path, build_path]:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    # Collect data files
    data_files = collect_data_files()
    
    # Base PyInstaller arguments
    args = [
        main_script,
        "--name=ChiropracticManager",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--distpath={dist_path}",
        f"--workpath={build_path}",
        f"--specpath={build_path}",
    ]
    
    # Add icon if available
    if os.path.exists(icon_path):
        args.append(f"--icon={icon_path}")
    
    # Add data files
    for src, dst in data_files:
        # Use absolute paths for data files
        args.append(f"--add-data={src}:{dst}")
    
    # Add hidden imports
    hidden_imports = [
        "PIL",
        "PIL._tkinter_finder",
        "tkcalendar",
        "babel.numbers",
        "customtkinter",
    ]
    for imp in hidden_imports:
        args.append(f"--hidden-import={imp}")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\nBuild completed successfully!")
    print(f"Executable can be found in: {dist_path}")

def create_inno_setup_script():
    """Create Inno Setup script for Windows installer"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    inno_script = os.path.join(script_dir, "installer.iss")
    
    script_content = """
[Setup]
AppName=Chiropractic Manager
AppVersion=1.0
AppPublisher=Naveed Jawaid
AppPublisherURL=https://github.com/njawaiddev/Junaid-Chiropractic-Appointment-Management-System
AppSupportURL=https://github.com/njawaiddev/Junaid-Chiropractic-Appointment-Management-System
AppUpdatesURL=https://github.com/njawaiddev/Junaid-Chiropractic-Appointment-Management-System
DefaultDirName={autopf}\\Chiropractic Manager
DefaultGroupName=Chiropractic Manager
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=ChiropracticManager_Setup
SetupIconFile=assets\\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\\ChiropracticManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\\*"; DestDir: "{app}\\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\Chiropractic Manager"; Filename: "{app}\\ChiropracticManager.exe"
Name: "{group}\\{cm:UninstallProgram,Chiropractic Manager}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\Chiropractic Manager"; Filename: "{app}\\ChiropracticManager.exe"; Tasks: desktopicon
Name: "{userappdata}\\Microsoft\\Internet Explorer\\Quick Launch\\Chiropractic Manager"; Filename: "{app}\\ChiropracticManager.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\\ChiropracticManager.exe"; Description: "{cm:LaunchProgram,Chiropractic Manager}"; Flags: nowait postinstall skipifsilent
"""
    
    with open(inno_script, "w") as f:
        f.write(script_content)
    
    print(f"Inno Setup script created at: {inno_script}")

if __name__ == "__main__":
    # Build executable
    build_exe()
    
    # Create Inno Setup script
    create_inno_setup_script()
    
    print("\nNext steps:")
    print("1. Install Inno Setup from: https://jrsoftware.org/isdl.php")
    print("2. Compile installer.iss with Inno Setup to create the installer")
    print("3. The installer will be created in the 'installer' directory") 