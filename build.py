import PyInstaller.__main__
import sys
import os

def build_exe():
    """Build the executable using PyInstaller"""
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set the paths
    main_script = os.path.join(script_dir, "src", "main.py")
    icon_path = os.path.join(script_dir, "assets", "icon.ico")
    
    # Create the assets directory if it doesn't exist
    os.makedirs(os.path.join(script_dir, "assets"), exist_ok=True)
    
    # PyInstaller arguments
    args = [
        main_script,
        "--name=ChiropracticManager",
        "--onefile",
        "--windowed",
        "--clean",
        f"--distpath={os.path.join(script_dir, 'dist')}",
        f"--workpath={os.path.join(script_dir, 'build')}",
        f"--specpath={os.path.join(script_dir, 'build')}"
    ]
    
    # Add icon if available
    if os.path.exists(icon_path):
        args.append(f"--icon={icon_path}")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build_exe() 