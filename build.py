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
    
    # Ensure logo exists and create icons
    logo_path = os.path.join("src", "assets", "logo.png")
    icon_path = os.path.join(assets_dir, "icon.ico")
    icns_path = os.path.join(assets_dir, "icon.icns")
    
    if os.path.exists(logo_path):
        try:
            from PIL import Image
            img = Image.open(logo_path)
            
            # Create .ico for Windows
            icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
            img.save(icon_path, format='ICO', sizes=icon_sizes)
            print(f"Created icon file at: {icon_path}")
            
            # Create .icns for macOS
            if sys.platform == "darwin":
                # Create iconset directory
                iconset_path = os.path.join(assets_dir, "icon.iconset")
                os.makedirs(iconset_path, exist_ok=True)
                
                # Generate different sizes for macOS
                sizes = [(16,16), (32,32), (64,64), (128,128), (256,256), (512,512), (1024,1024)]
                for size in sizes:
                    resized = img.resize(size, Image.Resampling.LANCZOS)
                    resized.save(os.path.join(iconset_path, f"icon_{size[0]}x{size[0]}.png"))
                    if size[0] <= 512:  # Also create @2x versions up to 512px
                        resized_2x = img.resize((size[0]*2, size[0]*2), Image.Resampling.LANCZOS)
                        resized_2x.save(os.path.join(iconset_path, f"icon_{size[0]}x{size[0]}@2x.png"))
                
                # Convert iconset to icns using iconutil
                os.system(f"iconutil -c icns {iconset_path}")
                print(f"Created icns file at: {icns_path}")
                
                # Clean up iconset directory
                shutil.rmtree(iconset_path)
                
        except Exception as e:
            print(f"Error creating icons: {str(e)}")

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
    
    # Add credentials.json if it exists
    credentials_file = os.path.join(script_dir, "credentials.json")
    if os.path.exists(credentials_file):
        # Copy credentials to app data directory during installation
        app_data_dir = "AppData" if sys.platform == "win32" else ".chiropracticmanager"
        data_files.append((credentials_file, app_data_dir))
    
    # Add Info.plist for macOS
    if sys.platform == "darwin":
        info_plist = os.path.join(script_dir, "Info.plist")
        if os.path.exists(info_plist):
            data_files.append((info_plist, '.'))
    
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
    
    # Base PyInstaller arguments
    args = [
        main_script,
        "--name=ChiropracticManager",
        "--windowed",
        "--onedir",
        "--clean",
        "--noconfirm",
        f"--distpath={dist_path}",
        f"--workpath={build_path}",
        f"--specpath={build_path}",
        f"--icon={icon_path}",
        # Windows-specific imports
        "--hidden-import=win32api",
        "--hidden-import=win32con",
        "--hidden-import=win32gui",
        # Hidden imports for Google OAuth
        "--hidden-import=google_auth_oauthlib.flow",
        "--hidden-import=google.auth.transport.requests",
        "--hidden-import=google.oauth2.credentials",
        "--hidden-import=google_auth_oauthlib",
        "--hidden-import=google.auth",
        "--hidden-import=google.oauth2",
        "--hidden-import=google_auth_httplib2",
        "--hidden-import=googleapiclient",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=babel.numbers",
        "--hidden-import=requests_oauthlib",
        "--hidden-import=oauthlib",
        "--hidden-import=oauthlib.oauth2",
        "--hidden-import=google_auth_oauthlib.session",
        "--hidden-import=google_auth_oauthlib.helpers",
        "--hidden-import=google_auth_oauthlib.interactive",
        # Collect all required modules
        "--collect-all=google_auth_oauthlib",
        "--collect-all=google_auth_httplib2",
        "--collect-all=googleapiclient",
        "--collect-all=google.auth",
        "--collect-all=google.oauth2",
        "--collect-all=oauthlib",
        "--collect-all=requests_oauthlib",
        # Add data files
        f"--add-data={os.path.join(script_dir, 'src')};src",
        f"--add-data={os.path.join(script_dir, 'assets')};assets"
    ]
    
    # Add credentials.json if it exists
    credentials_file = os.path.join(script_dir, "credentials.json")
    if os.path.exists(credentials_file):
        args.append(f"--add-data={credentials_file};.")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\nBuild completed successfully!")
    print(f"Executable can be found in: {dist_path}")
    
    # Create Inno Setup script
    create_inno_setup_script()
    print("\nNext steps:")
    print("1. Install Inno Setup from: https://jrsoftware.org/isdl.php")
    print("2. Compile installer.iss with Inno Setup to create the installer")
    print("3. The installer will be created in the 'installer' directory")

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
Source: "dist\\ChiropracticManager\\ChiropracticManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\ChiropracticManager\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
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